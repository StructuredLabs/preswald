# 🏛️ Monument Intelligence Dashboard

An interactive, AI-powered dashboard built with [Preswald](https://github.com/StructuredLabs/preswald) that explores iconic monuments across the world.  
Analyze historical sites by region, visitors, time period, and more—all through stunning visualizations and natural language chat.

---

## 🌍 Features

- 📍 Geospatial map of monuments with scalable marker sizes based on yearly visitors  
- 📊 Interactive filters for time period and visitor counts  
- 📈 Graphs for trends by country and build century  
- 🧠 Built-in chatbot for natural language queries  
- 🎨 Sidebar branding, responsive layout, and clean UI

---

## 🗂 Dataset

The app uses a curated GeoJSON dataset with 45+ monuments including attributes like:

- Name & Location  
- Year Built  
- Estimated Visitors per Year  
- Latitude/Longitude coordinates  

File: `data/monuments_geo.geojson`

---

## 🚀 Run Locally

Make sure you have Python ≥3.8 and Preswald installed.

```bash
pip install preswald
```

Then run the app.

```bash
preswald run
```

## 📁 Folder Structure

monument-dashboard/
├── hello.py
├── preswald.toml
├── pyproject.toml
├── README.md
├── .gitignore
├── data/
│   └── monuments_geo.geojson
├── images/
│   ├── logo.png
│   └── favicon.ico
└── dist/         # (created after export)

## 💡 Credits

Built using [Preswald](https://github.com/StructuredLabs/preswald)
Inspired by global cultural heritage and open data initiatives 🌐