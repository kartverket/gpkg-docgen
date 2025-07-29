````markdown
# geopkg-docgen

📦 **Self-documenting HTML generator for GeoPackages**

`geopkg-docgen` is a lightweight Python tool that reads one or more [GeoPackage (.gpkg)](https://www.geopackage.org/) files along with metadata from an Excel file, and generates fully self-contained HTML product sheets.

Each HTML report includes:
- General and dataset-specific metadata (from Excel)
- Layer and field overview (with types and sample values)
- Auto-detected domain/code lists
- Interactive Leaflet maps with simplified geometries
- Fully offline – no internet required

---

## 🔧 Features

- 🧠 Self-documenting: no UML or model schema required
- 📊 Field-level inspection with code list detection
- 🗺️ Embedded Leaflet map preview for each layer
- 📁 Reads metadata from `metadata.xlsx`
- 📄 Produces standalone HTML sheets (1 per dataset)

---

## 📁 Project Structure

```plaintext
.
├── script_standalone.py          # Main script to generate HTML sheets
├── template_standalone.html      # Jinja2 HTML template
├── metadata.xlsx                 # Excel metadata (sheet = 'metadata')
├── *.gpkg                        # One or more GeoPackage files
└── assets/                       # Supporting files for HTML output
    ├── countries.geojson         # Simplified basemap for Leaflet
    ├── leaflet.css               # Leaflet stylesheet
    ├── leaflet.js                # Leaflet JS library
    ├── marker-icon.png           # Default map marker icon
    ├── marker-shadow.png         # Marker shadow
    └── ugradert.png              # Optional custom marker icon
````

---

## 📦 Dependencies

Install required Python libraries:

```bash
pip install geopandas pandas jinja2 fiona openpyxl
```

---

## ▶️ How to Use

1. **Place files in the project folder**:

   * One or more `.gpkg` files
   * A `metadata.xlsx` file with a `metadata` sheet
   * An `/assets` folder with required Leaflet files

2. **Run the script**:

```bash
python script_standalone.py
```

3. **Output**:

   * For each `.gpkg`, an HTML file is created (e.g. `My_Dataset_(NOR)_-_Product_Sheet.html`)
   * Open in any browser – fully functional offline

---

## 📘 Metadata Format

Your `metadata.xlsx` should include:

* A sheet named `metadata`
* A column called `dataset` matching each `.gpkg` filename (without extension)
* Any number of additional columns (e.g. `title`, `abstract`, `author`)

Example:

| dataset     | title               | abstract                   |
| ----------- | ------------------- | -------------------------- |
| my\_dataset | My Dataset          | Description of the dataset |
| buildings   | Building Footprints | Building data for region X |

---

## 📌 Notes

* Layers with names starting with `code_` (e.g. `code_buildings_type`) are treated as code lists and linked to the relevant fields.
* If no code table is found, short string fields with few unique values are auto-detected as potential domain lists.
* Geometry is simplified for preview purposes only – original data is untouched.

---

## 📄 License

MIT License. See `LICENSE` file for details.

---

## 👤 Author

Henrik G. Schüller
[github.com/henrik716](https://github.com/henrik716)

```

---

