# 🗺 GeoJSON Comparison Visualizer - Streamlit Edition

MongoDB-powered geospatial visualization tool for comparing multiple historical empire datasets side-by-side with independent timeline controls.

## Features

✨ **3 Independent Datasets** - Compare INDIAN_final, Geojson_FolderB_named, and Ranjita_and_Ajay simultaneously

🎛 **Independent Timelines** - Each dataset has its own year slider (not linked)

🗺 **Live Map Rendering** - Folium maps update instantly as you change years

🎨 **Color Coded** - Each empire gets a unique color for visual identification

⚡ **MongoDB Backed** - Fast indexed queries, not filesystem scanning

📊 **Live Metrics** - Shows active empires count for each year and dataset

## Setup & Deployment

### Option A: Local Testing

1. **Clone/Copy to your machine:**
```bash
cd streamlit_visualizer
pip install -r requirements.txt
```

2. **Run locally:**
```bash
streamlit run app_comparison.py
```

3. **View at:** http://localhost:8501

### Option B: Deploy to Streamlit Cloud (FREE)

1. **Push to GitHub:**
```bash
git add .
git commit -m "Add Streamlit comparison visualizer"
git push
```

2. **Create Streamlit Cloud app:**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your repo and `streamlit_visualizer/app_comparison.py`
   - Deploy! (takes ~1 min)

3. **Your app is now live:** https://share.streamlit.io/YOUR-USER/YOUR-REPO/main/streamlit_visualizer/app_comparison.py

### Option C: Deploy to Heroku / Railway / Others

Any Docker-compatible host works. Streamlit requires PyPI packages and network access to MongoDB.

## How It Works

### Architecture

```
Streamlit (Web UI)
    ↓
Cached MongoDB Connection (@st.cache_resource)
    ↓
Query with filepath filter (INDIAN_final, Geojson_FolderB_named, etc.)
    ↓
Parse filenames → Extract year ranges
    ↓
Build independent timelines for each dataset
    ↓
User moves slider → Query active features for that year
    ↓
Render with Folium → Display in map
```

### Data Flow

1. **Initialization**: App connects to MongoDB and loads all datasets once
2. **Timeline Building**: Extracts all unique year breakpoints for each dataset
3. **Interactive Selection**: User moves slider for dataset A, B, or C
4. **Query & Render**: Filters features active in selected year, generates map
5. **Display**: Maps shown side-by-side (3 columns)

## Configuration

Edit `app_comparison.py` to customize:

```python
# Dataset filters (how to query MongoDB)
FILTER_A = 'INDIAN_final'
FILTER_B = 'Geojson_FolderB_named'
FILTER_C = 'Ranjita_and_Ajay'

# Dataset labels (shown in UI)
LABEL_A = 'Dataset A (INDIAN_final)'
LABEL_B = 'Dataset B (Geojson_FolderB_named)'
LABEL_C = 'Dataset C (Ranjita_and_Ajay)'

# Color palettes (empire colors)
PALETTE_A = ['#ff4500', '#ff6347', ...]  # Reds for A
PALETTE_B = ['#1e90ff', '#4169e1', ...]  # Blues for B
PALETTE_C = ['#2ecc71', '#27ae60', ...]  # Greens for C
```

## File Structure

```
streamlit_visualizer/
├── app_comparison.py          # Main Streamlit app
├── mongodb_utils.py           # MongoDB connection helper
├── requirements.txt           # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit cloud config
└── README.md                 # This file
```

## Troubleshooting

### "Cannot connect to MongoDB"
- ✅ Check that MongoDB server is accessible (172.235.1.240:27017)
- ✅ Verify credentials in `mongodb_utils.py`
- ✅ Run `python -c "from mongodb_utils import MongoDBClient; client = MongoDBClient(); print(client.connect())"`

### "No data for Dataset A"
- ✅ Make sure `upload_to_mongodb.py` has been run (all files uploaded)
- ✅ Check that filter string matches filepath in MongoDB: `db.geojson_features.findOne({_filepath: {$regex: 'INDIAN_final'}})`

### Maps not loading / Slow rendering
- ✅ If 100+ empires active in one year, rendering will be slower
- ✅ Consider filtering to specific regions or years
- ✅ Maps cache locally after first load

### Streamlit Cloud deployment fails
- ✅ Make sure `requirements.txt` is in root of `streamlit_visualizer/`
- ✅ Check that `app_comparison.py` is the entry point (path: `streamlit_visualizer/app_comparison.py`)
- ✅ Verify MongoDB is accessible from Streamlit Cloud (it is on 172.235.1.240)

## Performance Notes

- **First load**: ~5-10 seconds (queries and builds timelines)
- **Slider movement**: ~1-3 seconds (depends on number of active empires)
- **Map rendering**: Folium caches locally, browser rendering is fast
- **Memory**: ~200-500MB for full dataset (depending on number of empires)

## License

This tool is part of the MAPX Historical Visualization project.

## Questions?

See `MONGODB_GUIDE.md` for detailed MongoDB setup information.
