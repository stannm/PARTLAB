import streamlit as st
import tempfile
import os
from utils.step_reader import read_step_file, get_perimeter_and_features

st.set_page_config(page_title="PartLab – V1", layout="centered")

st.title("🧪 PartLab – Analyse de pièces STEP")

st.markdown("**Étape 1 : Importer une pièce STEP**")

uploaded_file = st.file_uploader("Dépose ton fichier .step ou .stp ici :", type=["step", "stp"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".step") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    st.success("✅ Fichier chargé avec succès.")

    st.markdown("**Étape 2 : Choisis la matière de la pièce**")
    matière = st.selectbox("Matière :", ["Acier", "Alu", "Inox", "Autre"])

    st.markdown("**Étape 3 : Lecture et analyse de la pièce**")

    part = read_step_file(temp_path)
    if part:
        perimetre, nb_trous, is_pliée = get_perimeter_and_features(part)

        st.info(f"**Matière :** {matière}")
        st.info(f"**Périmètre estimé :** {perimetre} mm")
        st.info(f"**Nombre d'impacts (trous) :** {nb_trous}")
        st.info(f"**La pièce semble être pliée :** {'✅ Oui' if is_pliée else '❌ Non'}")
        st.success("Lecture terminée.")
    else:
        st.error("Erreur lors de la lecture du fichier STEP.")

    os.remove(temp_path)
