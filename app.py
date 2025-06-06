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

# 🔒 Masquer menu/partage Streamlit
st.markdown("""
    <style>
    #MainMenu, header, footer {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# ============================
# 🌗 Thème Synthwave + clair/sombre
# ============================
theme = st.sidebar.selectbox("🎨 Thème", ["Sombre", "Clair", "Synthwave 🌅"], key="theme_selector")

if theme == "Clair":
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to bottom right, #ffffff, #eeeeee);
            color: #000000;
        }
        </style>
    """, unsafe_allow_html=True)
elif theme == "Synthwave 🌅":
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to bottom right, #0f0c29, #302b63, #24243e);
            color: #f8f8f8;
            font-family: 'Orbitron', sans-serif;
        }
        .stButton>button {
            background: linear-gradient(to right, #ff416c, #ff4b2b);
            color: white;
            font-weight: bold;
            border-radius: 12px;
            transition: all 0.3s ease-in-out;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0px 0px 15px rgba(255, 65, 108, 0.9);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(to right, #fc466b, #3f5efb);
            color: white;
            font-weight: bold;
            box-shadow: 0 0 10px #fc466b;
        }
        h1, h2, h3, h4 {
            text-shadow: 0 0 5px #ff6ec4, 0 0 10px #7873f5;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to bottom right, #1f1f1f, #2a2a2a);
            color: #f0f0f0;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================
# 🔐 Authentification
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
    username = st.text_input("Identifiant", key="username")
    password = st.text_input("Mot de passe", type="password", key="password")
    if st.button("Connexion", key="login_btn"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.update({
                "logged_in": True,
                "username": username,
                "role": user["role"]
            })
            st.rerun()
        else:
            st.error("Identifiants incorrects ❌")
    st.stop()

if st.sidebar.button("🔓 Se déconnecter", key="logout_btn"):
    st.session_state.update({
        "logged_in": False,
        "username": "",
        "role": ""
    })
    st.rerun()

# ============================
# ✅ Interface principale
# ============================
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo_arcanum.webp", width=100)
with col2:
    st.markdown(f"""
    <h1 style='font-size: 2.2em;'>🎨 PartLab – Bienvenue <span style='color: #f39c12;'>{st.session_state.username}</span></h1>
    <h4 style='opacity: 0.7;'>Rôle : <b>{st.session_state.role.upper()}</b></h4>
    """, unsafe_allow_html=True)

# 🧭 Onglets
tabs = st.tabs([
    "🖌️ Dessiner ✏️", 
    "➕ Ajouter DXF ✨", 
    "📂 Analyser DXF 🔎", 
    "🛠️ Options ✨", 
    "👤 Mon Profil 💼", 
    "⚙️ Demandes 📂", 
    "🏪 Test matériaux ⚖️"
])

# Onglet demandes
with tabs[5]:
    st.header("💡 Boîte à idées")
    st.markdown("Ajoutez ici toutes vos suggestions de fonctionnalités, design ou outils.")
    idee = st.text_area("✍️ Idée à proposer", placeholder="Ex : Ajouter les matières et épaisseurs dans le dessin...")
    if st.button("🚀 Soumettre"):
        st.success("Merci pour ton idée 💡 Elle sera prise en compte !")
