import streamlit as st
import tempfile
import os
from utils.dxf_reader import analyze_dxf_file

st.set_page_config(page_title="PartLab V2 – Analyse DXF", layout="centered")

st.title("📐 PartLab V2 – Analyse de fichiers DXF")

st.markdown("**Étape 1 : Importer un fichier DXF**")

uploaded_file = st.file_uploader("Dépose ton fichier .dxf ici :", type=["dxf"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    st.success("✅ Fichier chargé avec succès.")

    st.markdown("**Étape 2 : Choisis la matière de la pièce**")
    matière = st.selectbox("Matière :", ["Acier", "Alu", "Inox", "Autre"])

    st.markdown("**Étape 3 : Analyse du fichier DXF**")

    try:
        perimetre, nb_trous = analyze_dxf_file(temp_path)

        st.info(f"**Matière :** {matière}")
        st.info(f"**Périmètre estimé :** {perimetre:.2f} mm")
        st.info(f"**Nombre de trous :** {nb_trous}")
        st.success("📊 Analyse terminée.")
    except Exception as e:
        st.error(f"Erreur lors de l'analyse du fichier : {e}")

    os.remove(temp_path)
