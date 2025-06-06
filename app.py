import streamlit as st
import tempfile
import os
import matplotlib.pyplot as plt
from utils.dxf_reader import analyze_dxf_file, plot_dxf

st.set_page_config(page_title="PartLab – Arcanum Tech", layout="centered")

# --- STYLE PERSONNALISÉ ---
st.markdown("""
    <style>
        body {
            background-color: #111827;
            color: white;
        }
        .block-container {
            padding: 2rem 2rem 2rem 2rem;
        }
        .stButton button {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
        }
        .step-box {
            background-color: #1f2937;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        }
    </style>
""", unsafe_allow_html=True)

# --- LOGO ---
st.image("assets/logo_arcanum.webp", width=120)
st.markdown("<h1 style='text-align: center;'>PartLab – fichiers DXF</h1>", unsafe_allow_html=True)

# Étape 1
with st.container():
    st.markdown("### 📂 Étape 1 : Importer un fichier DXF")
    uploaded_file = st.file_uploader("Déposez votre fichier .dxf ici :", type=["dxf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    st.success("✅ Fichier chargé avec succès.")

    # Étape 2
    with st.container():
        st.markdown("### 🧱 Étape 2 : Choix de la matière")
        matière = st.selectbox("Matière :", ["Acier", "Alu", "Inox", "Autre"])

    # Étape 3
    with st.container():
        st.markdown("### 📊 Étape 3 : Analyse du fichier")

        try:
            perimetre, nb_trous = analyze_dxf_file(temp_path)

            st.markdown(f"✅ **Matière** : `{matière}`")
            st.markdown(f"📏 **Périmètre estimé** : `{perimetre:.2f}` mm")
            st.markdown(f"🕳️ **Nombre de trous** : `{nb_trous}`")

            fig = plot_dxf(temp_path)
            st.markdown("### 🖼️ Aperçu graphique :")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Erreur lors de l'analyse du fichier : {e}")

    os.remove(temp_path)
