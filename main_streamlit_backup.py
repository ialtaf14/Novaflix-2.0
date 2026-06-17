import streamlit as st
import os
import streamlit.components.v1 as components
import streamlit_option_menu
import base64
from PIL import Image
from streamlit_cropper import st_cropper
from processing import preprocess
from processing import auth
from processing.display import Main
from processing import session_manager

st.set_page_config(page_title="NovaFlix", layout="wide")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded_string}"
    except:
        return ""

GLASS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ─── Root / Reset ─────────────────────────────────────────────────── */
* { box-sizing: border-box; }

body, html, .stApp {
    background: #080808;
    color: white;
    font-family: 'Inter', sans-serif !important;
    user-select: none !important;
    -webkit-user-select: none !important;
    /* ── Remove horizontal scrollbar ── */
    overflow-x: hidden !important;
    max-width: 100vw !important;
}

/* Re-enable selection for input fields */
input, textarea, [contenteditable="true"] {
    user-select: auto !important;
    -webkit-user-select: auto !important;
}

/* Hide Streamlit Default Header (Removes Blue/White bar at top) */
header[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    display: none !important;
    height: 0 !important;
}

/* Prevent Option Menu Wrapper from Collapsing during Streamlit reruns */
div:has(> iframe[title="streamlit_option_menu.option_menu"]) {
    min-height: 70px !important;
}

/* Global Tab Styling (Removes Default Blue Line) */
[data-testid="stTabList"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(255,255,255,0.1) !important;
}
[data-testid="stTab"] button {
    color: #888 !important;
}
[data-testid="stTab"] button[aria-selected="true"] {
    color: var(--primary-color) !important;
    border-bottom: 3px solid var(--primary-color) !important;
}

/* ─── Block container — laptop-optimised width ──────────────────────── */
.block-container {
    max-width: 1400px !important;
    width: 100% !important;
    padding: 1.5rem 2rem !important;
    margin: 0 auto !important;
    overflow-x: hidden !important;
}

/* ─── Typography ────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.5px;
    line-height: 1.25;
}
h1, .stMarkdown h1 { font-size: clamp(1.8rem, 2.5vw, 2.8rem) !important; font-weight: 800; }
h2, .stMarkdown h2 { font-size: clamp(1.4rem, 2vw, 2rem) !important; font-weight: 700; }
h3, .stMarkdown h3 { font-size: clamp(1.1rem, 1.5vw, 1.5rem) !important; font-weight: 600; }
p, .stMarkdown p { font-size: clamp(0.9rem, 1.1vw, 1.05rem) !important; line-height: 1.7; color: #ddd; }
label, .stMarkdown li { font-size: clamp(0.85rem, 1vw, 1rem) !important; }

/* ─── Glassmorphism Containers ──────────────────────────────────────── */
[data-testid="stVerticalBlock"] {
    background: rgba(0, 0, 0, 0.55) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 20px !important;
    padding: 12px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.4s ease;
}
[data-testid="stVerticalBlock"]:hover {
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    background: rgba(0, 0, 0, 0.65) !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5) !important;
}
/* Remove double-box from nested blocks */
[data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

/* ─── Global Input & Dropdown Glassmorphism ────────────────────────── */
/* Targeted reset for all input-like containers */
div[data-testid="stFileUploader"],
div[data-testid="stFileUploadDropzone"],
div[data-testid="stFileUploadDropzone"] > section,
.stTextArea, .stTextInput, .stSelectbox, .stMultiSelect {
    background-color: transparent !important;
}

input, textarea, select,
div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="base-input"],
[data-testid="stFileUploadDropzone"] {
    background: rgba(0, 0, 0, 0.45) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    transition: all 0.3s ease !important;
}

/* Force inner text areas and inputs to be transparent */
.stTextArea textarea, .stTextInput input {
    background: transparent !important;
    border: none !important;
}

/* Specific target for the dropdown list items */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"], 
[data-testid="stVirtualDropdown"] {
    background: rgba(15, 15, 15, 0.75) !important;
    backdrop-filter: blur(30px) !important;
    -webkit-backdrop-filter: blur(30px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
}

div[data-baseweb="popover"] *,
div[data-baseweb="menu"] * {
    background-color: transparent !important;
    color: white !important;
}

li[role="option"] {
    background: transparent !important;
    color: white !important;
    padding: 10px 15px !important;
    transition: all 0.2s ease !important;
}

li[role="option"]:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    color: var(--primary-color) !important;
}

div[data-baseweb="input"]:focus-within,
div[data-baseweb="select"]:focus-within {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 3px var(--glow-color) !important;
}

/* Remove default dark backgrounds from Streamlit's internal widgets */
.stTextInput > div > div,
.stSelectbox > div > div,
.stTextArea > div > div,
.stMultiSelect > div > div {
    background: transparent !important;
    border: none !important;
}

/* ─── Buttons ───────────────────────────────────────────────────────── */
.stButton > button,
[data-testid="stLinkButton"] > a,
.stDownloadButton > button {
    background: rgba(0, 0, 0, 0.45) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.stButton > button:hover,
[data-testid="stLinkButton"] > a:hover,
.stDownloadButton > button:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    border-color: rgba(255,255,255,0.3) !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ─── Images (Posters) ──────────────────────────────────────────────── */
[data-testid="stImage"] {
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.35s ease !important;
    border-radius: 14px !important;
}
[data-testid="stImage"]:hover {
    transform: scale(1.08) translateY(-4px) !important;
    z-index: 999 !important;
    position: relative !important;
    box-shadow: 0 18px 40px rgba(0,0,0,0.65), 0 0 22px rgba(255, 75, 43, 0.45) !important;
}
img { border-radius: 14px !important; box-shadow: 0 4px 14px rgba(0,0,0,0.3) !important; }

/* ─── Keyframes ─────────────────────────────────────────────────────── */
@keyframes fadeInSlideUp {
    0%   { opacity: 0; transform: translateY(30px) scale(0.97); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes shimmer {
    0%   { background-position: -1000px 0; }
    100% { background-position: 1000px 0; }
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 8px rgba(255,75,43,0.3); }
    50%       { box-shadow: 0 0 20px rgba(255,75,43,0.65); }
}
@keyframes floatUp {
    0%, 100% { transform: translateY(0); }
    50%       { transform: translateY(-6px); }
}

/* Apply entrance animation to main content blocks */
[data-testid="stVerticalBlock"] > div > div > div {
    animation: fadeInSlideUp 0.65s cubic-bezier(0.16, 1, 0.3, 1) both;
}

/* ─── Skeleton ──────────────────────────────────────────────────────── */
.skeleton-box {
    display: inline-block; width: 100%;
    background: rgba(0, 0, 0, 0.35);
    background-image: linear-gradient(90deg, rgba(255,255,255,0.0) 0px, rgba(255,255,255,0.1) 40px, rgba(255,255,255,0.0) 80px);
    background-size: 1000px 100%;
    animation: shimmer 2s infinite linear;
    border-radius: 14px;
}

/* ─── Metric Badges ─────────────────────────────────────────────────── */
.metric-badge {
    background: rgba(0, 0, 0, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 14px 6px;
    margin-bottom: 12px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    cursor: default;
}
.metric-badge:hover {
    transform: translateY(-6px) scale(1.03);
    background: rgba(255, 75, 43, 0.12);
    box-shadow: 0 10px 28px rgba(255, 75, 43, 0.3);
    border-color: rgba(255, 75, 43, 0.55);
}
.metric-value {
    font-size: clamp(1rem, 1.4vw, 1.25rem);
    font-weight: 800;
    color: #ff4b2b;
    margin-bottom: 4px;
    font-family: 'Inter', sans-serif;
}
.metric-label {
    font-size: clamp(0.6rem, 0.8vw, 0.72rem);
    color: #aaa;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-family: 'Inter', sans-serif;
}

/* ─── Staggered Animations ──────────────────────────────────────────── */
.animate-delay-1 { animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.05s both; }
.animate-delay-2 { animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.15s both; }
.animate-delay-3 { animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.25s both; }
.animate-delay-4 { animation: fadeInSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.35s both; }

/* ─── Flashlight overlay ────────────────────────────────────────────── */
.flashlight-overlay {
    position: fixed; top: 0; left: 0;
    width: 100vw; height: 100vh;
    pointer-events: none;
    background: radial-gradient(
        circle 500px at var(--mouse-x, 50vw) var(--mouse-y, 50vh),
        rgba(255, 255, 255, 0.07), transparent 80%);
    z-index: 9999; mix-blend-mode: screen;
}

/* ─── View Full Cast Button ─────────────────────────────────────────── */
div[data-testid="stButton"]:has(button[title="view_full_cast"]) {
    display: flex; justify-content: center; margin: 18px 0;
}
button[title="view_full_cast"] {
    background: rgba(135, 206, 235, 0.12) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(135, 206, 235, 0.35) !important;
    color: #87CEEB !important;
    border-radius: 24px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.45rem 2.2rem !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.5px;
}
button[title="view_full_cast"]:hover {
    background: rgba(135, 206, 235, 0.25) !important;
    box-shadow: 0 0 18px rgba(135, 206, 235, 0.35) !important;
    transform: scale(1.06) !important;
}

/* ─── Option Menu (Navigation) — active tab highlight ───────────────── */
.nav-link {
    border-radius: 50px !important;
    margin: 0 6px !important;
    padding: 8px 20px !important;
    transition: all 0.3s ease !important;
    color: rgba(255, 255, 255, 0.7) !important;
    font-weight: 500 !important;
}

.nav-link:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    color: white !important;
}

.nav-link-selected,
.nav-link.active {
    background: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    border-radius: 50px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    backdrop-filter: blur(10px) !important;
}

/* ─── Header Container Style ────────────────────────────────────────── */
.custom-header-container {
    background: rgba(0, 0, 0, 0.6) !important;
    backdrop-filter: blur(30px) !important;
    -webkit-backdrop-filter: blur(30px) !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 20px !important;
    padding: 2px 25px !important;
    margin-bottom: 25px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5) !important;
}

.header-logo {
    font-size: 26px;
    font-weight: 900;
    background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -1.2px;
    white-space: nowrap;
    display: flex;
    align-items: center;
    height: 60px;
}

.header-icons {
    display: flex;
    gap: 25px;
    align-items: center;
    justify-content: flex-end;
    color: white;
    font-size: 20px;
    height: 60px;
}

.header-icon-item {
    cursor: pointer;
    transition: transform 0.2s ease, opacity 0.2s ease;
    opacity: 0.8;
}

.header-icon-item:hover {
    transform: scale(1.1);
    opacity: 1;
}

/* ─── Recommendation Grid Fixes ─────────────────────────────────────── */
.movie-poster-container {
    height: 320px !important;
    width: 100% !important;
    overflow: hidden !important;
    border-radius: 14px !important;
    margin-bottom: 8px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    position: relative !important;
}
.movie-poster-container img.main-poster {
    height: 100% !important;
    width: 100% !important;
    object-fit: cover !important;
    transition: transform 0.5s ease !important;
    display: block !important;
}
.movie-poster-container:hover img.main-poster {
    transform: scale(1.1) !important;
}
.provider-logo-overlay {
    position: absolute !important;
    bottom: 10px !important;
    right: 10px !important;
    width: 32px !important;
    height: 32px !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.6) !important;
    z-index: 10 !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    object-fit: contain !important;
    background: rgba(0, 0, 0, 0.5) !important;
    backdrop-filter: blur(5px) !important;
}
/* Movie title buttons — stay inside card, wrap cleanly */
div.stButton > button {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
}
div.stButton > button p {
    white-space: normal !important;
    overflow: hidden !important;
    word-break: break-word !important;
    text-overflow: unset !important;
    display: -webkit-box !important;
    -webkit-line-clamp: 2 !important;
    -webkit-box-orient: vertical !important;
    line-height: 1.3 !important;
    max-height: 2.6em !important;
}
/* ─── Horizontal Scroll / Swipe Right ──────────────────────────────── */
.stHorizontalBlock {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    flex-wrap: nowrap !important;
    gap: 1.8rem !important;
    padding: 15px 5px !important;
    padding-bottom: 25px !important;
    scrollbar-width: thin !important;
    scrollbar-color: #ff4b2b transparent !important;
    scroll-behavior: smooth !important;
}
.stHorizontalBlock::-webkit-scrollbar {
    height: 4px !important;
}
.stHorizontalBlock::-webkit-scrollbar-thumb {
    background: linear-gradient(90deg, #ff4b2b, #ff416c) !important;
    border-radius: 10px !important;
}
.stHorizontalBlock > div {
    min-width: 220px !important;
    max-width: 220px !important;
    flex-shrink: 0 !important;
    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    animation: slideUpFade 0.6s ease-out forwards !important;
    opacity: 0;
}

@keyframes slideUpFade {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.stHorizontalBlock > div:hover {
    transform: translateY(-12px) scale(1.03) !important;
    z-index: 10 !important;
}

.movie-poster-container {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    transition: all 0.4s ease;
    border: 1px solid rgba(255,255,255,0.1);
}

.stHorizontalBlock > div:hover .movie-poster-container {
    box-shadow: 0 15px 35px rgba(255, 75, 43, 0.4);
    border: 1px solid rgba(255, 75, 43, 0.6);
}

.main-poster {
    width: 100%;
    height: 320px;
    object-fit: cover;
    transition: filter 0.4s ease;
}

.stHorizontalBlock > div:hover .main-poster {
    filter: brightness(1.1) contrast(1.1);
}
</style>
"""
st.markdown(GLASS_CSS, unsafe_allow_html=True)

displayed = []

def format_currency(value):
    try:
        val = float(value)
        if val <= 0:
            return "Unknown"
        if val >= 1_000_000_000:
            return f"${val / 1_000_000_000:.2f}B"
        elif val >= 1_000_000:
            return f"${val / 1_000_000:.1f}M"
        elif val >= 1_000:
            return f"${val / 1_000:.1f}K"
        else:
            return f"${val:.0f}"
    except:
        return "Unknown"

def format_number(value):
    try:
        if isinstance(value, str):
            value = value.replace(',', '')
        val = float(value)
        if val >= 1_000_000_000:
            return f"{val / 1_000_000_000:.1f}B"
        elif val >= 1_000_000:
            return f"{val / 1_000_000:.1f}M"
        elif val >= 1_000:
            return f"{val / 1_000:.1f}K"
        else:
            return f"{val:.0f}"
    except:
        return str(value)


def format_runtime(minutes):
    try:
        m = int(float(minutes))
        if m <= 0:
            return "Unknown"
        hours = m // 60
        mins = m % 60
        if hours > 0:
            return f"{m} mins ({hours}h {mins}m)"
        return f"{m} mins"
    except:
        return "Unknown"

import re
import urllib.request
import urllib.parse
import pandas as pd

@st.cache_data(show_spinner=False, ttl=86400 * 7)
def get_trailer_url(movie_name):
    try:
        search_keyword = urllib.parse.quote_plus(f"{movie_name} official trailer")
        html = urllib.request.urlopen(f"https://www.youtube.com/results?search_query={search_keyword}", timeout=5)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
        return None
    except:
        return None

@st.cache_data(show_spinner=False, ttl=86400 * 7)
def get_screenshots(movie_name):
    try:
        url = f"https://www.bing.com/images/search?q={urllib.parse.quote_plus(movie_name + ' movie screencap 1080p wallpaper')}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
        imgs = re.findall(r'murl&quot;:&quot;(.*?)&quot;', html)
        return imgs[:4]
    except Exception as e:
        print("Screenshot error:", e)
        return []

def get_franchise_movies(title, movies_df, include_self=False):
    try:
        base = title.split(':')[0].split('-')[0].strip()
        base = re.sub(r'\s+\d+$', '', base)
        if len(base) < 4:
            return []
        franchise_df = movies_df[movies_df['title'].str.contains(f"^{re.escape(base)}", case=False, na=False)].copy()
        
        if not include_self:
            franchise_df = franchise_df[franchise_df['title'] != title]
        
        # Sort chronologically
        if 'release_date' in franchise_df.columns:
            franchise_df['release_date'] = pd.to_datetime(franchise_df['release_date'], errors='coerce')
            franchise_df = franchise_df.sort_values(by='release_date')
        
        franchise = franchise_df['title'].tolist()
        return franchise[:10]
    except Exception as e:
        print("Franchise Error:", e)
        return []

# ── Basic session defaults ─────────────────────────────────────────────────────
if 'movie_number' not in st.session_state:
    st.session_state['movie_number'] = 0

if 'selected_movie_name' not in st.session_state:
    st.session_state['selected_movie_name'] = ""

if 'user_menu' not in st.session_state:
    st.session_state['user_menu'] = ""

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'session_token' not in st.session_state:
    st.session_state.session_token = ""

if 'user_data' not in st.session_state:
    st.session_state.user_data = None

if 'bg_url' not in st.session_state:
    st.session_state.bg_url = None

if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "#ff4b2b"

if 'glow_color' not in st.session_state:
    st.session_state.glow_color = "rgba(255, 75, 43, 0.5)"

if 'wishlist' not in st.session_state:
    st.session_state['wishlist'] = []

if 'watched_list' not in st.session_state:
    st.session_state['watched_list'] = []

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': 'User',
        'bio': 'NovaFlix Movie Enthusiast',
        'instagram_id': '',
        'photo_url': 'https://www.pngall.com/wp-content/uploads/5/Profile-Avatar-PNG.png',
        'avatar': '👤'
    }
else:
    defaults = {
        'name': 'User',
        'bio': 'NovaFlix Movie Enthusiast',
        'instagram_id': '',
        'photo_url': 'https://www.pngall.com/wp-content/uploads/5/Profile-Avatar-PNG.png'
    }
    for key, val in defaults.items():
        if key not in st.session_state.user_profile:
            st.session_state.user_profile[key] = val

if 'edit_profile_mode' not in st.session_state:
    st.session_state.edit_profile_mode = False

# ── Token auto-restore: push localStorage token → query_params (JS bridge) ────
# This JS runs on every page load. If a token exists in localStorage but is
# absent from the URL, it adds it and does a silent one-time redirect so Python
# can read it from st.query_params on the next Streamlit rerun.
_ls_bridge_js = """
<script>
(function() {
    var tok = localStorage.getItem('nf_session_token');
    if (!tok) return;
    var url = new URL(window.location.href);
    if (url.searchParams.get('token') !== tok) {
        url.searchParams.set('token', tok);
        // Preserve 'page' param if already present
        window.location.replace(url.toString());
    }
})();
</script>
"""
if not st.session_state.authenticated:
    st.markdown(_ls_bridge_js, unsafe_allow_html=True)

# ── Token validation: auto-login if valid token is in query_params ─────────────
if not st.session_state.authenticated:
    _qp_token = st.query_params.get('token', '')
    if _qp_token:
        _restored_username = session_manager.validate_session(_qp_token)
        if _restored_username:
            _users = auth.load_users()
            if _restored_username in _users:
                _udata = _users[_restored_username]
                st.session_state.authenticated    = True
                st.session_state.session_token    = _qp_token
                st.session_state.user_username    = _restored_username
                st.session_state.user_data        = _udata
                st.session_state.user_profile     = _udata.get('profile', st.session_state.user_profile)
                st.session_state.user_profile['name'] = _udata.get('name', 'User')
                st.session_state.wishlist         = _udata.get('wishlist', [])
                st.session_state.watched_list     = _udata.get('watched_list', [])
                # Restore page from query params
                _saved_page = st.query_params.get('page', 'Discover')
                if _saved_page in ['Discover', 'Movies', 'Profile', 'Movie Details', 'Actor Details']:
                    st.session_state.user_menu = _saved_page
        else:
            # Token invalid/expired — clear it from URL and localStorage
            st.query_params.pop('token', None)
            st.markdown("<script>localStorage.removeItem('nf_session_token');</script>",
                        unsafe_allow_html=True)

if 'privacy_mode' not in st.session_state:
    st.session_state.privacy_mode = False

if 'privacy_settings' not in st.session_state:
    st.session_state.privacy_settings = {
        'public_profile': True,
        'activity_status': False,
        'personalized_recs': True,
        'allow_analytics': True
    }

def display_forgot_password_page():
    st.markdown("""
    <style>
    /* ─── Page Container & Background ──────────────────────────────────── */
    .block-container {
        max-width: 480px !important;
        width: 100% !important;
        padding-top: 4vh !important;
        padding-bottom: 4vh !important;
        overflow-x: hidden !important;
    }
    
    /* ─── Glassmorphism Login Container ────────────────────────────────── */
    div.block-container > div > [data-testid="stVerticalBlock"] {
        background: rgba(10, 10, 15, 0.7) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 45px 35px !important;
        border-radius: 28px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        animation: entranceCard 0.8s cubic-bezier(0.16, 1, 0.3, 1) both !important;
        transition: all 0.4s ease !important;
    }
    div.block-container > div > [data-testid="stVerticalBlock"]:hover {
        border: 1px solid rgba(255, 75, 43, 0.3) !important;
        box-shadow: 0 25px 60px rgba(255, 75, 43, 0.15), 
                    0 20px 50px rgba(0, 0, 0, 0.7) !important;
    }
    
    /* Remove double-box styling for nested containers */
    div.block-container > div > [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
        backdrop-filter: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        animation: none !important;
    }

    /* ─── Form Container Reset ────────────────────────────────────────── */
    div[data-testid="stForm"] {
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* ─── Entrance Animations ─────────────────────────────────────────── */
    @keyframes entranceCard {
        0% {
            opacity: 0;
            transform: translateY(40px) scale(0.96);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ─── Brand Header ───────────────────────────────────────── */
    .brand-title {
        font-size: 3.4rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #ff4b2b 0%, #ff416c 35%, #8a2be2 70%, #ff4b2b 100%) !important;
        background-size: 300% auto !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 8px !important;
        animation: shimmer 6s infinite linear !important;
        letter-spacing: -1.5px !important;
        text-align: center !important;
    }

    /* ─── Input Fields Glassmorphism & Glow ──────────────────────────── */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        color: white !important;
        padding: 12px 16px !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }

    .stTextInput input:focus {
        border-color: rgba(255, 75, 43, 0.8) !important;
        box-shadow: 0 0 15px rgba(255, 75, 43, 0.25), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }

    /* ─── Action Buttons (Primary / Form Submit) ────────────────────── */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%) !important;
        border: none !important;
        border-radius: 14px !important;
        color: white !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        box-shadow: 0 8px 24px rgba(255, 75, 43, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        margin-top: 15px !important;
        width: 100% !important;
    }

    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(255, 75, 43, 0.45), 
                    0 0 15px rgba(255, 75, 43, 0.2) !important;
        color: white !important;
    }

    .stFormSubmitButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* ─── Secondary Buttons (Forgot Password / Back to Login) ────────── */
    .stButton > button {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.3s ease !important;
        margin-top: 10px !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    logo_base64 = get_base64_image('logo.jpg')
    if logo_base64:
        st.markdown(f"""
        <div style='text-align:center; margin-bottom: 20px;'>
            <img src="{logo_base64}" style='width: 200px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);'>
            <p style='color:#888; font-size:1rem; letter-spacing: 0.5px; text-align: center; margin-top: 15px;'>Password Recovery</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; margin-bottom: 30px;'>
            <h1 class="brand-title">NovaFlix</h1>
            <p style='color:#888; font-size:1rem; letter-spacing: 0.5px; text-align: center;'>Password Recovery</p>
        </div>
        """, unsafe_allow_html=True)

    if 'forgot_step' not in st.session_state:
        st.session_state.forgot_step = 'send_otp'

    if st.session_state.forgot_step == 'send_otp':
        # Add temporary SMTP configuration helper if no credentials exist
        has_credentials = False
        try:
            if st.secrets.get("EMAIL_SENDER") and st.secrets.get("EMAIL_PASSWORD"):
                has_credentials = True
        except:
            pass
        if not has_credentials:
            if os.environ.get("EMAIL_SENDER") and os.environ.get("EMAIL_PASSWORD"):
                has_credentials = True
            elif st.session_state.get("temp_email_sender") and st.session_state.get("temp_email_password"):
                has_credentials = True

        if not has_credentials:
            st.warning("⚠️ Gmail configuration missing: To send a real email, configure SMTP credentials below.")
            with st.expander("Configure Gmail SMTP Sender (Temporary)", expanded=True):
                temp_sender = st.text_input("Sender Gmail Address", placeholder="example@gmail.com", key="smtp_sender_input")
                temp_password = st.text_input("Gmail App Password", type="password", placeholder="16-character app password", key="smtp_pass_input")
                if temp_sender and temp_password:
                    st.session_state.temp_email_sender = temp_sender.strip()
                    st.session_state.temp_email_password = temp_password.strip()
                    st.success("✔️ Temporary credentials loaded! Ready to send OTP.")
                else:
                    st.session_state.temp_email_sender = None
                    st.session_state.temp_email_password = None

        with st.form("send_otp_form", border=False):
            st.subheader("Recover Password")
            username = st.text_input("Username")
            submit = st.form_submit_button("Send Verification Code", use_container_width=True)

            if submit:
                if not username:
                    st.error("Please enter your username!")
                else:
                    email = auth.get_user_email(username)
                    if email:
                        from processing import email_service
                        otp = email_service.generate_otp()
                        st.session_state.forgot_otp = otp
                        st.session_state.forgot_username = username
                        st.session_state.forgot_email = email
                        
                        success, message = email_service.send_otp_email(email, otp)
                        if success:
                            st.success(f"OTP has been sent to your registered Gmail address.")
                            st.session_state.forgot_step = 'verify_otp'
                            st.rerun()
                        elif message == "SMTP_NOT_CONFIGURED":
                            st.warning("Gmail credentials are not configured in secrets.toml (EMAIL_SENDER/EMAIL_PASSWORD).")
                            st.info(f"[Local Testing] Your verification code is: {otp}")
                            st.session_state.forgot_step = 'verify_otp'
                            st.rerun()
                        else:
                            st.error(f"Failed to send email: {message}")
                    else:
                        st.error("Username not found!")

    elif st.session_state.forgot_step == 'verify_otp':
        raw_email = st.session_state.forgot_email
        if raw_email and '@' in raw_email:
            parts = raw_email.split('@')
            user_part = parts[0]
            n = len(user_part)
            if n <= 1:
                masked_user = "*"
            elif n == 2:
                masked_user = user_part[0] + "*"
            else:
                masked_user = user_part[0] + '*' * (n - 2) + user_part[-1]
            masked_email = f"{masked_user}@{parts[1]}"
        else:
            masked_email = "registered email"

        st.info(f"Verification code sent to {masked_email}")

        with st.form("verify_otp_form", border=False):
            otp_input = st.text_input("Verification Code (OTP)")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            submit = st.form_submit_button("Reset Password", use_container_width=True)

            if submit:
                if not otp_input or not new_password or not confirm_password:
                    st.error("Please fill in all fields!")
                elif otp_input.strip() != st.session_state.forgot_otp:
                    st.error("Invalid verification code!")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters long!")
                else:
                    success, msg = auth.reset_password(st.session_state.forgot_username, new_password)
                    if success:
                        st.success("Password reset successfully! Please sign in with your new password.")
                        st.session_state.forgot_password_mode = False
                        st.session_state.forgot_step = 'send_otp'
                        st.rerun()
                    else:
                        st.error(msg)

    if st.button("← Back to Login", key="back_to_login", use_container_width=True):
        st.session_state.forgot_password_mode = False
        st.session_state.forgot_step = 'send_otp'
        st.rerun()

def get_adaptive_colors(url):
    try:
        import requests
        from PIL import Image
        import io
        response = requests.get(url, timeout=2)
        img = Image.open(io.BytesIO(response.content))
        img = img.resize((1, 1))
        res = img.getpixel((0, 0))
        # Ensure it's not too dark
        r, g, b = res[0], res[1], res[2]
        if r + g + b < 100: # Too dark, boost it
            r, g, b = min(255, r+100), min(255, g+100), min(255, b+100)
        
        primary = f"rgb({r}, {g}, {b})"
        glow = f"rgba({r}, {g}, {b}, 0.5)"
        return primary, glow
    except:
        return "#ff4b2b", "rgba(255, 75, 43, 0.5)"

def sync_user_data():
    """Write current session state back to disk (called after mutations)."""
    if st.session_state.authenticated and 'user_username' in st.session_state:
        users = auth.load_users()
        uname = st.session_state.user_username
        if uname in users:
            users[uname]['name'] = st.session_state.user_profile['name']
            users[uname]['profile']['bio'] = st.session_state.user_profile['bio']
            users[uname]['profile']['photo_url'] = st.session_state.user_profile['photo_url']
            users[uname]['profile']['instagram_id'] = st.session_state.user_profile.get('instagram_id', '')
            users[uname]['wishlist'] = st.session_state.wishlist
            users[uname]['watched_list'] = st.session_state.watched_list
            auth.save_users(users)

@st.fragment(run_every=5)
def live_data_sync():
    """
    Runs every 5 seconds as a lightweight fragment (no full page re-run).
    Pulls fresh wishlist / watched / profile data from disk so that:
      - changes made in another tab/browser show up within ~5 s
      - the current user's data is always consistent with the server
    """
    if not st.session_state.get('authenticated') or not st.session_state.get('user_username'):
        return
    try:
        users = auth.load_users()
        uname = st.session_state.user_username
        if uname not in users:
            return
        fresh = users[uname]
        # Only update if something actually changed (avoids noisy rerenders)
        new_wish    = fresh.get('wishlist', [])
        new_watched = fresh.get('watched_list', [])
        if new_wish != st.session_state.wishlist:
            st.session_state.wishlist = new_wish
        if new_watched != st.session_state.watched_list:
            st.session_state.watched_list = new_watched
        # Sync profile name / bio if changed by another session
        fresh_profile = fresh.get('profile', {})
        for field in ('bio', 'photo_url', 'instagram_id'):
            if fresh_profile.get(field) != st.session_state.user_profile.get(field):
                st.session_state.user_profile[field] = fresh_profile.get(field, '')
        fresh_name = fresh.get('name', '')
        if fresh_name and fresh_name != st.session_state.user_profile.get('name'):
            st.session_state.user_profile['name'] = fresh_name
    except Exception:
        pass  # Never crash the UI from a background sync

def display_auth_page():
    if st.session_state.get('forgot_password_mode', False):
        display_forgot_password_page()
        return

    st.markdown("""
    <style>
    /* ─── Page Container — compact, no scroll ─────────────────────────── */
    .block-container {
        max-width: 460px !important;
        width: 100% !important;
        padding-top: 2vh !important;
        padding-bottom: 2vh !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        overflow-x: hidden !important;
    }

    /* ─── Hide Streamlit top chrome to save vertical space ───────────── */
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }

    /* ─── Glassmorphism Login Container ────────────────────────────────── */
    div.block-container > div > [data-testid="stVerticalBlock"] {
        background: rgba(10, 10, 15, 0.72) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        padding: 22px 28px !important;
        border-radius: 24px !important;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        animation: entranceCard 0.6s cubic-bezier(0.16, 1, 0.3, 1) both !important;
        transition: all 0.4s ease !important;
    }
    div.block-container > div > [data-testid="stVerticalBlock"]:hover {
        border: 1px solid rgba(255, 75, 43, 0.3) !important;
        box-shadow: 0 25px 60px rgba(255, 75, 43, 0.15),
                    0 20px 50px rgba(0, 0, 0, 0.7) !important;
    }

    /* Remove double-box for nested containers */
    div.block-container > div > [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        background: transparent !important;
        backdrop-filter: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        animation: none !important;
    }

    /* ─── Form Container Reset ────────────────────────────────────────── */
    div[data-testid="stForm"] {
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }

    /* ─── Tighten input label & widget gap ───────────────────────────── */
    .stTextInput { margin-bottom: -8px !important; }
    .stTextInput label { font-size: 0.82rem !important; margin-bottom: 2px !important; }
    p[style*="margin-top: -10px"] { margin-top: -6px !important; margin-bottom: 2px !important; }

    /* ─── Entrance Animation ──────────────────────────────────────────── */
    @keyframes entranceCard {
        0%   { opacity: 0; transform: translateY(30px) scale(0.97); }
        100% { opacity: 1; transform: translateY(0)   scale(1);    }
    }

    @keyframes shimmer {
        0%   { background-position: 0%   50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0%   50%; }
    }

    /* ─── Brand Header ────────────────────────────────────────────────── */
    .brand-title {
        font-size: 2.6rem !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #ff4b2b 0%, #ff416c 35%, #8a2be2 70%, #ff4b2b 100%) !important;
        background-size: 300% auto !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 4px !important;
        animation: shimmer 6s infinite linear !important;
        letter-spacing: -1.5px !important;
        text-align: center !important;
    }

    /* ─── Tabs Styling ───────────────────────────────────────────────── */
    [data-testid="stTabList"] {
        justify-content: center !important;
        gap: 12px !important;
        border-bottom: none !important;
        margin-bottom: 12px !important;
    }
    [data-testid="stTab"] button {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid transparent !important;
        border-radius: 30px !important;
        padding: 6px 20px !important;
        background: rgba(255, 255, 255, 0.03) !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    [data-testid="stTab"] button[aria-selected="true"] {
        color: white !important;
        background: rgba(255, 75, 43, 0.15) !important;
        border-color: rgba(255, 75, 43, 0.4) !important;
        box-shadow: 0 4px 12px rgba(255, 75, 43, 0.2) !important;
        transform: translateY(-1px) !important;
    }

    /* ─── Input Fields ───────────────────────────────────────────────── */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: white !important;
        padding: 8px 14px !important;
        font-size: 0.9rem !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2) !important;
    }
    .stTextInput input:focus {
        border-color: rgba(255, 75, 43, 0.8) !important;
        box-shadow: 0 0 12px rgba(255, 75, 43, 0.25),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }

    /* ─── Primary Submit Buttons ─────────────────────────────────────── */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #ff4b2b 0%, #ff416c 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        padding: 10px 20px !important;
        box-shadow: 0 6px 20px rgba(255, 75, 43, 0.3) !important;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
        margin-top: 8px !important;
        width: 100% !important;
    }
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 28px rgba(255, 75, 43, 0.45),
                    0 0 12px rgba(255, 75, 43, 0.2) !important;
        color: white !important;
    }
    .stFormSubmitButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }

    /* ─── Secondary Buttons ──────────────────────────────────────────── */
    .stButton > button {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        padding: 8px 16px !important;
        transition: all 0.3s ease !important;
        margin-top: 6px !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    logo_base64 = get_base64_image('logo.jpg')
    if logo_base64:
        st.markdown(f"""
        <div style='text-align:center; margin-bottom: 10px;'>
            <img src="{logo_base64}" style='width: 150px; border-radius: 16px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);'>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; margin-bottom: 10px;'>
            <h1 class="brand-title">NovaFlix</h1>
            <p style='color:#888; font-size:0.88rem; letter-spacing: 0.5px; text-align: center;'>Experience the future of cinema.</p>
        </div>
        """, unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with auth_tab1:
        with st.form("login_form", border=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if login_submit:
                success, result = auth.login(username, password)
                if success:
                    # ── Create persistent session token ──────────────────────
                    _token = session_manager.create_session(username)
                    st.session_state.authenticated    = True
                    st.session_state.session_token    = _token
                    st.session_state.user_username    = username
                    st.session_state.user_data        = result
                    st.session_state.user_profile     = result['profile']
                    st.session_state.user_profile['name'] = result['name']
                    st.session_state.wishlist         = result.get('wishlist', [])
                    st.session_state.watched_list     = result.get('watched_list', [])
                    # ── Persist token in browser localStorage + URL ──────────
                    st.markdown(f"""
                    <script>
                    (function() {{
                        localStorage.setItem('nf_session_token', '{_token}');
                        var url = new URL(window.location.href);
                        url.searchParams.set('token', '{_token}');
                        url.searchParams.set('page', 'Discover');
                        window.history.replaceState({{}}, '', url.toString());
                    }})();
                    </script>
                    """, unsafe_allow_html=True)
                    st.success(f"Welcome back, {result['name']}!")
                    st.rerun()
                else:
                    st.error(result)
        
        if st.button("Forgot Password?", key="forgot_pass_btn", use_container_width=True):
            st.session_state.forgot_password_mode = True
            st.rerun()

    with auth_tab2:
        import time
        if 'signup_step' not in st.session_state:
            st.session_state.signup_step = 'fill_details'

        if st.session_state.signup_step == 'fill_details':
            # Initialize inputs in session state if not present
            for key in ["s_name", "s_username", "s_email", "s_password", "s_confirm_password"]:
                if key not in st.session_state:
                    st.session_state[key] = ""

            with st.form("signup_details_form", border=False):
                new_name = st.text_input("Full Name", value=st.session_state.s_name, key="s_name_input", placeholder="e.g. Altaf Khan 👑")
                new_username = st.text_input("Choose Username (@handle)", value=st.session_state.s_username, key="s_username_input", placeholder="e.g. novaflix_team")
                new_email = st.text_input("Email Address", value=st.session_state.s_email, key="s_email_input", placeholder="e.g. example@gmail.com")
                new_password = st.text_input("Create Password", type="password", value=st.session_state.s_password, key="s_password_input")
                new_confirm_password = st.text_input("Confirm Password", type="password", value=st.session_state.s_confirm_password, key="s_confirm_password_input")
                
                st.session_state.s_name = new_name
                st.session_state.s_username = new_username.strip()
                st.session_state.s_email = new_email.strip()
                st.session_state.s_password = new_password
                st.session_state.s_confirm_password = new_confirm_password

                # ─── REAL-TIME VALIDATIONS ───────────────────────────────────
                all_valid = True

                # 1. Profile Name Validation
                if new_name:
                    if len(new_name) > 30:
                        st.markdown(f"<p style='color: #ff4b2b; font-size: 0.82rem; margin: -4px 0 2px;'>⚠️ Profile Name must be 30 characters or less.</p>", unsafe_allow_html=True)
                        all_valid = False
                    else:
                        st.markdown("<p style='color: #2bfa35; font-size: 0.82rem; margin: -4px 0 2px;'>✔️ Valid Profile Name.</p>", unsafe_allow_html=True)

                # 2. Username Validation
                if new_username:
                    valid_format, format_msg = auth.validate_username(new_username)
                    if not valid_format:
                        st.markdown(f"<p style='color: #ff4b2b; font-size: 0.82rem; margin: -4px 0 2px;'>⚠️ {format_msg}</p>", unsafe_allow_html=True)
                        all_valid = False
                    elif auth.load_users().get(new_username):
                        st.markdown("<p style='color: #ff4b2b; font-size: 0.82rem; margin: -4px 0 2px;'>⚠️ Username is already taken!</p>", unsafe_allow_html=True)
                        all_valid = False
                    else:
                        st.markdown("<p style='color: #2bfa35; font-size: 0.82rem; margin: -4px 0 2px;'>✔️ Username is unique and valid.</p>", unsafe_allow_html=True)

                # 3. Email Validation
                if new_email:
                    if '@' not in new_email or '.' not in new_email.split('@')[-1]:
                        st.markdown("<p style='color: #ff4b2b; font-size: 0.82rem; margin: -4px 0 2px;'>⚠️ Invalid email format.</p>", unsafe_allow_html=True)
                        all_valid = False
                    elif auth.is_email_registered(new_email):
                        st.markdown("<p style='color: #ff4b2b; font-size: 0.82rem; margin: -4px 0 2px;'>⚠️ Email address is already registered!</p>", unsafe_allow_html=True)
                        all_valid = False
                    else:
                        st.markdown("<p style='color: #2bfa35; font-size: 0.82rem; margin: -4px 0 2px;'>✔️ Email is valid and available.</p>", unsafe_allow_html=True)

                # 4. Password Strength Validation
                if new_password:
                    valid_strength, strength_msg = auth.validate_password_strength(new_password)
                    if not valid_strength:
                        st.markdown(f"<p style='color: #ff4b2b; font-size: 0.82rem; margin: -4px 0 2px;'>⚠️ {strength_msg}</p>", unsafe_allow_html=True)
                        all_valid = False
                    else:
                        st.markdown("<p style='color: #2bfa35; font-size: 0.82rem; margin: -4px 0 2px;'>✔️ Password strength is strong.</p>", unsafe_allow_html=True)

                # 5. Passwords Match Validation
                if new_password and new_confirm_password:
                    if new_password != new_confirm_password:
                        st.markdown("<p style='color: #ff4b2b; font-size: 0.82rem; margin: -4px 0 2px;'>⚠️ Passwords do not match.</p>", unsafe_allow_html=True)
                        all_valid = False
                    else:
                        st.markdown("<p style='color: #2bfa35; font-size: 0.82rem; margin: -4px 0 2px;'>✔️ Passwords match.</p>", unsafe_allow_html=True)

                submit = st.form_submit_button("Send Verification Code", use_container_width=True)

                if submit:
                    if not new_name or not new_username or not new_email or not new_password or not new_confirm_password:
                        st.error("Please fill in all fields!")
                    elif not all_valid:
                        st.error("Please resolve all validation errors before proceeding.")
                    else:
                        from processing import email_service
                        otp = email_service.generate_otp()
                        st.session_state.signup_otp = otp
                        st.session_state.signup_otp_sent_at = time.time()
                        st.session_state.signup_data = {
                            'username': new_username,
                            'name': new_name,
                            'email': new_email,
                            'password': new_password
                        }
                        
                        success, message = email_service.send_otp_email(new_email, otp)
                        if success:
                            st.success(f"Verification code sent to {new_email}!")
                            st.session_state.signup_step = 'verify_otp'
                            st.rerun()
                        elif message == "SMTP_NOT_CONFIGURED":
                            st.warning("Gmail credentials are not configured in secrets.toml (EMAIL_SENDER/EMAIL_PASSWORD).")
                            st.info(f"[Local Testing] Your verification code is: {otp}")
                            st.session_state.signup_step = 'verify_otp'
                            st.rerun()
                        else:
                            st.error(f"Failed to send email: {message}")

        elif st.session_state.signup_step == 'verify_otp':
            signup_email = st.session_state.signup_data['email']
            parts = signup_email.split('@')
            user_part = parts[0]
            masked_user = user_part[0] + '*' * (len(user_part) - 2) + user_part[-1] if len(user_part) > 2 else user_part[0] + '*'
            masked_email = f"{masked_user}@{parts[1]}"

            st.info(f"A 6-digit verification code has been sent to {masked_email}")

            elapsed = time.time() - st.session_state.signup_otp_sent_at
            is_expired = elapsed > 300
            
            if is_expired:
                st.error("⚠️ The verification code has expired (valid for 5 minutes). Please click 'Resend OTP'.")

            with st.form("verify_signup_otp_form", border=False):
                otp_input = st.text_input("Enter 6-Digit Code (OTP)", placeholder="e.g. 123456")
                submit = st.form_submit_button("Verify & Create Account", use_container_width=True)

                if submit:
                    if is_expired:
                        st.error("Verification code has expired! Please request a new one.")
                    elif not otp_input:
                        st.error("Please enter the verification code!")
                    elif otp_input.strip() != st.session_state.signup_otp:
                        st.error("Invalid verification code!")
                    else:
                        data = st.session_state.signup_data
                        success, msg = auth.signup(data['username'], data['name'], data['email'], data['password'])
                        if success:
                            st.success("Account created successfully! Please sign in on the Login tab.")
                            st.session_state.signup_step = 'fill_details'
                            for k in ["s_name", "s_username", "s_email", "s_password", "s_confirm_password", "signup_otp", "signup_otp_sent_at", "signup_data"]:
                                if k in st.session_state:
                                    del st.session_state[k]
                            st.rerun()
                        else:
                            st.error(msg)

            # Resend OTP Timer & Button
            elapsed = time.time() - st.session_state.signup_otp_sent_at
            remaining_resend = max(0, 30 - int(elapsed))

            col1, col2 = st.columns([1, 1])
            with col1:
                if remaining_resend > 0:
                    st.button(f"Resend OTP ({remaining_resend}s)", key="resend_otp_btn_disabled", disabled=True, use_container_width=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    if st.button("Resend OTP", key="resend_otp_btn", use_container_width=True):
                        from processing import email_service
                        otp = email_service.generate_otp()
                        st.session_state.signup_otp = otp
                        st.session_state.signup_otp_sent_at = time.time()
                        
                        success, message = email_service.send_otp_email(signup_email, otp)
                        if success:
                            st.success("A new verification code has been sent!")
                            st.rerun()
                        elif message == "SMTP_NOT_CONFIGURED":
                            st.warning("Gmail credentials are not configured in secrets.toml.")
                            st.info(f"[Local Testing] Your verification code is: {otp}")
                            st.rerun()
                        else:
                            st.error(f"Failed to send email: {message}")
            with col2:
                if st.button("← Edit Details", key="back_to_details_btn", use_container_width=True):
                    st.session_state.signup_step = 'fill_details'
                    st.rerun()

def main():
    if not st.session_state.authenticated:
        display_auth_page()
        return

    # 🎭 Dynamic Adaptive Theme
    p_color = st.session_state.get('primary_color', '#ff4b2b')
    g_color = st.session_state.get('glow_color', 'rgba(255, 75, 43, 0.5)')
    bg_img = st.session_state.get('bg_url')

    st.markdown(f"""
    <style>
    :root {{
        --primary-color: {p_color};
        --glow-color: {g_color};
    }}
    
    .stApp {{
        background: {f"url('{bg_img}')" if bg_img else "#080808"};
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        transition: all 1.2s ease-in-out;
    }}
    
    /* 20% visibility (0.8 dark overlay) + 60% blur (25px) */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background: {f"rgba(0,0,0,0.8)" if bg_img else "transparent"};
        backdrop-filter: {f"blur(25px)" if bg_img else "none"};
        z-index: -1;
        transition: all 1.2s ease-in-out;
    }}
    
    /* Dynamic Button Styling */
    div.stButton > button:first-child {{
        border: 1px solid var(--primary-color) !important;
        background: rgba(0,0,0,0.4) !important;
        color: white !important;
    }}
    div.stButton > button:first-child:hover {{
        background: var(--primary-color) !important;
        box-shadow: 0 0 20px var(--glow-color) !important;
    }}
    
    /* Dynamic Text & Borders */
    h1, h2, h3 {{ color: white !important; }}
    .metric-badge {{ border-left: 4px solid var(--primary-color) !important; }}
    
    /* Flashlight focus */
    .flashlight-overlay {{
        background: radial-gradient(600px at var(--mouse-x) var(--mouse-y), {g_color.replace('0.5', '0.15')}, transparent 80%);
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="flashlight-overlay"></div>', unsafe_allow_html=True)
    
    # 🎬 Fixed Top Center Logo
    logo_base64 = get_base64_image('logo.jpg')
    if logo_base64:
        st.markdown(f"""
        <style>
        .fixed-main-logo {{
            position: fixed;
            top: 5px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 999999;
            cursor: pointer;
            transition: transform 0.3s ease;
            pointer-events: auto;
        }}
        .fixed-main-logo:hover {{
            transform: translateX(-50%) scale(1.05);
        }}
        </style>
        <div class="fixed-main-logo" onclick="window.parent.location.reload()">
            <img src="{logo_base64}" style='height: 42px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5);'>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .fixed-main-logo {
            position: fixed;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            font-size: clamp(24px, 3vw, 34px);
            font-weight: 900;
            color: #ff4b2b;
            z-index: 999999;
            text-shadow: 0 4px 20px rgba(255, 75, 43, 0.7);
            font-family: 'Inter', sans-serif;
            letter-spacing: -1px;
            cursor: pointer;
            transition: transform 0.3s ease;
            pointer-events: auto;
        }
        .fixed-main-logo:hover {
            transform: translateX(-50%) scale(1.05);
        }
        </style>
        <div class="fixed-main-logo" onclick="window.parent.location.reload()">🎬 NovaFlix</div>
        """, unsafe_allow_html=True)

    pfp_url = st.session_state.user_profile.get('photo_url', 'https://www.pngall.com/wp-content/uploads/5/Profile-Avatar-PNG.png') if 'user_profile' in st.session_state else 'https://www.pngall.com/wp-content/uploads/5/Profile-Avatar-PNG.png'
    
    js_script = """
        <script>
        const doc = window.parent.document;
        // Flashlight effect
        doc.addEventListener("mousemove", (e) => {
            doc.documentElement.style.setProperty('--mouse-x', e.clientX + 'px');
            doc.documentElement.style.setProperty('--mouse-y', e.clientY + 'px');
        });
        
        // Force removal of Navy Backgrounds in Main Doc (Optimized for performance)
        const styleGlobalUI = () => {
            // Brute Force File Uploader
            const uploaders = doc.querySelectorAll('[data-testid="stFileUploader"]:not(.glass-styled)');
            uploaders.forEach(u => {
                u.style.background = 'transparent';
                u.style.backgroundColor = 'transparent';
                const children = u.querySelectorAll('*');
                children.forEach(c => {
                    c.style.backgroundColor = 'transparent';
                    if (c.tagName === 'SECTION') {
                        c.style.background = 'rgba(255,255,255,0.05)';
                        c.style.backdropFilter = 'blur(10px)';
                    }
                });
                u.classList.add('glass-styled');
            });
            
            // Target TextAreas, Inputs and Selectboxes (Ultra Brute Force)
            const inputs = doc.querySelectorAll('textarea:not(.glass-styled), input:not(.glass-styled), [data-baseweb="base-input"]:not(.glass-styled), [data-baseweb="textarea"]:not(.glass-styled), [data-baseweb="select"]:not(.glass-styled)');
            inputs.forEach(i => {
                i.style.setProperty('background', 'rgba(255, 255, 255, 0.05)', 'important');
                i.style.setProperty('background-color', 'rgba(255, 255, 255, 0.05)', 'important');
                i.style.setProperty('backdrop-filter', 'blur(15px)', 'important');
                
                // Climb up to parents and clear their bg
                let p = i.parentElement;
                for(let step=0; step<4; step++) {
                    if(p && !p.dataset.testid) {
                        p.style.setProperty('background-color', 'transparent', 'important');
                        p.style.setProperty('background', 'transparent', 'important');
                        p = p.parentElement;
                    }
                }
                i.classList.add('glass-styled');
            });

            // Target Buttons
            const allButtons = doc.querySelectorAll('button[data-testid^="stBaseButton"]:not(.glass-styled)');
            allButtons.forEach(b => {
                b.style.background = 'rgba(255, 255, 255, 0.08)';
                b.style.backgroundColor = 'rgba(255, 255, 255, 0.08)';
                b.style.backdropFilter = 'blur(12px)';
                b.style.border = '3.5px solid #ff4b2b'; // Thick 0.1cm-like border
                b.style.boxShadow = '0 0 20px rgba(255, 75, 43, 0.4)';
                b.style.borderRadius = '18px';
                b.style.fontWeight = '700';
                b.classList.add('glass-styled');
            });
        };
        styleGlobalUI();
        setInterval(styleGlobalUI, 10);

        // Inject animated text gradient and selectability into the Option Menu iframe
        const styleIframes = () => {
            const iframes = doc.querySelectorAll('iframe');
            iframes.forEach(iframe => {
                try {
                    const idoc = iframe.contentDocument || iframe.contentWindow.document;
                    if (idoc && idoc.querySelector('.nav-link') && !idoc.getElementById('custom-anim-style')) {
                        iframe.style.background = 'transparent';
                        if (iframe.parentElement) iframe.parentElement.style.background = 'transparent';
                        idoc.body.style.background = 'transparent';
                        idoc.documentElement.style.background = 'transparent';
                        
                        // Remove all href attributes so URLs don't get copied with the text
                        const allLinks = idoc.querySelectorAll('a');
                        allLinks.forEach(link => {
                            link.removeAttribute('href');
                        });

                        // 1. Ensure the Nav is a Flex Row
                        const nav = idoc.querySelector('.nav');
                        if (nav) {
                            nav.style.display = 'flex';
                            nav.style.flexDirection = 'row';
                            nav.style.alignItems = 'center';
                            nav.style.justifyContent = 'center';
                            nav.style.width = '100%';
                            nav.style.padding = '0 30px';
                            nav.style.position = 'relative';
                            
                            // 2. Inject Icons if not present
                            if (!idoc.getElementById('injected-icons')) {
                                const icons = idoc.createElement('div');
                                icons.id = 'injected-icons';
                                icons.style.cssText = 'font-size: 22px; color: white; display: flex; align-items: center; position: fixed; right: 30px; top: 50%; transform: translateY(-50%); z-index: 9999;';
                                
                                const profileSpan = idoc.createElement('span');
                                profileSpan.id = 'top-right-pfp';
                                profileSpan.innerHTML = '<img src="USER_PROFILE_URL" style="width: 28px; height: 28px; border-radius: 50%; object-fit: cover; border: 2px solid rgba(255,255,255,0.3);">';
                                profileSpan.title = 'Profile';
                                profileSpan.style.cssText = 'cursor:pointer; transition: all 0.3s; opacity: 0.8;';
                                profileSpan.onclick = () => {
                                    const tabs = Array.from(idoc.querySelectorAll('.nav-link'));
                                    const profileTab = tabs.find(el => el.innerText.toUpperCase().includes('PROFILE'));
                                    if(profileTab) profileTab.click();
                                };
                                profileSpan.onmouseover = () => profileSpan.style.transform = 'scale(1.2)';
                                profileSpan.onmouseout = () => profileSpan.style.transform = 'scale(1)';

                                icons.appendChild(profileSpan);
                                idoc.body.appendChild(icons);
                            }
                            
                            // 4. Force styles on all links
                            const links = idoc.querySelectorAll('.nav-link');
                            links.forEach(link => {
                                const text = link.innerText.toUpperCase();
                                link.style.borderRadius = '100px';
                                link.style.transition = 'all 0.3s ease';
                                link.style.margin = '0 5px';
                                link.style.whiteSpace = 'nowrap';
                                
                                if (text.includes('PROFILE')) {
                                    const topRightPfp = idoc.getElementById('top-right-pfp');
                                    if (!link.classList.contains('active')) {
                                        link.style.display = 'none';
                                        if (topRightPfp) topRightPfp.style.display = 'inline-block';
                                    } else {
                                        link.style.display = 'flex';
                                        if (topRightPfp) topRightPfp.style.display = 'none';
                                        if (!link.querySelector('img.pfp-in-tab')) {
                                            const icon = link.querySelector('i');
                                            if (icon) icon.style.display = 'none';
                                            const img = idoc.createElement('img');
                                            img.src = 'USER_PROFILE_URL';
                                            img.className = 'pfp-in-tab';
                                            img.style.cssText = 'width: 22px; height: 22px; border-radius: 50%; object-fit: cover; margin-right: 8px; border: 1.5px solid white;';
                                            link.insertBefore(img, link.firstChild);
                                        }
                                    }
                                } else {
                                    link.style.display = 'flex';
                                }
                                link.style.alignItems = 'center';
                                link.style.justifyContent = 'center';
                                link.style.textAlign = 'center';
                                link.style.height = '38px';
                                link.style.padding = '0 20px';
                                
                                if (link.classList.contains('active')) {
                                    link.style.background = 'rgba(46, 213, 115, 0.25)';
                                    link.style.color = '#2ed573';
                                    link.style.border = '2px solid #2ed573';
                                    link.style.fontWeight = '900';
                                    link.style.boxShadow = '0 0 15px rgba(46, 213, 115, 0.3)';
                                    link.style.transform = 'scale(1.05)';
                                } else {
                                    link.style.background = 'transparent';
                                    link.style.color = 'rgba(255, 255, 255, 0.65)';
                                    link.style.border = '1px solid transparent';
                                    link.style.fontWeight = '500';
                                    link.style.boxShadow = 'none';
                                    link.style.transform = 'scale(1)';
                                }
                            });
                        }

                        const style = idoc.createElement('style');
                        style.id = 'custom-anim-style';
                        style.innerHTML = `
                            body, html, .nav-link, span {
                                user-select: none !important;
                                -webkit-user-select: none !important;
                                -moz-user-select: none !important;
                                -ms-user-select: none !important;
                            }
                            .nav-link { 
                                text-transform: uppercase !important; 
                                letter-spacing: 0.8px !important;
                                font-size: 10.5px !important;
                                font-family: Inter, sans-serif !important;
                                white-space: nowrap !important;
                            }
                            .nav-link span {
                                width: 100% !important;
                                text-align: center !important;
                            }
                            .nav-link:hover:not(.active) {
                                background: rgba(255, 255, 255, 0.1) !important;
                                color: white !important;
                                transform: scale(1.05) !important;
                            }
                        `;
                        idoc.head.appendChild(style);
                    }
                } catch(e) {}
            });
        };
        styleIframes();
        setInterval(styleIframes, 10);
        </script>
        """.replace("USER_PROFILE_URL", pfp_url)

    components.html(js_script, height=0, width=0)

    if 'user_menu' not in st.session_state or st.session_state.user_menu == "":
        st.session_state.user_menu = 'Discover'

    if 'active_person_name' not in st.session_state:
        st.session_state.active_person_name = ""

    def initial_options():
        options = ['Discover', 'Movies', 'Profile']
        icons = ['stars', 'search', 'person']

        if st.session_state.get('last_recommended_movie'):
            options.append('Movie Details')
            icons.append('info-circle')

        if st.session_state.get('active_person_name'):
            options.append('Actor Details')
            icons.append('people')

        try:
            current_idx = options.index(st.session_state.user_menu)
        except ValueError:
            current_idx = 0
            st.session_state.user_menu = options[0]

        selected = streamlit_option_menu.option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            orientation="horizontal",
            default_index=current_idx,
            manual_select=current_idx,
            styles={
                "container": {
                    "background": "rgba(0, 0, 0, 0.6)",
                    "backdrop-filter": "blur(30px)",
                    "-webkit-backdrop-filter": "blur(30px)",
                    "border": "1px solid rgba(255, 255, 255, 0.12)",
                    "border-radius": "25px",
                    "padding": "0",
                    "margin": "0 auto 30px auto",
                    "box-shadow": "none",
                    "width": "fit-content", "max-width": "95%"
                },
                "icon": {"display": "none"}, 
                "nav-link": {
                    "font-family": 'Inter, sans-serif',
                    "font-size": "10.5px",
                    "letter-spacing": "0.8px",
                    "white-space": "nowrap",
                    "padding": "0 20px",
                    "height": "38px",
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "text-align": "center",
                    "border-radius": "100px",
                    "border": "1px solid transparent",
                    "color": "rgba(255, 255, 255, 0.9)",
                    "background": "transparent",
                    "font-weight": "500",
                    "margin": "0 5px",
                    "text-transform": "uppercase",
                    "transition": "all 0.3s ease"
                },
                "nav-link-selected": {
                    "background": "rgba(46, 213, 115, 0.25)",
                    "color": "#2ed573",
                    "font-weight": "900",
                    "box-shadow": "0 0 15px rgba(46, 213, 115, 0.3)",
                    "transform": "scale(1.05)",
                    "border-radius": "100px",
                    "border": "2px solid #2ed573"
                }
            }
        )
        
        if selected != st.session_state.user_menu:
            st.session_state.user_menu = selected
            # Persist page in URL so refresh restores position
            st.query_params['page'] = selected
            if st.session_state.get('session_token'):
                st.query_params['token'] = st.session_state.session_token
            st.rerun()

        if st.session_state.user_menu == 'Discover':
            recommend_display()
        elif st.session_state.user_menu == 'Movies':
            paging_movies()
        elif st.session_state.user_menu == 'Profile':
            display_profile()
        elif st.session_state.user_menu == 'Movie Details':
            display_movie_details()
        elif st.session_state.user_menu == 'Actor Details':
            display_person_details()



    def display_wishlist():
        # Minimal spacing at the top instead of a heavy header
        st.markdown("<br>", unsafe_allow_html=True)

        if not st.session_state.get('wishlist'):
            st.markdown("""
            <div style="background: rgba(0,0,0,0.45); padding: 60px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.08); text-align: center; margin-top: 20px;">
                <div style="font-size: 4rem; margin-bottom: 20px;">🍿</div>
                <h2 style="color: white; margin-bottom: 10px;">Your Wishlist is Empty</h2>
                <p style="color: #888; font-size: 1.1rem;">Explore the library and heart your favorite movies to see them here.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        wishlist_movies = list(set(st.session_state['wishlist'])) # Ensure unique
        
        # Display in a clean grid
        for row_start in range(0, len(wishlist_movies), 5):
            row_movies = wishlist_movies[row_start : row_start + 5]
            cols = st.columns(5)
            for idx, movie in enumerate(row_movies):
                poster, rating, year = preprocess.fetch_posters_v2(movie)
                with cols[idx]:
                    # Premium Glow Card with Fixed Aspect Ratio
                    st.markdown(f"""
                    <div class="movie-glow-card" style="aspect-ratio: 2/3; position: relative;">
                        <img src="{poster if poster else 'https://via.placeholder.com/300x450'}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                        <div class="card-rating-overlay" style="background: rgba(0,0,0,0.85); color: #f5c518; border: 1px solid rgba(245,197,24,0.3);">⭐ {rating}</div>
                    </div>
                    <div style="height: 12px;"></div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(movie[:18] + '..' if len(movie) > 18 else movie, key=f"btn_wish_v3_{movie}_{idx}", use_container_width=True):
                        st.session_state['last_recommended_movie'] = movie
                        st.session_state.user_menu = 'Movie Details'
                        st.rerun()
                    
                    st.markdown(f"<div style='text-align: center; color: #ff4b2b; font-size: 0.9rem; font-weight: 700; margin-bottom: 5px;'>📅 {year}</div>", unsafe_allow_html=True)
                    
                    if st.button("🗑️ Remove", key=f"rm_wish_v3_{movie}_{idx}", use_container_width=True):
                        st.session_state['wishlist'].remove(movie)
                        sync_user_data()
                        st.toast(f"Removed **{movie}** from wishlist.")
                        st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)

    def display_watched_list():
        st.markdown("<br>", unsafe_allow_html=True)
        if not st.session_state.get('watched_list'):
            st.markdown("""
            <div style="background: rgba(0,0,0,0.45); padding: 40px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.08); text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 15px;">🎬</div>
                <h3 style="color: white;">Your Watched Library is Empty</h3>
                <p style="color: #888;">Mark movies as 'Watched' to keep track of your cinema journey.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        watched_movies = list(set(st.session_state['watched_list']))
        for row_start in range(0, len(watched_movies), 5):
            row_movies = watched_movies[row_start : row_start + 5]
            cols = st.columns(5)
            for idx, movie in enumerate(row_movies):
                poster, rating, year = preprocess.fetch_posters_v2(movie)
                with cols[idx]:
                    st.markdown(f"""
                    <div class="movie-glow-card" style="aspect-ratio: 2/3; position: relative; border-color: #2ed573;">
                        <img src="{poster if poster else 'https://via.placeholder.com/300x450'}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                        <div class="card-rating-overlay" style="background: rgba(46,213,115,0.9); color: white;">✅ Watched</div>
                    </div>
                    <div style="height: 12px;"></div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(movie[:15] + '..' if len(movie) > 15 else movie, key=f"btn_watch_v3_{movie}_{idx}", use_container_width=True):
                        st.session_state['last_recommended_movie'] = movie
                        st.session_state.user_menu = 'Movie Details'
                        st.rerun()
                    
                    if st.button("🗑️ Remove", key=f"rm_watch_v3_{movie}_{idx}", use_container_width=True):
                        st.session_state['watched_list'].remove(movie)
                        sync_user_data()
                        st.toast(f"Removed from Watched list.")
                        st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    def recommend_display():
        st.title('Movie Recommender System')

        # State persistence logic
        if 'last_recommended_movie' not in st.session_state:
            st.session_state.last_recommended_movie = ""
        if 'trigger_recommend' not in st.session_state:
            st.session_state.trigger_recommend = False

        # Callback: fires automatically when user picks a movie (select or Enter)
        def on_movie_select():
            chosen = st.session_state.get('_rec_selectbox', '')
            if chosen:
                st.session_state.last_recommended_movie = chosen
                st.session_state.trigger_recommend = True

        # Maintain last selection index
        movie_list = new_df['title'].values.tolist()
        try:
            default_idx = movie_list.index(st.session_state.last_recommended_movie)
        except ValueError:
            default_idx = None

        st.selectbox(
            '🔍 Choose a movie to find similar recommendations:',
            new_df['title'].values,
            index=default_idx,
            placeholder="Type or select a movie you love (e.g., Avatar)...",
            key='_rec_selectbox',
            on_change=on_movie_select
        )

        selected_movie_name = st.session_state.last_recommended_movie

        if st.session_state.trigger_recommend and selected_movie_name:
            selected_movie_name = st.session_state.last_recommended_movie


            # SKELETON UI
            placeholder = st.empty()
            with placeholder.container():
                st.header("Scanning for the best matches... 🔍")
                for _ in range(4): # 4 rows of recommendations
                    cols = st.columns(5)
                    for col in cols:
                        with col:
                            st.markdown('<div class="skeleton-box" style="height:350px;"></div>', unsafe_allow_html=True)
                            st.markdown('<div class="skeleton-box" style="height:20px; width:80%; margin-top:10px;"></div>', unsafe_allow_html=True)
                            st.markdown('<div class="skeleton-box" style="height:15px; width:60%; margin-top:5px; margin-bottom: 20px;"></div>', unsafe_allow_html=True)

            # Pre-fetch elements so they are cached before drawing
            try:
                preprocess.recommend(new_df, selected_movie_name, r'Files/similarity_tags_tags.pkl')
                preprocess.recommend(new_df, selected_movie_name, r'Files/similarity_tags_genres.pkl')
                preprocess.recommend(new_df, selected_movie_name, r'Files/similarity_tags_tcast.pkl')
                preprocess.recommend(new_df, selected_movie_name, r'Files/similarity_tags_tcrew.pkl')
            except Exception:
                pass
            # Clear Skeleton
            placeholder.empty()

            # DRAW ACTUAL RESULTS
            # 🔥 MAIN (BEST)
            st.header("Recommended Movies")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_tags.pkl')

            # 🎞️ FRANCHISE (Conditional)
            franchise_movies = get_franchise_movies(selected_movie_name, movies, include_self=True)
            if franchise_movies and len(franchise_movies) > 1:
                st.header("🎞️ The Franchise Collection")
                cols = st.columns(min(5, len(franchise_movies)))
                for i, mov in enumerate(franchise_movies[:5]):
                    poster, rating, year = preprocess.fetch_posters_v2(mov)
                    
                    # Local Data Lookup
                    m_info = movies2[movies2['title'] == mov]
                    if not m_info.empty:
                        if rating == "N/A" or rating == "No Rating":
                            rating = str(round(float(m_info['vote_average'].values[0]), 1))
                        if year == "Unknown" or year == "N/A":
                            rd = m_info['release_date'].values[0]
                            year = str(rd)[:4] if rd and str(rd) != 'nan' else "N/A"

                    with cols[i]:
                        html = f"""
                        <div class="movie-poster-container">
                            <img src="{poster if poster else 'https://via.placeholder.com/300x450'}" class="main-poster" />
                        </div>
                        """
                        st.markdown(html, unsafe_allow_html=True)
                        if st.button(mov, key=f"btn_fran_rec_{mov}_{i}", use_container_width=True):
                            st.session_state['last_recommended_movie'] = mov
                            st.session_state.user_menu = 'Movie Details'
                            st.rerun()
                        st.markdown(f"<div style='text-align: center; color: #aaa; font-size: 0.85rem;'>⭐ {rating} | 📅 {year}</div>", unsafe_allow_html=True)

            # 🎭 GENRE
            st.header("🎭 Based on Genre")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_genres.pkl')

            # 👥 CAST / DIRECTOR
            st.header("👥 Based on Cast")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_tcast.pkl')

            # 🎬 SAME DIRECTOR
            st.header("🎬 Directed by the Same Creator")
            recommendation_tags(new_df, selected_movie_name, r'Files/similarity_tags_tcrew.pkl')

            st.success("Recommendations ready ✅")

    def recommendation_tags(new_df, selected_movie_name, pickle_file_path):

        # Check if movie is in local DB or we need live data
        is_local = selected_movie_name in new_df['title'].values
        
        if is_local:
            movies, posters, ratings, years = preprocess.recommend(new_df, selected_movie_name, pickle_file_path)
        else:
            # Internet Connected Recommendation
            with st.spinner("🌐 Connecting to AI for live recommendations..."):
                live_titles = preprocess.fetch_live_recommendations(selected_movie_name)
                movies, posters, ratings, years = [], [], [], []
                for lt in live_titles:
                    p, r, y = preprocess.fetch_posters_v2(lt)
                    movies.append(lt)
                    posters.append(p)
                    ratings.append(r)
                    years.append(y)

        rec_movies = []
        rec_posters = []
        rec_ratings = []
        rec_years = []

        for i, j in enumerate(movies):
            if len(rec_movies) == 15:
                break
            if j not in displayed:
                rec_movies.append(j)
                rec_posters.append(posters[i])
                rec_ratings.append(ratings[i])
                rec_years.append(years[i])
                displayed.append(j)

        if not rec_movies:
            return

        cols = st.columns(len(rec_movies))

        for i in range(len(rec_movies)):
            with cols[i]:
                poster = rec_posters[i] if rec_posters[i] else "https://via.placeholder.com/300x450"
                rating = rec_ratings[i] if rec_ratings[i] != "N/A" else "No Rating"
                year = rec_years[i] if rec_years[i] != "N/A" else "Unknown"
                
                # Fetch real data from local database if OMDb failed
                movie_info = movies2[movies2['title'] == rec_movies[i]]
                if not movie_info.empty:
                    if rating == "No Rating" or rating == "N/A":
                        rating = str(round(float(movie_info['vote_average'].values[0]), 1))
                    if year == "Unknown" or year == "N/A":
                        rel_date = movie_info['release_date'].values[0]
                        year = str(rel_date)[:4] if rel_date and str(rel_date) != 'nan' else "N/A"

                primary_provider = preprocess.get_primary_provider(rec_movies[i])

                html = f"""
                <div class="movie-poster-container">
                    <img src="{poster}" class="main-poster" />
                    <img src="{primary_provider['logo']}" class="provider-logo-overlay" title="Watch on {primary_provider['name']}" />
                </div>
                """
                st.markdown(html, unsafe_allow_html=True)
                if st.button(rec_movies[i], key=f"btn_rec_{rec_movies[i]}_{pickle_file_path[-10:]}", use_container_width=True):
                    st.session_state['last_recommended_movie'] = rec_movies[i]
                    st.session_state.user_menu = 'Movie Details'
                    st.rerun()
                st.markdown(f"<div style='text-align: center; color: #aaa; font-size: 0.85rem;'>⭐ {rating} | 📅 {year}</div>", unsafe_allow_html=True)

    def render_cinematic_movie_view(selected_movie_name):
        info = preprocess.get_details(selected_movie_name)
        poster_url = info[0] if info[0] else "https://via.placeholder.com/300x450"
        
        # Update Adaptive Theme
        st.session_state.bg_url = poster_url
        p, g = get_adaptive_colors(poster_url)
        st.session_state.primary_color = p
        st.session_state.glow_color = g

        # 🎬 Full Screen Cinematic Hero
        st.markdown(f"""
        <style>
        .cinematic-hero {{
            position: relative; width: 100%; min-height: 500px;
            background: rgba(0, 0, 0, 0.55);
            border-radius: 25px;
            padding: 40px; margin-bottom: 30px; display: flex; gap: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(20px); animation: fadeIn 0.8s ease-out;
        }}
        .hero-poster {{ flex: 0 0 320px; height: 480px; border-radius: 20px; object-fit: cover; border: 1px solid rgba(255,255,255,0.2); }}
        .hero-content {{ flex: 1; }}
        </style>
        <div class="cinematic-hero">
            <img src="{poster_url}" class="hero-poster" />
            <div class="hero-content">
                <h1 style="color: white; font-size: 3.5em; margin-bottom: 5px;">{selected_movie_name}</h1>
                <p style="color: #ff4b2b; font-size: 1.2em; font-weight: 600; margin-bottom: 20px;">{str(info[4])[:4] if info[4] else "N/A"} • {format_runtime(info[6])} • {", ".join(info[2]) if info[2] else "N/A"}</p>
                <div style="background: rgba(0,0,0,0.4); padding: 25px; border-radius: 18px; border-left: 6px solid #ff4b2b; margin-bottom: 25px;">
                    <h3 style="color: #ff4b2b; margin-top: 0; margin-bottom: 10px; font-size: 1.2em; text-transform: uppercase;">🎬 Film Summary</h3>
                    <p style="color: #eee; font-size: 1.15em; line-height: 1.7; font-style: italic;">"{info[3]}"</p>
                </div>
                <div style="display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 25px;">
                    <div class="metric-badge" style="background: rgba(245, 197, 24, 0.2); border: 1px solid rgba(245, 197, 24, 0.4);">
                        <span style="color: #f5c518; font-weight: 900; margin-right: 5px;">IMDb</span> 
                        <strong style="color: white; font-size: 1.1em;">{info[8]}</strong>
                        <span style="color: #aaa; font-size: 0.8rem; margin-left: 8px;">({format_number(info[9])} votes)</span>
                    </div>
                    <div class="metric-badge" style="background: rgba(43, 255, 136, 0.15);"><span style="color: #2bff88;">📈</span> <strong>{format_currency(info[5])}</strong> Revenue</div>
                    <div class="metric-badge" style="background: rgba(0,0,0,0.3);"><span style="color: #bbb;">💰</span> {format_currency(info[1])} Budget</div>
                </div>
        """, unsafe_allow_html=True)
        
        # Wishlist & Watched Buttons
        w1, w2 = st.columns(2)
        with w1:
            if selected_movie_name in st.session_state['wishlist']:
                st.button("💖 Wishlist", disabled=True, key=f"wished_details_{selected_movie_name}", use_container_width=True)
            else:
                if st.button("❤️ Wishlist", key=f"wish_details_{selected_movie_name}", use_container_width=True):
                    st.session_state['wishlist'].append(selected_movie_name)
                    sync_user_data()
                    st.toast(f"**{selected_movie_name}** added to Wishlist! 🎉")
                    st.rerun()
        with w2:
            if selected_movie_name in st.session_state['watched_list']:
                st.button("✅ Watched", disabled=True, key=f"watched_details_{selected_movie_name}", use_container_width=True)
            else:
                if st.button("🎬 Watched", key=f"watch_details_{selected_movie_name}", use_container_width=True):
                    st.session_state['watched_list'].append(selected_movie_name)
                    if selected_movie_name in st.session_state['wishlist']:
                        st.session_state['wishlist'].remove(selected_movie_name)
                    sync_user_data()
                    st.toast(f"**{selected_movie_name}** marked as Watched! 🍿")
                    st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

        # 💎 STREAM ON (App Icon Style - Direct Deep-Links)
        search_query = selected_movie_name.replace(' ', '%20')
        STREAM_PROVIDERS = [
            {"name": "Netflix", "domain": "netflix.com", "url": f"https://www.netflix.com/search?q={search_query}"},
            {"name": "Hotstar", "domain": "hotstar.com", "url": f"https://www.hotstar.com/in/search?q={search_query}"},
            {"name": "Prime Video", "domain": "primevideo.com", "url": f"https://www.primevideo.com/search?phrase={search_query}"},
            {"name": "Max", "domain": "max.com", "url": f"https://www.max.com/search?q={search_query}"},
            {"name": "Apple TV", "domain": "tv.apple.com", "url": f"https://tv.apple.com/search/{search_query}"},
            {"name": "YouTube", "domain": "youtube.com", "url": f"https://www.youtube.com/results?search_query={search_query}"}
        ]
        
        icons_html = "".join([
            f'<a href="{p["url"]}" target="_blank" style="text-decoration: none;">'
            f'<img src="https://www.google.com/s2/favicons?domain={p["domain"]}&sz=128" style="width: 38px; height: 38px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.15); margin-right: 10px; transition: all 0.3s ease;" '
            f'onmouseover="this.style.transform=\'translateY(-5px) scale(1.15)\'; this.style.borderColor=\'#ff4b2b\';" '
            f'onmouseout="this.style.transform=\'none\'; this.style.borderColor=\'rgba(255,255,255,0.15)\';" title="Search on {p["name"]}">'
            f'</a>' for p in STREAM_PROVIDERS
        ])

        st.markdown(f"""
        <div style="margin-top: 30px; padding: 12px 20px; background: rgba(0,0,0,0.4); border-radius: 20px; border: 1px solid rgba(255,255,255,0.08); display: flex; align-items: center; gap: 15px; width: fit-content;">
            <span style="color: #ff4b2b; font-size: 0.85rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; white-space: nowrap;">Stream on</span>
            <div style="display: flex; align-items: center; flex-wrap: nowrap;">
                {icons_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 🎬 DIRECTOR SPOTLIGHT
        dir_name = info[12] if isinstance(info[12], str) else info[12][0] if info[12] else "N/A"
        if dir_name != "N/A":
            dir_bio, dir_img = preprocess.get_person_details(dir_name)
            dir_extra = preprocess.get_person_extra_details(dir_name)
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.5); border-radius: 30px; padding: 40px; border: 1px solid rgba(255,255,255,0.1); margin-top: 40px;">
                <div style="display: flex; gap: 50px; flex-wrap: wrap;">
                    <div style="flex: 0 0 300px;"><img src="{dir_img}" style="width: 300px; height: 450px; border-radius: 20px; object-fit: cover;"></div>
                    <div style="flex: 1; min-width: 400px;">
                        <h1 style="color: white; font-size: 3em; margin: 0;">{dir_name}</h1>
                        <p style="color: #ff4b2b; letter-spacing: 2px;">DIRECTING EXCELLENCE</p>
                        <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.2); padding: 20px; border-radius: 20px; margin: 20px 0;">
                            <div><span style="color:#ff4b2b; font-size:0.7rem;">DOB</span><br><b>{dir_extra['dob']}</b></div>
                            <div><span style="color:#ff4b2b; font-size:0.7rem;">COUNTRY</span><br><b>{dir_extra['country']}</b></div>
                            <div>
                                <span style="color:#ff4b2b; font-size:0.7rem;">SOCIAL</span><br>
                                {f'<a href="https://instagram.com/{dir_extra["insta"]}" target="_blank" style="text-decoration:none;"><img src="https://www.google.com/s2/favicons?domain=instagram.com&sz=128" style="width:20px; vertical-align:middle; margin-right:5px; border-radius:5px;"><b>@{dir_extra["insta"]}</b></a>' if dir_extra['insta'] else '<b>N/A</b>'}
                            </div>
                        </div>
                        <div style="background: rgba(0,0,0,0.35); padding: 20px; border-radius: 15px; border-left: 4px solid #ff4b2b;">
                            <p style="color: #aaa; font-size: 1rem; line-height: 1.6;">{dir_bio[:1000]}...</p>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 🎬 TRAILER & SCREENSHOTS
        trailer_url = get_trailer_url(selected_movie_name)
        if trailer_url:
            st.markdown("### 🎬 Movie Trailer")
            st.video(trailer_url)

        # 🎭 CAST GALLERY (Swipe Right)
        st.markdown("### 🎭 Top Cast")
        cast_list = info[11]
        if cast_list:
            c_cols = st.columns(min(len(cast_list), 6))
            for idx, actor in enumerate(cast_list[:6]):
                actor_img = preprocess.fetch_person_image(actor)
                with c_cols[idx]:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <img src="{actor_img}" style="width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 2px solid #ff4b2b; margin-bottom: 10px;">
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(actor, key=f"btn_cast_new_{actor}_{idx}", use_container_width=True):
                        st.session_state.active_person_name = actor
                        st.session_state.user_menu = 'Actor Details'
                        st.rerun()

        # 🎞️ FRANCHISE (Swipe Right)
        sequels = get_franchise_movies(selected_movie_name, movies, include_self=False)
        if sequels:
            st.markdown("---")
            st.markdown("### 🎬 Franchise & Sequels")
            seq_cols = st.columns(len(sequels))
            for idx, seq in enumerate(sequels):
                seq_poster, seq_rating, seq_year = preprocess.fetch_posters_v2(seq)
                with seq_cols[idx]:
                    st.image(seq_poster if seq_poster else "https://via.placeholder.com/300x450", use_container_width=True)
                    if st.button(seq, key=f"btn_seq_new_{seq}_{idx}"):
                        # For franchise, we set as last recommended so details tab updates
                        st.session_state['last_recommended_movie'] = seq
                        st.session_state['active_modal_movie'] = None # Close modal if opening from modal
                        st.rerun()
                    st.markdown(f"<div style='text-align: center; font-size: 0.8rem;'>⭐ {seq_rating} | 📅 {seq_year}</div>", unsafe_allow_html=True)

    def render_cinematic_cast_view(actor_name):
        bio, img_url = preprocess.get_person_details(actor_name)
        extra_info = preprocess.get_person_extra_details(actor_name)
        
        # 🎬 Master Cast Hero Design (Ambient Background Edition)
        st.markdown(f"""
<style>
.cast-card-hero {{
    position: relative; width: 100%; border-radius: 35px;
    background: rgba(255, 255, 255, 0.03); 
    backdrop-filter: blur(15px);
    overflow: hidden;
    display: flex; margin-bottom: 40px; box-shadow: 0 40px 100px rgba(0,0,0,0.5);
    min-height: 480px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}}
.cast-card-hero::before {{
    content: ''; position: absolute; inset: 0;
    background: url('{img_url}') center center; background-size: cover;
    filter: blur(40px) brightness(0.15); z-index: 1;
}}
.cast-left-info {{ flex: 1.1; padding: 60px; position: relative; z-index: 5; display: flex; flex-direction: column; justify-content: center; }}
.cast-right-img {{ 
    flex: 0.9; 
    background: url('{img_url}') center 15%; 
    background-size: cover; 
    position: relative; z-index: 5;
    min-height: 480px;
}}
.cast-right-img::after {{
    content: ''; position: absolute; inset: 0; 
    background: linear-gradient(to right, rgba(0,0,0,0.2) 0%, transparent 100%);
}}
.pill-badge {{
    display: inline-block; border: 1.5px solid #ff4b2b; color: white;
    background: rgba(255,75,43,0.1); border-radius: 20px;
    padding: 8px 22px; margin-right: 14px; margin-bottom: 14px;
    font-size: 0.9rem; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.8px;
    box-shadow: 0 4px 15px rgba(255,75,43,0.15);
}}
</style>
<div class="cast-card-hero">
<div class="cast-left-info">
<h1 style="color: white; font-size: 5.5em; font-weight: 900; line-height: 0.9; margin: 0; letter-spacing: -2px;">
{actor_name.upper()} <span style="background:#5b7fff; color:white; border-radius:50%; padding:4px 10px; font-size:24px; vertical-align:middle;">✓</span>
</h1>
<div style="margin-top: 45px;">
<div class="pill-badge">Born: {extra_info['dob']}</div>
<div class="pill-badge">Age: {extra_info['age']}</div>
<div class="pill-badge">Origin: {extra_info['country']}</div>
{f'<a href="https://instagram.com/{extra_info["insta"]}" target="_blank" style="text-decoration:none;"><div class="pill-badge">📸 @{extra_info["insta"]}</div></a>' if extra_info['insta'] else ''}
</div>
</div>
<div class="cast-right-img"></div>
</div>
""", unsafe_allow_html=True)

        # Known For Section
        st.markdown("<h2 style='margin-bottom: 25px;'>KNOWN FOR</h2>", unsafe_allow_html=True)
        known_movies = preprocess.get_movies_by_person(actor_name)
        if known_movies:
            k_cols = st.columns(min(6, len(known_movies)))
            for idx, k_movie in enumerate(known_movies[:6]):
                poster, rating, year = preprocess.fetch_posters_v2(k_movie)
                with k_cols[idx]:
                    # Fixed Aspect Ratio Container
                    st.markdown(f"""
                    <div class="movie-glow-card" style="aspect-ratio: 2/3; position: relative;">
                        <img src="{poster if poster else 'https://via.placeholder.com/300x450'}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                        <div class="card-rating-overlay" style="background: rgba(0,0,0,0.8); border: 1px solid #f5c518; color: #f5c518;">⭐ {rating}</div>
                    </div>
                    <div style="height: 10px;"></div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(k_movie[:18] + '..' if len(k_movie) > 18 else k_movie, key=f"btn_known_v5_{k_movie}_{idx}", use_container_width=True):
                        st.session_state['last_recommended_movie'] = k_movie
                        st.session_state.user_menu = 'Movie Details'
                        st.rerun()
                    
                    st.markdown(f"<div style='text-align: center; color: #ff4b2b; font-size: 0.9rem; font-weight: 700;'>📅 {year}</div>", unsafe_allow_html=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # 📖 Full-Width Horizontal Biography Section
        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px); margin-bottom: 30px;">
            <h3 style="color: var(--primary-color); margin-top: 0; margin-bottom: 25px; font-size: 1.8rem; letter-spacing: 2px; border-bottom: 2px solid var(--glow-color); padding-bottom: 15px; width: fit-content;">📖 BIOGRAPHY</h3>
            <p style="color: #ddd; line-height: 1.9; font-size: 1.1rem; text-align: justify;">{bio if bio else 'Biography not available.'}</p>
        </div>
        """, unsafe_allow_html=True)

        # 🎞️ Full-Width Filmography Section
        film_html = "".join([
            f'<div style="padding: 15px 25px; background: rgba(255,255,255,0.02); border-radius: 15px; border: 1px solid rgba(255,255,255,0.05); color: #eee; font-size: 1.1rem; display: flex; align-items: center; gap: 15px; min-width: 250px;">'
            f'<span style="color: #ff4b2b;">🎬</span> {m}'
            f'</div>' for m in known_movies[:15]
        ]) if known_movies else '<p style="color: #888;">No filmography data available.</p>'

        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.05); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
            <h3 style="color: var(--primary-color); margin-top: 0; margin-bottom: 25px; font-size: 1.8rem; letter-spacing: 2px; border-bottom: 2px solid var(--glow-color); padding-bottom: 15px; width: fit-content;">🎞️ FILMOGRAPHY</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                {film_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    def display_privacy_safety():
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); 
                    padding: 30px; border-radius: 25px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 30px; backdrop-filter: blur(15px);">
            <h1 style="color: var(--primary-color); margin: 0; font-size: 2rem;">🛡️ Privacy & Safety Hub</h1>
            <p style="color: #aaa;">Manage your data, visibility, and account security.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 👁️ Visibility")
            st.session_state.privacy_settings['public_profile'] = st.toggle(
                "Public Profile", 
                value=st.session_state.privacy_settings['public_profile'],
                help="Allow others to see your wishlist and movie ratings."
            )
            st.session_state.privacy_settings['activity_status'] = st.toggle(
                "Show Activity Status", 
                value=st.session_state.privacy_settings['activity_status'],
                help="Show when you are online."
            )
            
            st.markdown("### 📊 Data & Personalization")
            st.session_state.privacy_settings['personalized_recs'] = st.toggle(
                "Personalized Recommendations", 
                value=st.session_state.privacy_settings['personalized_recs'],
                help="Use my watch history to improve suggestions."
            )
            st.session_state.privacy_settings['allow_analytics'] = st.toggle(
                "Allow Analytics", 
                value=st.session_state.privacy_settings['allow_analytics'],
                help="Share anonymous usage data to help improve NovaFlix."
            )

        with col2:
            st.markdown("### 🔒 Security")
            
            # Functional Change Password
            if st.button("Change Password", use_container_width=True):
                st.session_state['show_pw_form'] = not st.session_state.get('show_pw_form', False)

            if st.session_state.get('show_pw_form'):
                with st.form("pw_change_form"):
                    old_pw = st.text_input("Current Password", type="password")
                    new_pw = st.text_input("New Password", type="password")
                    conf_pw = st.text_input("Confirm New Password", type="password")
                    if st.form_submit_button("Update Password", use_container_width=True):
                        if new_pw != conf_pw:
                            st.error("New passwords do not match!")
                        elif len(new_pw) < 8:
                            st.error("Password should be at least 8 characters!")
                        else:
                            success, msg = auth.update_password(st.session_state.user_username, old_pw, new_pw)
                            if success:
                                st.success(msg)
                                st.session_state['show_pw_form'] = False
                                st.rerun()
                            else:
                                st.error(msg)

            if st.button("Two-Factor Authentication (2FA)", use_container_width=True):
                st.info("2FA setup: Please scan the QR code in your authenticator app (Simulated).")
                st.image("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=NovaFlix-2FA-Demo", width=150)
            
            if st.button("Manage Login Sessions", use_container_width=True):
                st.write("Current active sessions:")
                st.code("• Windows - Delhi, India (This device)\n• Android - Mumbai, India (2 days ago)")
                st.button("Log out of all other devices", type="primary")

        st.markdown("---")
        st.markdown("### 🗑️ Danger Zone")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🗑️ Clear Wishlist", use_container_width=True):
                st.session_state.wishlist = []
                sync_user_data()
                st.toast("Wishlist cleared.")
                st.rerun()
        with c2:
            if st.button("🎬 Clear Watched", use_container_width=True):
                st.session_state.watched_list = []
                sync_user_data()
                st.toast("Watched History cleared.")
                st.rerun()
        with c3:
            if st.button("🛑 Deactivate Account", use_container_width=True):
                st.warning("Are you sure? This action is irreversible.")
                if st.button("Confirm Deactivation", type="primary"):
                    st.error("Account deactivated. Refresh to start over.")

        if st.button("⬅️ Back to Profile", use_container_width=True):
            st.session_state.privacy_mode = False
            st.rerun()

    def display_profile():
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ── Privacy Mode Logic ─────────────────────────────────────────────
        if st.session_state.privacy_mode:
            display_privacy_safety()
            return

        # ── Edit Profile Logic ─────────────────────────────────────────────
        if st.session_state.edit_profile_mode:
            st.markdown("### ✏️ Edit Your Profile")
            
            # 📸 Photo Upload & Crop (Outside form for instant reaction)
            uploaded_photo = st.file_uploader("Choose a profile photo (PNG, JPG)", type=['png', 'jpg', 'jpeg'])
            
            if uploaded_photo:
                img = Image.open(uploaded_photo)
                st.markdown("#### ✂️ Crop Your Photo")
                # Real-time crop
                cropped_img_obj = st_cropper(img, realtime_update=True, box_color='#ff4b2b', aspect_ratio=(1,1))
                st.session_state['temp_cropped_img'] = cropped_img_obj
                st.markdown("Preview:")
                st.image(cropped_img_obj, width=120)
            else:
                st.session_state['temp_cropped_img'] = None

            with st.form("edit_profile_form"):
                new_name = st.text_input("Name", value=st.session_state.user_profile.get('name', 'User'))
                new_bio = st.text_area("Bio", value=st.session_state.user_profile.get('bio', ''), height=100)
                new_insta = st.text_input("Instagram ID (without @)", value=st.session_state.user_profile.get('instagram_id', ''))
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    save_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)
                with col_cancel:
                    cancel_btn = st.form_submit_button("✖ Cancel", use_container_width=True)
                
                if save_btn:
                    # Save cropped image if exists
                    if st.session_state.get('temp_cropped_img') is not None:
                        try:
                            import io
                            buf = io.BytesIO()
                            st.session_state['temp_cropped_img'].save(buf, format="PNG")
                            bytes_data = buf.getvalue()
                            b64_img = base64.b64encode(bytes_data).decode()
                            st.session_state.user_profile['photo_url'] = f"data:image/png;base64,{b64_img}"
                        except Exception as e:
                            st.error(f"Error saving cropped image: {e}")
                    
                    st.session_state.user_profile['name'] = new_name
                    st.session_state.user_profile['bio'] = new_bio
                    st.session_state.user_profile['instagram_id'] = new_insta.replace('@', '').strip()
                    
                    # Update backend
                    sync_user_data()

                    st.session_state.edit_profile_mode = False
                    st.session_state['temp_cropped_img'] = None
                    st.toast("Profile updated successfully! 🎉")
                    st.rerun()
                
                if cancel_btn:
                    st.session_state.edit_profile_mode = False
                    st.session_state['temp_cropped_img'] = None
                    st.rerun()
            return

        # ── Profile View ───────────────────────────────────────────────────
        # Premium Profile Header
        photo = st.session_state.user_profile.get('photo_url', 'https://via.placeholder.com/150')
        st.markdown(f"""
<div style="background: rgba(255, 255, 255, 0.05); padding: 40px; border-radius: 30px; border: 1px solid rgba(255, 255, 255, 0.1); text-align: center; margin-bottom: 40px; backdrop-filter: blur(20px);">
<div style="width: 140px; height: 140px; background: url('{photo}') center center; background-size: cover; border-radius: 50%; margin: 0 auto 20px; border: 3px solid var(--primary-color); box-shadow: 0 0 20px var(--glow-color);"></div>
<h1 style="margin: 0; font-weight: 900; letter-spacing: -1px; color: white; -webkit-text-stroke: 0.5px lightskyblue; text-shadow: 0 0 12px rgba(135, 206, 250, 0.5);">{st.session_state.user_profile['name']}</h1>
{f'<div style="margin-top: 10px;"><a href="https://instagram.com/{st.session_state.user_profile["instagram_id"]}" target="_blank" style="text-decoration:none; color: #ff416c; font-weight: 700; font-size: 1.1rem; display: flex; align-items: center; justify-content: center; gap: 8px;"><img src="https://www.google.com/s2/favicons?domain=instagram.com&sz=128" style="width:20px; border-radius: 5px;">@{st.session_state.user_profile["instagram_id"]}</a></div>' if st.session_state.user_profile.get('instagram_id') else ''}
<p style="color: #aaa; margin-top: 15px; font-style: italic;">"{st.session_state.user_profile['bio']}"</p>
<div style="display: flex; justify-content: center; gap: 40px; margin-top: 30px;">
<div style="text-align: center;">
<div style="font-size: 1.5rem; font-weight: 800; color: #ff4b2b;">{len(st.session_state.get('wishlist', []))}</div>
<div style="font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px;">Wishlist</div>
</div>
<div style="text-align: center;">
<div style="font-size: 1.5rem; font-weight: 800; color: #ff4b2b;">{len(st.session_state.get('watched_list', []))}</div>
<div style="font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px;">Watched</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ⚙️ Account Settings")
            if st.button("✏️ Edit Profile", use_container_width=True, key="edit_profile_btn"):
                st.session_state.edit_profile_mode = True
                st.rerun()
            if st.button("🛡️ Privacy & Safety", use_container_width=True, key="privacy_btn"):
                st.session_state.privacy_mode = True
                st.rerun()
            if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                # Destroy server-side token
                session_manager.destroy_session(st.session_state.get('session_token', ''))
                # Clear browser localStorage token + URL params
                st.markdown("""
                <script>
                (function() {
                    localStorage.removeItem('nf_session_token');
                    var url = new URL(window.location.href);
                    url.searchParams.delete('token');
                    url.searchParams.delete('page');
                    window.history.replaceState({}, '', url.toString());
                })();
                </script>
                """, unsafe_allow_html=True)
                st.session_state.authenticated  = False
                st.session_state.session_token  = ''
                st.session_state.user_data      = None
                st.session_state.user_menu      = ''
                st.query_params.clear()
                st.rerun()
            
        with col2:
            st.markdown("### 🔔 Notifications")
            st.checkbox("Email me about new releases", value=True, key="notify_email")
            st.checkbox("Push notifications for recommendations", value=True, key="notify_push")
            st.checkbox("Weekly movie digest", value=False, key="notify_digest")
            
        st.markdown("---")
        
        tab_wish, tab_watched = st.tabs(["💖 Wishlist", "🎬 Watched History"])
        
        with tab_wish:
            display_wishlist()
            
        with tab_watched:
            display_watched_list()

    def display_watched_list():
        st.markdown("<br>", unsafe_allow_html=True)
        if not st.session_state.get('watched_list'):
            st.markdown("""
            <div style="background: rgba(255,255,255,0.03); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.08); text-align: center; margin-top: 20px;">
                <div style="font-size: 4rem; margin-bottom: 20px;">🎬</div>
                <h2 style="color: white; margin-bottom: 10px;">Watched History is Empty</h2>
                <p style="color: #888; font-size: 1.1rem;">Movies you mark as 'Watched' will appear here.</p>
            </div>
            """, unsafe_allow_html=True)
            return

        watched_movies = list(set(st.session_state['watched_list']))
        for row_start in range(0, len(watched_movies), 5):
            row_movies = watched_movies[row_start : row_start + 5]
            cols = st.columns(5)
            for idx, movie in enumerate(row_movies):
                poster, rating, year = preprocess.fetch_posters_v2(movie)
                with cols[idx]:
                    st.markdown(f"""
                    <div class="movie-glow-card" style="aspect-ratio: 2/3; position: relative;">
                        <img src="{poster if poster else 'https://via.placeholder.com/300x450'}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                        <div class="card-rating-overlay" style="background: rgba(0,0,0,0.85); color: #f5c518; border: 1px solid rgba(245,197,24,0.3);">⭐ {rating}</div>
                    </div>
                    <div style="height: 12px;"></div>
                    """, unsafe_allow_html=True)
                    if st.button(movie[:18] + '..' if len(movie) > 18 else movie, key=f"btn_watched_v1_{movie}_{idx}", use_container_width=True):
                        st.session_state['last_recommended_movie'] = movie
                        st.session_state.user_menu = 'Movie Details'
                        st.rerun()
                    if st.button("🗑️ Remove", key=f"rm_watched_v1_{movie}_{idx}", use_container_width=True):
                        st.session_state['watched_list'].remove(movie)
                        st.rerun()

    def display_movie_details():
        if 'last_recommended_movie' in st.session_state and st.session_state.last_recommended_movie:
            st.markdown("""
            <style>
            .md-close-marker { display: none; }
            div:has(> .md-close-marker) + div {
                height: 0px !important; min-height: 0px !important;
                display: flex !important; justify-content: flex-end !important;
                z-index: 9999 !important; position: relative !important;
            }
            div:has(> .md-close-marker) + div > div {
                transform: translate(-30px, 30px) !important;
            }
            div:has(> .md-close-marker) + div button {
                border-radius: 50% !important;
                width: 45px !important; height: 45px !important; padding: 0 !important;
                background: rgba(255,75,43,0.9) !important; color: white !important;
                border: 2px solid white !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
                transition: transform 0.3s ease !important;
            }
            div:has(> .md-close-marker) + div button:hover {
                transform: scale(1.15) rotate(90deg) !important;
            }
            </style>
            <div class="md-close-marker"></div>
            """, unsafe_allow_html=True)
            
            if st.button("✖", key="close_md_btn", help="Close Movie Details"):
                st.session_state.last_recommended_movie = ""
                st.session_state.active_person_name = ""
                st.session_state.user_menu = 'Discover'
                st.rerun()
                
            render_cinematic_movie_view(st.session_state.last_recommended_movie)
        else:
            st.info("ℹ️ No movie selected yet! Head over to the **✨ Discover Movies** tab and search for your favorite movie to see its details here.")

    def paging_movies():
        # ── Init state ────────────────────────────────────────────────────
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ''
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'search_selected_id' not in st.session_state:
            st.session_state.search_selected_id = None

        # ── Search form ────────────────────────────────────────────────────
        st.markdown("""
        <div class='animate-delay-1' style='text-align:center; margin-bottom: 10px;'>
            <h1 style='font-size: clamp(2rem,3vw,3rem); font-weight:900; background: linear-gradient(135deg,#ff4b2b,#ff6b35,#ffaa35); -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
                🔍 Search & Explore
            </h1>
            <p style='color:#aaa; font-size:1rem; margin-top:-10px;'>Search across millions of movies or browse the library</p>
        </div>
        """, unsafe_allow_html=True)

        col_inp, col_btn = st.columns([4, 1])
        with col_inp:
            query = st.text_input(
                "", 
                value=st.session_state.search_query,
                placeholder="🔎  Type a movie name… e.g. Oppenheimer, Avengers, KGF",
                key="live_search_input",
                label_visibility="collapsed"
            )
        with col_btn:
            do_search = st.button("🔍 Search", use_container_width=True, key="btn_live_search")

        if do_search and query.strip():
            st.session_state.search_query = query.strip()
            with st.spinner("Searching across all movies..."):
                st.session_state.search_results = preprocess.omdb_search_movies(query.strip())

        # ── If a search result movie is selected, show the high-end Cinematic Detail View ────
        if st.session_state.search_selected_id:
            movie_data = preprocess.omdb_get_full_details(imdb_id=st.session_state.search_selected_id)
            if movie_data:
                title = movie_data.get('Title', 'Unknown')
                
                # Back Button to return to search results
                st.markdown("""
                <style>
                .back-btn-container { position: sticky; top: 10px; z-index: 1000; margin-bottom: 20px; }
                </style>
                """, unsafe_allow_html=True)
                
                if st.button("⬅️ Back to Search Results", key="back_to_search"):
                    st.session_state.search_selected_id = None
                    st.rerun()

                # Reuse the high-end Cinematic View
                st.session_state['last_recommended_movie'] = title
                display_movie_details()
                return

        # ── OMDB Search Results ────────────────────────────────────────────
        if st.session_state.search_results:
            st.markdown(f"<p style='color:#aaa;margin:8px 0 18px;'>Found <strong style='color:#ff4b2b;'>{len(st.session_state.search_results)}</strong> results for \"{st.session_state.search_query}\"</p>", unsafe_allow_html=True)
            r_cols = st.columns(5)
            for idx, mv in enumerate(st.session_state.search_results[:10]):
                with r_cols[idx % 5]:
                    p = mv.get('Poster', preprocess.FALLBACK_POSTER)
                    if not p or p == 'N/A': p = preprocess.FALLBACK_POSTER
                    st.markdown(f"""
                        <div style="width: 100%; aspect-ratio: 2/3; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.4); margin-bottom: 8px;">
                            <img src="{p}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                        </div>
                        <div style='text-align:center;color:#888;font-size:0.8rem;margin-top:4px;'>📅 {mv.get('Year','')}</div>
                    """, unsafe_allow_html=True)
                    if st.button(mv.get('Title','?'), key=f"sr_{mv.get('imdbID','')}_{idx}", use_container_width=True):
                        st.session_state.search_selected_id = mv.get('imdbID','')
                        st.rerun()
            st.markdown("---")
        elif st.session_state.search_query:
            st.warning("No results found. Try a different spelling or movie name.")
            st.markdown("---")
        else:
            # ── Latest Releases (Only show when no active search) ──────────────
            st.markdown("""
            <div class='animate-delay-2' style='margin: 10px 0 20px;'>
                <h2 style='font-size:1.8rem; font-weight:800; background: linear-gradient(135deg,#ff4b2b,#ffaa35);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent; display:inline;'>
                    🔥 Latest Releases
                </h2>
            </div>
            """, unsafe_allow_html=True)

            latest = preprocess.get_latest_movies()

            if latest:
                for row_start in range(0, min(10, len(latest)), 5):
                    row = latest[row_start:row_start+5]
                    row_cols = st.columns(5)
                    for ci, mv in enumerate(row):
                        with row_cols[ci]:
                            poster = mv.get('Poster', preprocess.FALLBACK_POSTER)
                            if not poster or poster == 'N/A': poster = preprocess.FALLBACK_POSTER
                            mv_title  = mv.get('Title', 'Unknown')
                            mv_id     = mv.get('imdbID', '')
                            st.markdown(f"""
                                <div style="width: 100%; aspect-ratio: 2/3; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.4); margin-bottom: 8px;">
                                    <img src="{poster}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                                </div>
                            """, unsafe_allow_html=True)
                            if st.button(mv_title, key=f"latest_{mv_id}_{row_start}_{ci}", use_container_width=True):
                                st.session_state.search_selected_id = mv_id
                                st.rerun()
            st.markdown("---")

        st.markdown("<p style='color:#aaa; font-size:1.5rem; font-weight:800; text-align:center;'>📚 Classic Library</p>", unsafe_allow_html=True)

        # ── Classic Library Browser ────────────────────────────────────────

        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            selected_year = st.text_input("📅 Filter by Year (e.g. 2012)", max_chars=4)
            if selected_year: selected_year = selected_year.strip()
        with filter_col2:
            letters = ["All"] + list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            selected_letter = st.selectbox("🔤 Starts with...", letters)

        if selected_year and not selected_year.isdigit():
            st.warning("Year must contain digits only!"); selected_year = ""

        filtered_movies = movies.copy()
        if selected_year:
            filtered_movies = filtered_movies[filtered_movies['release_date'].astype(str).str.contains(selected_year, na=False)]
        if selected_letter != "All":
            filtered_movies = filtered_movies[filtered_movies['title'].str.upper().str.startswith(selected_letter)]

        st.divider()
        if filtered_movies.empty:
            st.warning("No movies found matching your filters."); return

        # ── Professional Numbered Pagination (Image 2 Style) ─────────────────
        st.markdown("""
        <style>
            div[data-testid="stHorizontalBlock"] {
                justify-content: center !important;
                align-items: center !important;
                gap: 2px !important;
            }
            div[data-testid="stHorizontalBlock"] > div {
                min-width: 0px !important;
                flex: 0 0 auto !important;
                padding: 0 1px !important;
            }
            div[data-testid="stHorizontalBlock"] button {
                padding: 0.2rem 0.6rem !important;
                font-size: 0.75rem !important;
                height: 28px !important;
                min-width: 36px !important;
                width: auto !important;
            }
            div[data-testid="stHorizontalBlock"] button[kind="primary"] {
                background-color: #76a021 !important;
                color: white !important;
                border: none !important;
                font-weight: bold !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        total_pages = max(1, (len(filtered_movies) - 1) // 20 + 1)
        current_page = (st.session_state['movie_number'] // 20) + 1
        
        # Determine range (max 5 numbers to fit on one line)
        start_pg = max(1, min(current_page - 2, total_pages - 4))
        if start_pg < 1: start_pg = 1
        end_pg = min(total_pages, start_pg + 4)
        
        # Columns: Prev (0.6), Numbers (5 * 0.5), Next (0.6) - compact spacing
        total_cols = 2 + (end_pg - start_pg + 1)
        p_cols = st.columns(total_cols, gap="small")
        
        with p_cols[0]:
            if st.button("← Prev", disabled=(current_page == 1), use_container_width=False):
                st.session_state['movie_number'] -= 20
                st.rerun()
        
        for i, pg_num in enumerate(range(start_pg, end_pg + 1)):
            with p_cols[i+1]:
                is_active = (pg_num == current_page)
                if is_active:
                    if st.button(str(pg_num), key=f"pg_{pg_num}", type="primary", use_container_width=False):
                        pass
                else:
                    if st.button(str(pg_num), key=f"pg_{pg_num}", use_container_width=False):
                        st.session_state['movie_number'] = (pg_num - 1) * 20
                        st.rerun()

        with p_cols[-1]:
            if st.button("Next →", disabled=(current_page == total_pages), use_container_width=False):
                st.session_state['movie_number'] += 20
                st.rerun()
        
        st.markdown(f"<div style='text-align:center; color:#888; font-size:0.9rem; margin-top:10px; font-weight:bold;'>Page {current_page} selected</div>", unsafe_allow_html=True)

        display_all_movies(st.session_state['movie_number'], filtered_movies)

    def display_all_movies(start, filtered_movies):
        # Show 20 movies (4 rows of 5)
        for row_idx in range(4):
            row_start = start + (row_idx * 5)
            if row_start >= len(filtered_movies):
                break
            
            row_movies = filtered_movies.iloc[row_start : row_start + 5]
            cols = st.columns(5)
            
            for idx, (_, movie_row) in enumerate(row_movies.iterrows()):
                movie_name = movie_row['title']
                poster, rating, year = preprocess.fetch_posters_v2(movie_name)
                primary_provider = preprocess.get_primary_provider(movie_name)

                with cols[idx]:
                    poster_url = poster if poster else "https://via.placeholder.com/300x450"
                    # Fixed Aspect Ratio with Blue Top Border
                    html = f"""
                    <div style="position: relative; border-radius: 12px; overflow: hidden; margin-bottom: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); aspect-ratio: 2/3; border-top: 4px solid #5b7fff;">
                        <img src="{poster_url}" style="width: 100%; height: 100%; object-fit: cover; display: block;" />
                        <img src="{primary_provider['logo']}" style="position: absolute; bottom: 8px; right: 8px; width: 35px; height: 35px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.8); z-index: 10;" title="Watch on {primary_provider['name']}" />
                        <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: #f5c518; padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; border: 1px solid rgba(245,197,24,0.3); z-index: 10;">⭐ {rating}</div>
                    </div>
                    """
                    st.markdown(html, unsafe_allow_html=True)
                    if st.button(movie_name[:18] + '..' if len(movie_name) > 18 else movie_name, key=f"btn_all_v2_{movie_name}_{row_start}_{idx}", use_container_width=True):
                        st.session_state['last_recommended_movie'] = movie_name
                        st.session_state.user_menu = 'Movie Details'
                        st.rerun()
                    st.markdown(f"<div style='text-align: center; color: #aaa; font-size: 0.8rem;'>📅 {year}</div>", unsafe_allow_html=True)

    def display_person_details():
        if 'active_person_name' in st.session_state and st.session_state.active_person_name:
            st.markdown("""
            <style>
            .ad-close-marker { display: none; }
            div:has(> .ad-close-marker) + div {
                height: 0px !important; min-height: 0px !important;
                display: flex !important; justify-content: flex-end !important;
                z-index: 9999 !important; position: relative !important;
            }
            div:has(> .ad-close-marker) + div > div {
                transform: translate(-30px, 30px) !important;
            }
            div:has(> .ad-close-marker) + div button {
                border-radius: 50% !important;
                width: 45px !important; height: 45px !important; padding: 0 !important;
                background: rgba(255,75,43,0.9) !important; color: white !important;
                border: 2px solid white !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
                transition: transform 0.3s ease !important;
            }
            div:has(> .ad-close-marker) + div button:hover {
                transform: scale(1.15) rotate(90deg) !important;
            }
            </style>
            <div class="ad-close-marker"></div>
            """, unsafe_allow_html=True)
            
            if st.button("✖", key="close_ad_btn", help="Close Actor Details"):
                st.session_state.active_person_name = ""
                st.session_state.user_menu = 'Movie Details'
                st.rerun()
                
            render_cinematic_cast_view(st.session_state.active_person_name)
        else:
            st.info("ℹ️ No person selected yet! Head over to a movie's details and click on a cast member to see their biography here.")

    with Main() as bot:
        bot.main_()
        new_df, movies, movies2 = bot.getter()

        # ── Live data sync (polls disk every 5 s, no full re-run) ──────────
        live_data_sync()

        # Always render initial_options to keep the header visible
        initial_options()


if __name__ == '__main__':
    main()