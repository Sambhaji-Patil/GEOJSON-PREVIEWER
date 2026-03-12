#!/usr/bin/env python3
"""
Streamlit Comparison Visualizer for MongoDB GeoJSON Data
Clean, minimal interface with proper map rendering
"""

import streamlit as st
import re
import folium
from streamlit_folium import st_folium
from mongodb_utils import MongoDBClient
from typing import List, Dict, Optional

# ── Configuration ──────────────────────────────────────────────────────────────
COLLECTION_A = 'geojson_features'
COLLECTION_B = 'geojson_features'
COLLECTION_C = 'geojson_features'

LABEL_A = 'INDIAN_final'
LABEL_B = 'Geojson_FolderB_named'
LABEL_C = 'Ranjita_and_Ajay'

FILTER_A = 'INDIAN_final'
FILTER_B = 'Geojson_FolderB_named'
FILTER_C = 'Ranjita_and_Ajay'

INDIA_CENTRE = [22.5, 82.5]

PALETTE_A = ['#e63946', '#c1121f', '#f4a261', '#e76f51', '#d62828',
             '#ff6b6b', '#c0392b', '#a93226', '#e74c3c', '#922b21']
PALETTE_B = ['#457b9d', '#1d3557', '#2196f3', '#0077b6', '#023e8a',
             '#2980b9', '#1565c0', '#0d47a1', '#1976d2', '#1a5276']
PALETTE_C = ['#2d6a4f', '#40916c', '#52b788', '#1b4332', '#74c69d',
             '#27ae60', '#1e8449', '#196f3d', '#28b463', '#0e6655']

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GeoJSON Comparison Visualizer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import clean font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    /* Root variables */
    :root {
        --bg: #0f1117;
        --surface: #1a1d27;
        --border: #2a2d3e;
        --text-primary: #e8eaf0;
        --text-muted: #6b7280;
        --accent-a: #e63946;
        --accent-b: #457b9d;
        --accent-c: #2d6a4f;
    }

    /* Global reset */
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    /* App background */
    .stApp {
        background: #0f1117;
    }

    /* Main container */
    .main .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
        max-width: 100%;
    }

    /* Hide default Streamlit header decorations */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Title area ── */
    .app-header {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }
    .app-title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #e8eaf0;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .app-subtitle {
        font-size: 0.82rem;
        color: #6b7280;
        font-weight: 400;
        margin: 0 0 1.5rem 0;
    }

    /* ── Dataset badge pills ── */
    .dataset-badges {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.7rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 500;
        font-family: 'IBM Plex Mono', monospace;
        border: 1px solid;
    }
    .badge-dot { width: 7px; height: 7px; border-radius: 50%; }
    .badge-a { color: #e63946; border-color: #e6394430; background: #e6394410; }
    .badge-b { color: #457b9d; border-color: #457b9d30; background: #457b9d10; }
    .badge-c { color: #2d6a4f;  border-color: #2d6a4f30;  background: #2d6a4f10; }

    /* ── Controls card ── */
    .controls-card {
        background: #1a1d27;
        border: 1px solid #2a2d3e;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .controls-title {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #6b7280;
        margin: 0 0 1rem 0;
    }

    /* ── Dataset column headers ── */
    .dataset-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
    }
    .dataset-stripe {
        width: 3px;
        height: 18px;
        border-radius: 2px;
    }
    .dataset-name {
        font-size: 0.82rem;
        font-weight: 600;
        color: #c8ccd8;
        font-family: 'IBM Plex Mono', monospace;
    }

    /* ── Year display ── */
    .year-display {
        background: #0f1117;
        border: 1px solid #2a2d3e;
        border-radius: 6px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .year-value {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.95rem;
        font-weight: 500;
        color: #e8eaf0;
    }
    .empire-count {
        font-size: 0.72rem;
        color: #6b7280;
    }
    .empire-count span {
        font-weight: 600;
        color: #9ca3b8;
    }

    /* ── Slider overrides ── */
    .stSlider > div > div > div > div {
        background: #2a2d3e !important;
    }
    .stSlider [data-baseweb="slider"] {
        margin-top: 0 !important;
    }

    /* ── Map section ── */
    .map-section-title {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #6b7280;
        margin: 0 0 1rem 0;
    }

    /* ── Map card wrapper ── */
    .map-card {
        background: #1a1d27;
        border: 1px solid #2a2d3e;
        border-radius: 8px;
        overflow: hidden;
    }
    .map-card-header {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #2a2d3e;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .map-card-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .map-card-label {
        font-size: 0.78rem;
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
        color: #9ca3b8;
    }
    .map-card-year {
        margin-left: auto;
        font-size: 0.72rem;
        font-family: 'IBM Plex Mono', monospace;
        color: #6b7280;
    }
    .map-card-body {
        padding: 0.75rem;
    }

    /* ── Empty state ── */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 300px;
        color: #4b5563;
        gap: 0.5rem;
    }
    .empty-state-icon { font-size: 2rem; }
    .empty-state-text { font-size: 0.82rem; }

    /* ── Streamlit metrics cleanup ── */
    [data-testid="metric-container"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    /* Divider */
    hr { border-color: #2a2d3e !important; margin: 1.25rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_filename(filename: str) -> Optional[tuple]:
    name = filename.replace('.geojson', '').replace('(', '').replace(')', '')
    match = re.match(r'^(.+?)_(\d+)(BCE|CE)_(\d+)(BCE|CE)$', name)
    if not match:
        return None
    empire = match.group(1).strip('_').strip()
    s_num, s_era = int(match.group(2)), match.group(3)
    e_num, e_era = int(match.group(4)), match.group(5)
    start = -s_num if s_era == 'BCE' else s_num
    end   = -e_num if e_era == 'BCE' else e_num
    if start > end:
        start, end = end, start
    return empire, start, end


def year_label(y: int) -> str:
    return f"{-y} BCE" if y < 0 else f"{y} CE"


@st.cache_resource
def get_mongo_client():
    client = MongoDBClient()
    if client.connect():
        try:
            client.collection.create_index("_filepath")
            client.collection.create_index("_filename")
        except Exception:
            pass
        return client
    return None


def build_file_index(filter_path: str, mongo_client) -> List[Dict]:
    if not mongo_client:
        return []
    entries = []
    try:
        query = {"_filepath": {"$regex": filter_path, "$options": "i"}}
        for doc in mongo_client.collection.find(query):
            filename = doc.get('_filename', '')
            if not filename.endswith('.geojson'):
                continue
            parsed = parse_filename(filename)
            if not parsed:
                continue
            empire, start, end = parsed
            entries.append({
                'filename': filename,
                'filepath': doc.get('_filepath', ''),
                '_id': doc.get('_id'),
                'geojson': doc,
                'empire': empire,
                'start': start,
                'end': end,
            })
    except Exception as e:
        st.error(f"MongoDB error: {e}")
    return entries


def build_timeline(index: List[Dict]) -> List[int]:
    years = set()
    for e in index:
        years.add(e['start'])
        years.add(e['end'])
    return sorted(years)


def active_at(index: List[Dict], year: int) -> List[Dict]:
    return [e for e in index if e['start'] <= year <= e['end']]


def build_map(files: List[Dict], palette: List[str]) -> folium.Map:
    m = folium.Map(
        location=INDIA_CENTRE,
        zoom_start=4,
        tiles='CartoDB positron',
        min_zoom=2,
        zoom_control=True,
        scrollWheelZoom=True,
    )
    for i, entry in enumerate(files):
        color = palette[i % len(palette)]
        try:
            data_clean = {k: v for k, v in entry['geojson'].items() if not k.startswith('_')}
        except Exception:
            continue
        display_name = entry['empire'].replace('_', ' ').title()
        yr_range = f"{year_label(entry['start'])} – {year_label(entry['end'])}"
        folium.GeoJson(
            data_clean,
            name=f"{display_name} ({yr_range})",
            style_function=lambda _, c=color: {
                'fillColor': c,
                'color': c,
                'weight': 1.5,
                'fillOpacity': 0.40,
            },
            tooltip=folium.Tooltip(f"<b>{display_name}</b><br><span style='color:#888'>{yr_range}</span>")
        ).add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)
    return m


def render_map_card(label: str, color: str, year_str: str, active: List[Dict], palette: List[str]):
    """Render a single map card with header and folium map."""
    st.markdown(f"""
    <div class="map-card">
        <div class="map-card-header">
            <div class="map-card-dot" style="background:{color}"></div>
            <span class="map-card-label">{label}</span>
            <span class="map-card-year">{year_str} · {len(active)} empire{'s' if len(active) != 1 else ''}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if active:
        m = build_map(active, palette)
        st_folium(m, use_container_width=True, height=480, returned_objects=[])
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">◌</div>
            <div class="empty-state-text">No active empires at this year</div>
        </div>
        """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # ── Header ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="app-header">
        <h1 class="app-title">GeoJSON Comparison Visualizer</h1>
    </div>
    <p class="app-subtitle">Compare geopolitical boundaries across three independent datasets with separate timeline controls</p>
    <div class="dataset-badges">
        <span class="badge badge-a"><span class="badge-dot" style="background:#e63946"></span>Dataset A — INDIAN_final</span>
        <span class="badge badge-b"><span class="badge-dot" style="background:#457b9d"></span>Dataset B — Geojson_FolderB_named</span>
        <span class="badge badge-c"><span class="badge-dot" style="background:#2d6a4f"></span>Dataset C — Ranjita_and_Ajay</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Session state init ────────────────────────────────────────────────
    for key, default in [
        ('index_a', []), ('index_b', []), ('index_c', []),
        ('tl_a', []),    ('tl_b', []),    ('tl_c', []),
        ('pos_a', 0),    ('pos_b', 0),    ('pos_c', 0),
        ('loaded', False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # ── MongoDB connect ───────────────────────────────────────────────────
    mongo_client = get_mongo_client()
    if not mongo_client:
        st.error("Failed to connect to MongoDB. Check your credentials and network.")
        return

    # ── Load data once ────────────────────────────────────────────────────
    if not st.session_state.loaded:
        with st.spinner("Loading datasets…"):
            st.session_state.index_a = build_file_index(FILTER_A, mongo_client)
            st.session_state.index_b = build_file_index(FILTER_B, mongo_client)
            st.session_state.index_c = build_file_index(FILTER_C, mongo_client)
            st.session_state.tl_a    = build_timeline(st.session_state.index_a)
            st.session_state.tl_b    = build_timeline(st.session_state.index_b)
            st.session_state.tl_c    = build_timeline(st.session_state.index_c)
            st.session_state.loaded  = True

    # ── Controls card ─────────────────────────────────────────────────────
    st.markdown('<div class="controls-card"><p class="controls-title">Timeline Controls</p>', unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)

    datasets = [
        (col_a, 'index_a', 'tl_a', 'pos_a', 'slider_a', LABEL_A, '#e63946', PALETTE_A),
        (col_b, 'index_b', 'tl_b', 'pos_b', 'slider_b', LABEL_B, '#457b9d', PALETTE_B),
        (col_c, 'index_c', 'tl_c', 'pos_c', 'slider_c', LABEL_C, '#2d6a4f', PALETTE_C),
    ]

    active_results = {}

    for col, idx_key, tl_key, pos_key, slider_key, label, color, palette in datasets:
        with col:
            tl = st.session_state[tl_key]
            st.markdown(f"""
            <div class="dataset-header">
                <div class="dataset-stripe" style="background:{color}"></div>
                <span class="dataset-name">{label}</span>
            </div>
            """, unsafe_allow_html=True)

            if tl:
                pos = st.slider(
                    "pos", 0, len(tl) - 1,
                    st.session_state[pos_key],
                    key=slider_key,
                    label_visibility="collapsed"
                )
                st.session_state[pos_key] = pos
                year = tl[pos]
                active = active_at(st.session_state[idx_key], year)
                active_results[label] = (year, active, palette, color)

                st.markdown(f"""
                <div class="year-display">
                    <span class="year-value">{year_label(year)}</span>
                    <span class="empire-count"><span>{len(active)}</span> empire{'s' if len(active) != 1 else ''} · {len(st.session_state[idx_key])} total</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<p style="color:#6b7280;font-size:0.82rem;">No data loaded</p>', unsafe_allow_html=True)
                active_results[label] = (0, [], palette, color)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Maps ──────────────────────────────────────────────────────────────
    st.markdown('<p class="map-section-title">Map Views</p>', unsafe_allow_html=True)

    # Row 1: Dataset A and B
    map_col1, map_col2 = st.columns(2)

    year_a, active_a, pal_a, col_a_color = active_results.get(LABEL_A, (0, [], PALETTE_A, '#e63946'))
    year_b, active_b, pal_b, col_b_color = active_results.get(LABEL_B, (0, [], PALETTE_B, '#457b9d'))
    year_c, active_c, pal_c, col_c_color = active_results.get(LABEL_C, (0, [], PALETTE_C, '#2d6a4f'))

    with map_col1:
        render_map_card(LABEL_A, col_a_color, year_label(year_a), active_a, pal_a)

    with map_col2:
        render_map_card(LABEL_B, col_b_color, year_label(year_b), active_b, pal_b)

    # Row 2: Dataset C — full width
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    render_map_card(LABEL_C, col_c_color, year_label(year_c), active_c, pal_c)


if __name__ == '__main__':
    main()