# 📄 Fichier : app.py

try:
    import streamlit as st
    import tempfile
    import os
    from utils.dxf_reader import load_dxf, get_dxf_perimeter_and_holes, plot_dxf, modify_dxf
    from streamlit_drawable_canvas import st_canvas
except ModuleNotFoundError as e:
    raise ImportError("Ce script nécessite les bibliothèques `streamlit` et `streamlit-drawable-canvas`. Veuillez les installer avec 'pip install streamlit streamlit-drawable-canvas'") from e

st.set_page_config(page_title="PartLab – DXF Lab Creator", layout="wide")

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
    if st.button("Connexion"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = user["role"]
            st.success("Connexion réussie ✅")
            st.experimental_rerun()
        else:
            st.error("Identifiants incorrects ❌")
    st.stop()

if st.button("🔓 Se déconnecter"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

# ============================
# ✅ Interface principale (après connexion)
# ============================
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/logo_arcanum.webp", width=100)
with col2:
    st.title(f"PartLab – Bienvenue {st.session_state.username}")
    st.caption(f"Rôle : {st.session_state.role.upper()}")

st.markdown("## 🧰 Options avancées")

canvas_result = st_canvas(
    fill_color="rgba(0, 0, 255, 0.3)",
    stroke_width=2,
    stroke_color="#000000",
    background_color="#f0f0f0",
    height=400,
    width=800,
    drawing_mode=st.selectbox("Mode de dessin", ["freedraw", "line", "rect", "circle", "transform"]),
    key="canvas"
)

st.markdown("### 📷 Importer une image de base")
img = st.file_uploader("Importer une image (JPG/PNG)", type=["png", "jpg"])

if img:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(img.read())
        st.image(tmp.name, caption="Image importée", use_column_width=True)
        st.info("⚠️ Conversion en DXF non encore activée – à venir !")

if st.session_state.role == "admin":
    st.markdown("### ✍️ Ajouter des entités DXF personnalisées")
    shape = st.selectbox("Type de forme à ajouter :", ["Aucune", "Ligne", "Cercle", "Rectangle", "Texte"])
    output_filename = st.text_input("Nom du fichier de sortie (.dxf)", value="output.dxf")
    params = {}

    if shape == "Ligne":
        x1 = st.number_input("X1", value=0.0)
        y1 = st.number_input("Y1", value=0.0)
        x2 = st.number_input("X2", value=100.0)
        y2 = st.number_input("Y2", value=100.0)
        params['add_line'] = ((x1, y1), (x2, y2))

    elif shape == "Cercle":
        cx = st.number_input("Centre X", value=50.0)
        cy = st.number_input("Centre Y", value=50.0)
        radius = st.number_input("Rayon", value=25.0)
        params['add_circle'] = ((cx, cy), radius)

    elif shape == "Rectangle":
        rx = st.number_input("X", value=10.0)
        ry = st.number_input("Y", value=10.0)
        width = st.number_input("Largeur", value=100.0)
        height = st.number_input("Hauteur", value=50.0)
        params['add_rectangle'] = ((rx, ry), width, height)

    elif shape == "Texte":
        tx = st.number_input("Position X", value=0.0)
        ty = st.number_input("Position Y", value=0.0)
        content = st.text_input("Texte à afficher", value="PartLab")
        height = st.number_input("Taille du texte", value=10.0)
        params['add_text'] = ((tx, ty), content, height)

    if st.button("💾 Générer / Modifier le DXF"):
        output_path = os.path.join(tempfile.gettempdir(), output_filename)
        modify_dxf(output_path, **params)
        st.success(f"✅ Fichier généré/modifié avec succès : {output_path}")
else:
    st.info("🔐 Seuls les administrateurs peuvent ajouter des formes au DXF.")

st.markdown("## 📂 Analyse d’un fichier DXF existant")

uploaded_file = st.file_uploader("Déposez votre fichier DXF ici :", type="dxf")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    dxf_doc = load_dxf(tmp_path)

    if dxf_doc:
        st.success("✅ Fichier chargé !")
        st.markdown("### ⚙️ Analyse technique")
        material = st.selectbox("Sélectionner la matière", ["Acier", "Alu", "Inox", "Autre"])

        try:
            perimeter, num_holes, details = get_dxf_perimeter_and_holes(dxf_doc)
            st.markdown(f"📏 **Périmètre estimé :** `{perimeter} mm`")
            st.markdown(f"🕳️ **Nombre de trous détectés :** `{num_holes}`")
            st.markdown("### 👁️ Aperçu visuel du plan")
            fig = plot_dxf(dxf_doc)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"❌ Erreur pendant l'analyse : {e}")
