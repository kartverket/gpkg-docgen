````markdown
# geopkg-docgen

📦 **Self-documenting HTML generator for GeoPackages**

`geopkg-docgen` is a lightweight Python tool that reads one or more [GeoPackage (.gpkg)](https://www.geopackage.org/)
files along with metadata from an Excel file, and generates fully self-contained HTML product sheets.

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

## 🌐 Optional: Make It Online

This tool is designed to produce **fully self-contained, offline HTML files** — including the basemap (`countries.geojson`) and all Leaflet assets (`leaflet.js`, `leaflet.css`, marker icons, etc.). However, you can easily modify the setup to reduce file size and load maps dynamically using online sources.

### 🔁 Use an online basemap

To switch from the offline `countries.geojson` to a live background map like OpenStreetMap, update the map initialization block in `template_standalone.html`:

```javascript
// Replace this:
// L.geoJSON(world_data).addTo(map);

// With this:
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);
```

You can also combine both (e.g., keeping `countries.geojson` as an overlay, and OSM underneath as a base layer).

---

### 📡 Load Leaflet from CDN

Instead of bundling Leaflet JS/CSS in each HTML file, you can modify the template to load these from the official CDN:

In `template_standalone.html`, replace the local asset links:

```html
<!-- Instead of this -->
<link rel="stylesheet" href="assets/leaflet.css" />
<script src="assets/leaflet.js"></script>
```

Use this:

```html
<!-- Load Leaflet from CDN -->
<link
  rel="stylesheet"
  href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
  integrity="sha512-sA+eP4EqXKjRWr8K4kS2YZ5YzP3X27xem7R7Hl+JmriA04V9X7r3VYQqx2xAoR0FqIknsWIX3wD+J7XjG0zHEQ=="
  crossorigin=""
/>
<script
  src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
  integrity="sha512-nMMMyM1JK1H9zY9Pa1GRqQHXzYkk+ZcgzODIYxWx0m3YUNb3ZQ1Aq2hrk6o0uJbdN6tYP6llloAI8aT/HdlxNQ=="
  crossorigin=""
></script>
```

> 💡 **Why use CDN?**
>
> * Lighter HTML output
> * Faster initial load (especially over internet)
> * Always latest stable Leaflet version (unless you pin it)

---
## 📄 License

MIT License. See `LICENSE` file for details.

---

## 👤 Author

Henrik G. Schüller
[github.com/henrik716](https://github.com/henrik716)


