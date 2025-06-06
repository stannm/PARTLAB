# 📄 Fichier : app.py

import streamlit as st
import tempfile
import os
from utils.dxf_reader import load_dxf, get_dxf_perimeter_and_holes, plot_dxf, modify_dxf

st.set_page_config(page_title="PartLab – DXF Editor", layout="centered")

st.image("assets/logo_arcanum.webp", width=100)
st.title("PartLab – Éditeur de fichiers DXF")

# Section création DXF
st.markdown("### ✏️ Création ou modification d’un fichier DXF")

shape = st.selectbox("Ajouter une forme :", ["Aucune", "Ligne", "Cercle", "Rectangle"])
output_filename = st.text_input("Nom du fichier de sortie (avec .dxf)", "output.dxf")

params = {}
if shape == "Ligne":
    x1 = st.number_input("X début", value=0.0)
    y1 = st.number_input("Y début", value=0.0)
    x2 = st.number_input("X fin", value=100.0)
    y2 = st.number_input("Y fin", value=100.0)
    params["add_line"] = ((x1, y1), (x2, y2))

elif shape == "Cercle":
    cx = st.number_input("Centre X", value=50.0)
    cy = st.number_input("Centre Y", value=50.0)
    radius = st.number_input("Rayon", value=20.0)
    params["add_circle"] = ((cx, cy), radius)

elif shape == "Rectangle":
    rx = st.number_input("Coin bas gauche X", value=10.0)
    ry = st.number_input("Coin bas gauche Y", value=10.0)
    width = st.number_input("Largeur", value=40.0)
    height = st.number_input("Hauteur", value=30.0)
    params["add_rectangle"] = ((rx, ry), width, height)

if st.button("🛠️ Générer le fichier DXF"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
        path = modify_dxf(tmp.name, **params)
        st.success(f"✅ Fichier généré : `{output_filename}`")
        dxf_doc = load_dxf(path)
        fig = plot_dxf(dxf_doc)
        st.pyplot(fig)
        with open(path, "rb") as f:
            st.download_button("📥 Télécharger le fichier DXF", data=f, file_name=output_filename)

# Analyse d’un fichier DXF existant
st.markdown("---")
st.markdown("### 📂 Analyse d’un fichier DXF existant")
uploaded_file = st.file_uploader("Importer un fichier DXF :", type=["dxf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    dxf_doc = load_dxf(temp_path)
    if dxf_doc:
        périmètre, nb_trous, _ = get_dxf_perimeter_and_holes(dxf_doc)
        st.markdown(f"📏 **Périmètre estimé :** `{périmètre} mm`")
        st.markdown(f"🕳️ **Nombre de trous détectés :** `{nb_trous}`")
        fig = plot_dxf(dxf_doc)
        st.pyplot(fig)
    else:
        st.error("❌ Impossible de lire le fichier DXF.")
