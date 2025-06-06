# 📄 Fichier : app.py

try:
    import streamlit as st
    import tempfile
    import os
    import io
    import matplotlib.pyplot as plt
    from utils.dxf_reader import load_dxf, get_dxf_perimeter_and_holes, plot_dxf, modify_dxf
    from streamlit_drawable_canvas import st_canvas
    import math
    import base64
    import json
except ModuleNotFoundError as e:
    raise ImportError("Ce script nécessite les bibliothèques `streamlit` et `streamlit-drawable-canvas`. Veuillez les installer avec 'pip install streamlit streamlit-drawable-canvas'") from e

st.set_page_config(page_title="PartLab – DXF Lab Creator", layout="wide")

# ============================
# 🌗 Choix du thème (Dark/Light)
# ============================
theme = st.sidebar.selectbox("🎨 Thème", ["Sombre", "Clair"])
if theme == "Clair":
    st.markdown("""
        <style>
        body { background-color: #ffffff; color: #000000; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body { background-color: #0e1117; color: #ffffff; }
        </style>
    """, unsafe_allow_html=True)

# ============================
# 🛡️ Authentification
# ============================
USERS = {
    "admin": {"password": "adminpass", "role": "admin"},
    "invite": {"password": "invitepass", "role": "invite"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.title("🔐 Connexion à PartLab")
    username = st.text_input("Identifiant")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Connexion", key="login_button"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success("Connexion réussie ✅")
            st.rerun()
        else:
            st.error("Identifiants incorrects ❌")
    st.stop()

if st.sidebar.button("🔓 Se déconnecter", key="logout_sidebar"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# ============================
# ✅ Interface principale avec onglets
# ============================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo_arcanum.webp", width=100)
with col2:
    st.title(f"PartLab – Bienvenue {st.session_state.username}")
    st.caption(f"Rôle : {st.session_state.role.upper()}")

# 🔀 Onglets principaux avec animations
onglets = st.tabs(["🖌️ Dessiner ✏️", "➕ Ajouter DXF ✨", "📂 Analyser DXF 🔎", "🛠️ Options ✨", "👤 Mon Profil 💼", "🏪 Test matériaux ⚖️"])

# === Mise à jour Onglet 1 : Dessiner avec mesure ===
with onglets[0]:
    st.header("🖌️ Zone de dessin avec mesure")
    st.markdown("Dessinez des formes et mesurez les distances.")

    with st.expander("Paramètres du canvas"):
        stroke_width = st.slider("🌌 Épaisseur du trait :", 1, 10, 3)
        bg_color = st.color_picker("🎨 Couleur de fond :", "#FFFFFF")
        drawing_mode = st.selectbox(
            "📝 Mode de dessin :", ("freedraw", "line", "rect", "circle", "transform")
        )

    canvas_result = st_canvas(
        fill_color="#00000000",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color=bg_color,
        height=500,
        drawing_mode=drawing_mode,
        key="canvas_zone1",
    )

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if drawing_mode == "line" and len(objects) >= 1:
            shape = objects[-1]
            x1, y1 = shape["x1"], shape["y1"]
            x2, y2 = shape["x2"], shape["y2"]
            distance_px = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            distance_mm = distance_px * 0.264583
            st.info(f"🔹 Distance mesurée : `{distance_mm:.2f} mm`")

        # ✨ Export JSON / SVG brut
        st.download_button("📂 Exporter JSON brut", json.dumps(canvas_result.json_data), file_name="dessin.json")

    # 🔧 Bouton pour tout effacer (recharge la page)
    if st.button("🔄 Effacer le dessin"):
        st.experimental_rerun()
