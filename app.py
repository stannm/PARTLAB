# 📄 Fichier : app.py

import streamlit as st
import tempfile
import os
from utils.dxf_reader import load_dxf, get_dxf_perimeter_and_holes, plot_dxf

st.set_page_config(page_title="PartLab – fichiers DXF", layout="centered")

# Logo + Titre
col1, col2 = st.columns([1, 6])
with col1:
    st.image("assets/logo_arcanum.webp", width=100)
with col2:
    st.title("PartLab – fichiers DXF")

# Étape 1
st.markdown("### 📂 Étape 1 : Importer un fichier DXF")
uploaded_file = st.file_uploader("Déposez votre fichier .dxf ici :", type=["dxf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.success("✅ Fichier chargé avec succès.")

    # Étape 2
    st.markdown("### 🧱 Étape 2 : Choix de la matière")
    matiere = st.selectbox("Matière :", ["Acier", "Alu", "Inox", "Autre"])

    # Étape 3
    st.markdown("### 🧪 Étape 3 : Analyse du fichier")
    try:
        dxf_doc = load_dxf(tmp_path)
        if dxf_doc:
            perimetre, nb_trous, _ = get_dxf_perimeter_and_holes(dxf_doc)

            st.markdown(f"✅ **Matière :** `{matiere}`")
            st.markdown(f"📏 **Périmètre estimé :** `{perimetre} mm`")
            st.markdown(f"🕳️ **Nombre de trous :** `{nb_trous}`")

            # Affichage DXF
            st.markdown("### 🖼️ Aperçu du fichier DXF")
            fig = plot_dxf(dxf_doc)
            st.pyplot(fig)

            st.success("✅ Analyse terminée.")
        else:
            st.error("❌ Erreur de chargement du fichier DXF.")
    except Exception as e:
        st.error(f"Erreur lors de l’analyse du fichier : {str(e)}")
