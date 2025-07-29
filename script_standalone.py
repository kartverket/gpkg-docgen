import geopandas as gpd
import pandas as pd
import json
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import fiona
import shutil
import warnings

# Suppress specific warning related to unary_union usage
warnings.filterwarnings("ignore", message=".*unary_union*")

"""
GeoPackage to HTML Product Sheet Generator
------------------------------------------

This script reads one or more GeoPackage (.gpkg) files from the current directory
along with a corresponding Excel file containing metadata. It generates a
standalone, offline HTML product sheet for each dataset using a Jinja2 template.

Main features:
- Extracts general and dataset-specific metadata
- Lists all layers and associated fields (including datatype and sample values)
- Detects and displays domain/code lists (either from `code_*` tables or inferred values)
- Generates interactive Leaflet maps with simplified geometry previews
- Fully self-contained HTML product sheets (can be opened without internet)

Author: Henrik G. Schüller
"""

# Locate GeoPackage and Excel files
gpkg_files = [f for f in os.listdir('.') if f.lower().endswith('.gpkg')]
xlsx_files = [f for f in os.listdir('.') if f.lower().endswith('.xlsx')]
if not gpkg_files or not xlsx_files:
    raise FileNotFoundError("Missing both .gpkg and .xlsx files in the directory.")

# Use first Excel file found
metadata_excel_path = xlsx_files[0]
metadata_sheet = "metadata"
metadata_key_col = "dataset"

# Load metadata from Excel
try:
    metadata_df = pd.read_excel(metadata_excel_path, sheet_name=metadata_sheet)
except Exception as e:
    raise RuntimeError("Could not read metadata sheet: " + str(e))

# Load HTML template
env = Environment(loader=FileSystemLoader("."))
with open("template_standalone.html", "r", encoding="utf-8") as f:
    template = env.from_string(f.read())

# Load world basemap (used for context in Leaflet)
world_gdf = gpd.read_file("assets/countries.geojson").to_crs(epsg=4326)
world_gdf["geometry"] = world_gdf["geometry"].simplify(tolerance=0.01, preserve_topology=True)
world_data_json = json.dumps(json.loads(world_gdf.to_json()))

# Parameters for sampling and geometry simplification
max_total_features = 2500
simplify_tolerance = 0.0010

# Ensure filename is safe for output
def safe_filename(s):
    return "".join(c if c.isalnum() or c in " -_()" else "_" for c in s).strip()

# Process each GeoPackage file
for gpkg_path in gpkg_files:
    dataset_name = os.path.splitext(os.path.basename(gpkg_path))[0]

    # Initialize metadata structure
    metadata_grouped = {
        "General Metadata": {},
        "Dataset Metadata": {
            "File name": os.path.basename(gpkg_path),
            "Generated": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }

    # Match Excel metadata by dataset name
    try:
        match_row = metadata_df[metadata_df[metadata_key_col] == dataset_name].iloc[0]
        metadata_grouped["General Metadata"] = {
            k: str(v) for k, v in match_row.dropna().items() if k != metadata_key_col
        }
    except:
        print(f"⚠️ No metadata found for {dataset_name}, skipping.")
        continue

    layer_info = []
    geojson_layers = []
    layers = fiona.listlayers(gpkg_path)

    # Extract code lists from layers starting with "code_"
    code_lookup = {}
    for l in layers:
        if l.startswith("code_"):
            parts = l.split("_", 2)
            if len(parts) == 3:
                _, base_layer, field = parts
                gdf_code = gpd.read_file(gpkg_path, layer=l)
                if not gdf_code.empty:
                    values = sorted(gdf_code[gdf_code.columns[0]].dropna().astype(str).unique().tolist())
                    code_lookup.setdefault(base_layer.lower(), {})[field] = values

    num_layers = len(layers)
    features_per_layer = max(max_total_features // num_layers, 1) if num_layers else 0

    for layer_name in layers:
        try:
            gdf = gpd.read_file(gpkg_path, layer=layer_name)
            if not gdf.empty:
                gdf = gdf.to_crs(epsg=4326)
                gdf_clean = gdf.copy()

                # Convert all non-geometry fields to string for HTML rendering
                for col in gdf_clean.columns:
                    if col != "geometry":
                        gdf_clean[col] = gdf_clean[col].astype(str)

                # Read schema from Fiona to preserve field types
                with fiona.open(gpkg_path, layer=layer_name) as src:
                    schema_props = src.schema["properties"]
                    fields = []
                    for field_name, gpkg_type in schema_props.items():
                        sample = ""
                        if field_name in gdf.columns:
                            non_null = gdf[field_name].dropna()
                            if not non_null.empty:
                                sample = str(non_null.iloc[0])

                        field_dict = {
                            "name": field_name,
                            "dtype": gpkg_type,
                            "sample": sample,
                        }

                        # Check for predefined or inferred code list
                        allowed_values = code_lookup.get(layer_name.lower(), {}).get(field_name)
                        if not allowed_values and "str" in gpkg_type.lower() and field_name in gdf.columns:
                            unique_vals = gdf[field_name].dropna().astype(str).unique()
                            short_enough = [v for v in unique_vals if len(v) <= 60]
                            if 1 < len(short_enough) <= 16 and len(short_enough) == len(unique_vals):
                                allowed_values = sorted(short_enough)

                        if allowed_values:
                            field_dict["allowedValues"] = allowed_values

                        fields.append(field_dict)

                note = ""
                if len(gdf) > features_per_layer:
                    note = f"Only showing {features_per_layer} features in map, centered near dataset centroid."

                # Summary information for HTML table
                layer_info.append({
                    "name": layer_name,
                    "feature_count": len(gdf),
                    "geometry_type": gdf.geom_type.unique().tolist(),
                    "fields": fields,
                    "note": note
                })

                # Sample geometries closest to centroid for map
                gdf_proj = gdf_clean.to_crs(epsg=3857)
                center = gdf_proj.unary_union.centroid
                gdf_clean['__distance'] = gdf_proj.geometry.centroid.distance(center)
                sample_gdf = gdf_clean.nsmallest(features_per_layer, '__distance').drop(columns='__distance')

                sample_gdf["geometry"] = sample_gdf["geometry"].simplify(tolerance=simplify_tolerance, preserve_topology=True)

                geojson_layers.append({
                    "name": layer_name,
                    "data": json.loads(sample_gdf.to_json()),
                    "field_order": [f["name"] for f in fields],
                    "fields": fields
                })

                print(f"✅ Processed layer: {layer_name} ({len(gdf)} features, showing {min(len(gdf), features_per_layer)})")
        except Exception as e:
            print(f"⚠️ Could not read layer '{layer_name}': {e}")

    metadata_grouped["Dataset Metadata"]["Number of layers"] = str(len(layer_info))

    title_base = metadata_grouped["General Metadata"].get("title", dataset_name)
    title = f"{title_base} (NOR) - Product Sheet"

    # Render HTML output
    html_output = template.render(
        filename=os.path.basename(gpkg_path),
        title=title,
        layers=layer_info,
        geojson_layers=geojson_layers,
        metadata=metadata_grouped,
        world_data=world_data_json
    )

    # Save to file with safe title
    safe_title = safe_filename(title)
    output_path = f"{safe_title}.html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"📄 Product sheet saved as: {output_path}")
