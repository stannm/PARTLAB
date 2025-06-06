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
# 🌗 Thème Personnalisé Synthwave
# ============================
theme = st.sidebar.selectbox("🎨 Thème", ["Sombre", "Clair", "Synthwave 🌅"], key="theme_selector")

if theme == "Clair":
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to bottom right, #ffffff, #eeeeee);
            color: #000000;
        }
        .stButton>button {
            background: linear-gradient(to right, #2980b9, #6dd5fa);
            color: black;
            font-weight: bold;
            border-radius: 10px;
            border: none;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 10px #2980b9;
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
            border: none;
            padding: 8px 16px;
            box-shadow: 0px 0px 10px rgba(255, 65, 108, 0.6);
            transition: all 0.3s ease-in-out;
        }

        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0px 0px 15px rgba(255, 65, 108, 0.9);
        }

        .stTabs [data-baseweb="tab"] {
            background-color: #1e1e2f;
            color: #f0f0f0;
            border-radius: 8px;
            padding: 10px;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #292944;
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

        #MainMenu, header, footer {
            visibility: hidden;
        }
        </style>

        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

else:
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to bottom right, #1f1f1f, #2a2a2a);
            color: #f0f0f0;
        }
        .stButton>button {
            background: linear-gradient(to right, #f39c12, #e67e22);
            color: white;
            font-weight: bold;
            border-radius: 10px;
            border: none;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 0 10px #f39c12;
        }
        h1, h2, h3 {
            text-shadow: 1px 1px 2px #000000;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================
# 🚡 Authentification
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
    if st.button("Connexion"):
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

if st.sidebar.button("🔓 Se déconnecter"):
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
    st.markdown("""
    <h1 style='font-size: 2.2em;'>🎨 PartLab – Bienvenue <span style='color: #f39c12;'>{}</span></h1>
    <h4 style='opacity: 0.7;'>Rôle : <b>{}</b></h4>
    """.format(st.session_state.username, st.session_state.role.upper()), unsafe_allow_html=True)

onglets = st.tabs([
    "🖌️ Dessiner ✏️", "➕ Ajouter DXF ✨", "📂 Analyser DXF 🔎", "🛠️ Options ✨", "👤 Mon Profil 💼", "⚙️ Demandes 📂", "🏪 Test matériaux ⚖️"])

# === Onglet Suggestions
with onglets[5]:
    st.header("🧙‍♂️ Boîte à idées & Améliorations")
    st.markdown("Ajoute ici des idées de fonctionnalités ou d'amélioration du site PartLab.")
    suggestion = st.text_area("💬 Votre idée / amélioration", placeholder="Ex : Ajouter une fonction pour générer des pentes en tôle...")
    if st.button("📉 Soumettre la demande"):
        st.success("Merci pour ta suggestion ! Elle a bien été enregistrée. 🔥")
