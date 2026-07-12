
import pickle
import streamlit as st
import requests
import pandas as pd
import sqlite3

# ---------------- CONFIG ----------------
API_KEY = "7b0137f83d762a597cbf727479fb5e0f"

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- SESSION ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "recommended" not in st.session_state:
    st.session_state.recommended = []

# ---------------- DATABASE ----------------
conn = sqlite3.connect("wishlist.db", check_same_thread=False)
c = conn.cursor()
c.execute(
    """
CREATE TABLE IF NOT EXISTS wishlist (
    movie_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL
)
"""
)
conn.commit()

# ---------------- THEME TOGGLE ----------------
_, col2 = st.columns([9, 1])
with col2:
   if st.button("🌙 / ☀", key="theme_toggle_1"):
        st.session_state.theme = (
            "dark" if st.session_state.theme == "light" else "light"
        )

# ---------------- THEME COLORS ----------------
bg_dark = "https://images.unsplash.com/photo-1524985069026-dd778a71c7b4"
bg_light = "https://images.unsplash.com/photo-1542204165-65bf26472b9b"

if st.session_state.theme == "dark":
    BACKGROUND = bg_dark
    TEXT = "#ffffff"
    CARD_BG = "rgba(0,0,0,.85)"
    BORDER = "#ff1e1e"
    GLOW = "0 0 40px rgba(255,0,0,.8)"
else:
    BACKGROUND = bg_light
    TEXT = "#111111"
    CARD_BG = "rgba(255,255,255,.9)"
    BORDER = "#ff3b3b"
    GLOW = "none"

# ---------------- CSS ----------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Poppins', sans-serif;
}}

#MainMenu, footer, header {{visibility:hidden;}}
[data-testid="stSidebar"] {{display:none;}}

.stApp {{
    background:
        linear-gradient(rgba(0,0,0,.55), rgba(0,0,0,.85)),
        url('{BACKGROUND}');
    background-size: cover;
    background-attachment: fixed;
    color: {TEXT};
}}

.section {{
    background: {CARD_BG};
    border-radius: 22px;
    padding: 28px;
    margin-bottom: 30px;
    border: 2px solid {BORDER};
    box-shadow: {GLOW};
}}

.main-title {{
    text-align: center;
    font-size: 46px;
    font-weight: 800;
    color: #ff2b2b;
    text-shadow: 0 0 18px rgba(255,0,0,.7);
}}

.stTextInput input,
.stSelectbox select {{
    background: rgba(0,0,0,.9) !important;
    border: 2px solid #ff2b2b !important;
    color: white !important;
    border-radius: 14px !important;
}}

.stButton button {{
    background: linear-gradient(135deg, #b30000, #ff0000);
    color: white;
    border-radius: 18px;
    font-weight: 800;
    padding: 12px 26px;
    transition: all .35s ease;
    box-shadow: 0 0 15px rgba(255,0,0,.4);
}}

.stButton button:hover {{
    transform: scale(1.08);
    box-shadow: 0 0 40px rgba(255,0,0,.9);
}}

.movie-card {{
    width: 165px;
    height: 250px;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 15px 45px rgba(0,0,0,.9);
    transition: .35s;
}}

.movie-card:hover {{
    transform: scale(1.15);
    box-shadow: 0 0 45px rgba(255,0,0,.85);
}}

.movie-card img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
}}

.movie-title {{
    text-align: center;
    margin-top: 6px;
    font-weight: 600;
}}

.wishlist-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(0,0,0,.9);
    padding: 12px 18px;
    border-radius: 14px;
    border-left: 5px solid #ff2b2b;
    margin-bottom: 10px;
    font-weight: 600;
}}

@media (max-width: 768px) {{
    .movie-card {{ width: 130px; height: 200px; }}
    .main-title {{ font-size: 34px; }}
}}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------- TITLE ----------------
st.markdown(
    """
<div class="section">
    <div class="main-title">🎬 Movie Recommendation System</div>
</div>
""",
    unsafe_allow_html=True,
)


# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    movies = pickle.load(open("artifacts/movies.pkl", "rb"))
    similarity = pickle.load(open("artifacts/similarity.pkl", "rb"))
    return pd.DataFrame(movies), similarity


movies, similarity = load_data()


# ---------------- POSTER ----------------
@st.cache_data(show_spinner=False)
def poster(mid):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{mid}?api_key={API_KEY}"
    ).json()
    return "https://image.tmdb.org/t/p/w500" + str(data.get("poster_path", ""))


# ---------------- RECOMMEND ----------------
def recommend(movie):
    idx = movies[movies["title"] == movie].index[0]
    scores = similarity[idx]
    rec = sorted(list(enumerate(scores)), key=lambda x: x[1], reverse=True)[1:11]
    return [(movies.iloc[i[0]].title, movies.iloc[i[0]].movie_id) for i in rec]


# ---------------- SEARCH ----------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("🎯 Choose a Movie")

movie = st.selectbox(
    "🎬 Movie Name",
    movies["title"].sort_values().values,
    key="movie_select_1"
)

if st.button("🔥 Get Recommendations"):
    st.session_state.recommended = recommend(movie)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RECOMMENDATIONS ----------------
if st.session_state.recommended:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("🔥 Recommended Movies")

    for r in range(2):
        cols = st.columns(5)
        for col, (name, mid) in zip(
            cols, st.session_state.recommended[r * 5 : (r + 1) * 5]
        ):
            with col:
                st.markdown(
                    f"""
                <div class="movie-card">
                    <img src="{poster(mid)}">
                </div>
                <div class="movie-title">{name}</div>
                """,
                    unsafe_allow_html=True,
                )

                if st.button("💾 Add to Wishlist", key=f"add_{mid}"):
                    c.execute(
                        "INSERT OR IGNORE INTO wishlist (movie_id, title) VALUES (?,?)",
                        (mid, name),
                    )
                    conn.commit()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- WISHLIST ----------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("💾 Your Wishlist")

rows = c.execute("SELECT movie_id, title FROM wishlist").fetchall()

if rows:
    for mid, title in rows:
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(
                f"<div class='wishlist-row'>🎬 {title}</div>", unsafe_allow_html=True
            )
        with col2:
            if st.button("❌", key=f"del_{mid}"):
                c.execute("DELETE FROM wishlist WHERE movie_id=?", (mid,))
                conn.commit()
else:
    st.write("📭 Wishlist empty")

st.markdown("</div>", unsafe_allow_html=True)

import pickle
import streamlit as st
import requests
import pandas as pd
import sqlite3

# ---------------- CONFIG ----------------
API_KEY = "7b0137f83d762a597cbf727479fb5e0f"
