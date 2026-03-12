#!/usr/bin/env python3
"""
Streamlit Comparison Visualizer for MongoDB GeoJSON Data
Clean, light-themed interface with proper map rendering and borders
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
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
        overflow: hidden;
    }

    /* Light Theme Main Background */
    .stApp {
        background: #f4f6f8;
    }

    /* 1. Distribute empty space: Frame the entire app nicely */
    .main .block-container {
        padding: 1.5rem 2.5rem !important; 
        max-width: 100% !important;
        height: 100vh;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* 2. Map card header styling */
    .map-card-header {
        background: #f9fafb;
        padding: 12px 18px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        border-bottom: 1px solid #e5e7eb;
    }
    .map-card-dataset {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.06em;
    }
    .map-card-year {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 1.15rem;
        font-weight: 700;
    }
    .map-card-sub {
        font-size: 0.7rem;
        color: #6b7280;
        margin-top: 4px;
    }

    /* 3. Controller Panel Typography */
    .ctrl-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        color: #4b5563;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 24px;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 12px;
    }
    .ctrl-dataset-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .ctrl-step {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 12px;
    }

    /* Clean up Streamlit buttons for Light Theme */
    .stButton > button {
        border-radius: 6px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
        padding: 4px 12px !important;
        height: 38px !important;
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        color: #374151 !important;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        border-color: #9ca3af !important;
        background-color: #f3f4f6 !important;
        color: #111827 !important;
    }

    /* Empty state styling */
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #9ca3af;
        gap: 0.4rem;
        height: 100%;
    }

    /* 4. The main structural fix: clear borders, background, and rounded corners for each box */
    [data-testid="column"] > div {
        background: #ffffff;
        border: 1px solid #e5e7eb; /* Soft light gray border */
        border-radius: 10px; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04); /* Much softer shadow for light theme */
        height: 100%;
        overflow: hidden; 
    }

    /* 5. Add inner padding exclusively to the 4th box (Control Panel) */
    div[data-testid="stHorizontalBlock"]:last-of-type > [data-testid="column"]:last-of-type > div {
        padding: 2rem;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
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


def render_map_card(dataset_label: str, color: str, year_str: str, step: int, total_steps: int, empire_count: int, active: List[Dict], palette: List[str], map_height: int):
    """Render a single map panel with compact header."""
    # Changed the year text color from light gray to dark slate (#111827) for the light theme
    st.markdown(f"""
    <div class="map-card-header">
        <div class="map-card-dataset" style="color:{color}">Dataset {dataset_label} &nbsp; <span style="color:#111827;font-size:1.15rem;">{year_str}</span></div>
        <div class="map-card-sub">Step {step}/{total_steps} &nbsp;·&nbsp; {empire_count} empire{'s' if empire_count != 1 else ''}</div>
    </div>
    """, unsafe_allow_html=True)

    if active:
        m = build_map(active, palette)
        st_folium(m, use_container_width=True, height=map_height, returned_objects=[])
    else:
        st.markdown(f"""
        <div class="empty-state" style="height:{map_height}px;">
            <span style="font-size:2.5rem;">◌</span>
            <span style="font-size:0.85rem;">No active empires at this year</span>
        </div>
        """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
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

    # ── Compute current state ─────────────────────────────────────────────
    def get_state(idx_key, tl_key, pos_key):
        tl = st.session_state[tl_key]
        pos = st.session_state[pos_key]
        if tl and 0 <= pos < len(tl):
            year = tl[pos]
            active = active_at(st.session_state[idx_key], year)
            return year, active, pos + 1, len(tl)
        return 0, [], 0, 0

    year_a, active_a, step_a, total_a = get_state('index_a', 'tl_a', 'pos_a')
    year_b, active_b, step_b, total_b = get_state('index_b', 'tl_b', 'pos_b')
    year_c, active_c, step_c, total_c = get_state('index_c', 'tl_c', 'pos_c')

    MAP_H = 340 

    # ── 2×2 Grid ──────────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="large")

    with col1:
        render_map_card("A", '#e63946', year_label(year_a), step_a, total_a, len(active_a), active_a, PALETTE_A, MAP_H)

    with col2:
        render_map_card("B", '#457b9d', year_label(year_b), step_b, total_b, len(active_b), active_b, PALETTE_B, MAP_H)
        
    # Vertical gap between rows
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    col3, col4 = st.columns(2, gap="large")

    with col3:
        render_map_card("C", '#2d6a4f', year_label(year_c), step_c, total_c, len(active_c), active_c, PALETTE_C, MAP_H)

    with col4:
        st.markdown('<p class="ctrl-title">GeoJSON Comparison — Dual Timeline</p>', unsafe_allow_html=True)

        # Dataset A row
        st.markdown(f'<div class="ctrl-dataset-label" style="color:#e63946;">Dataset A &nbsp; <span style="color:#111827;">{year_label(year_a)}</span></div><div class="ctrl-step">Step {step_a}/{total_a} · {len(active_a)} empires</div>', unsafe_allow_html=True)
        ca1, ca2 = st.columns(2)
        with ca1:
            if st.button("◀ Prev A", key="prev_a", use_container_width=True):
                st.session_state['pos_a'] = max(0, st.session_state['pos_a'] - 1)
                st.rerun()
        with ca2:
            if st.button("Next A ▶", key="next_a", use_container_width=True):
                st.session_state['pos_a'] = min(total_a - 1, st.session_state['pos_a'] + 1)
                st.rerun()

        # Changed border color to a light gray for dividers
        st.markdown("<hr style='border-color:#e5e7eb; margin: 16px 0;'/>", unsafe_allow_html=True)

        # Dataset B row
        st.markdown(f'<div class="ctrl-dataset-label" style="color:#457b9d;">Dataset B &nbsp; <span style="color:#111827;">{year_label(year_b)}</span></div><div class="ctrl-step">Step {step_b}/{total_b} · {len(active_b)} empires</div>', unsafe_allow_html=True)
        cb1, cb2 = st.columns(2)
        with cb1:
            if st.button("◀ Prev B", key="prev_b", use_container_width=True):
                st.session_state['pos_b'] = max(0, st.session_state['pos_b'] - 1)
                st.rerun()
        with cb2:
            if st.button("Next B ▶", key="next_b", use_container_width=True):
                st.session_state['pos_b'] = min(total_b - 1, st.session_state['pos_b'] + 1)
                st.rerun()

        st.markdown("<hr style='border-color:#e5e7eb; margin: 16px 0;'/>", unsafe_allow_html=True)

        # Dataset C row
        st.markdown(f'<div class="ctrl-dataset-label" style="color:#2d6a4f;">Dataset C &nbsp; <span style="color:#111827;">{year_label(year_c)}</span></div><div class="ctrl-step">Step {step_c}/{total_c} · {len(active_c)} empires</div>', unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("◀ Prev C", key="prev_c", use_container_width=True):
                st.session_state['pos_c'] = max(0, st.session_state['pos_c'] - 1)
                st.rerun()
        with cc2:
            if st.button("Next C ▶", key="next_c", use_container_width=True):
                st.session_state['pos_c'] = min(total_c - 1, st.session_state['pos_c'] + 1)
                st.rerun()


if __name__ == '__main__':
    main()