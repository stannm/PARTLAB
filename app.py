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
    st.markdown(f"""
    <h1 style='font-size: 2.2em;'>🎨 PartLab – Bienvenue <span style='color: #f39c12;'>{st.session_state.username}</span></h1>
    <h4 style='opacity: 0.7;'>Rôle : <b>{st.session_state.role.upper()}</b></h4>
    """, unsafe_allow_html=True)

onglets = st.tabs([
    "🖌️ Dessiner ✏️", "➕ Ajouter DXF ✨", "📂 Analyser DXF 🔎", "🛠️ Options ✨", "👤 Mon Profil 💼", "⚙️ Demandes 📂", "🏪 Test matériaux ⚖️"])

with onglets[0]:
    st.header("🎨 Zone de dessin interactive")
    drawing_mode = st.selectbox("✏️ Mode de dessin", ("freedraw", "line", "rect", "circle"))
    stroke_width = st.slider("🖌️ Épaisseur du trait", 1, 10, 2)
    fill_color = st.color_picker("🎨 Couleur de remplissage", "#ee6677")
    stroke_color = st.color_picker("🖍️ Couleur du trait", "#000000")

    canvas_result = st_canvas(
        fill_color=fill_color,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#ffffff",
        height=400,
        width=800,
        drawing_mode=drawing_mode,
        key="canvas",
    )

    if canvas_result.json_data:
        st.success("✅ Dessin sauvegardé (JSON dispo)")
        export_format = st.selectbox("📂 Exporter en format", ("json", "pdf", "dxf"))

        if export_format == "pdf":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Aperçu du dessin (formes non visibles)", ln=True, align="C")
            pdf.output("dessin_export.pdf")
            with open("dessin_export.pdf", "rb") as f:
                st.download_button("📄 Télécharger PDF", f, file_name="dessin_export.pdf")

        elif export_format == "json":
            json_str = json.dumps(canvas_result.json_data)
            st.download_button("📄 Télécharger JSON", json_str, file_name="dessin.json")

        elif export_format == "dxf":
            doc = ezdxf.new()
            msp = doc.modelspace()
            for obj in canvas_result.json_data["objects"]:
                if obj["type"] == "line":
                    x1, y1 = obj["x1"], obj["y1"]
                    x2, y2 = obj["x2"], obj["y2"]
                    msp.add_line((x1, y1), (x2, y2))
                elif obj["type"] == "rect":
                    x, y = obj["left"], obj["top"]
                    w, h = obj["width"], obj["height"]
                    msp.add_lwpolyline([
                        (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
                    ], close=True)
                elif obj["type"] == "circle":
                    x, y = obj["left"] + obj["radius"], obj["top"] + obj["radius"]
                    r = obj["radius"]
                    msp.add_circle((x, y), r)
            buffer = io.BytesIO()
            doc.write(buffer)
            st.download_button("🔀 Télécharger DXF", buffer.getvalue(), file_name="dessin_export.dxf")



# Onglet 2 : Ajouter DXF
with onglets[1]:
    st.subheader("➕ Importer un fichier DXF")
    uploaded_file = st.file_uploader("Dépose ton fichier DXF ici :", type=["dxf"])
    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            dxf_path = tmp_file.name
        st.success("✅ Fichier DXF chargé avec succès")

# Onglet 3 : Analyser DXF
with onglets[2]:
    st.subheader("📏 Analyse du fichier DXF")
    try:
        doc = load_dxf(dxf_path)
        perimeter, holes, _ = get_dxf_perimeter_and_holes(doc)
        st.metric("📐 Périmètre estimé", f"{perimeter:.2f} mm")
        st.metric("🕳️ Nombre de trous", holes)
        st.pyplot(plot_dxf(doc))
    except Exception as e:
        st.warning("⚠️ Aucun fichier DXF valide à analyser ou une erreur est survenue.")

# Onglet 4 : Options utilisateur
with onglets[3]:
    st.subheader("🛠️ Paramètres personnalisés")
    matiere = st.selectbox("🧱 Matière", ["Acier", "Alu", "Inox"])
    epaisseur = st.slider("📏 Épaisseur (mm)", 0.5, 20.0, step=0.5)
    quantite = st.number_input("🔢 Quantité", min_value=1, value=1)
    st.info(f"Matière : **{matiere}** | Épaisseur : **{epaisseur}mm** | Quantité : **{quantite}**")

    if st.button("💾 Sauvegarder la configuration"):
        if "configurations" not in st.session_state:
            st.session_state.configurations = []
        st.session_state.configurations.append({
            "matiere": matiere,
            "epaisseur": epaisseur,
            "quantite": quantite
        })
        st.success("✅ Configuration enregistrée")

    if "configurations" in st.session_state and st.session_state.configurations:
        st.markdown("---")
        st.subheader("📁 Configurations enregistrées")
        for idx, config in enumerate(st.session_state.configurations):
            st.markdown(f"🔹 **#{idx+1}** : {config['matiere']}, {config['epaisseur']}mm, {config['quantite']} pièce(s)")

# Onglet 5 : Profil
with onglets[4]:
    st.subheader("👤 Profil de l'utilisateur")
    st.write(f"**Nom d'utilisateur :** {st.session_state.username}")
    st.write(f"**Rôle :** {st.session_state.role.upper()}")

# Onglet Suggestions
with onglets[5]:
    st.header("🧙‍♂️ Boîte à idées & Améliorations")
    st.markdown("Ajoute ici des idées de fonctionnalités ou d'amélioration du site PartLab.")
    suggestion = st.text_area("💬 Votre idée / amélioration", placeholder="Ex : Ajouter une fonction pour générer des pentes en tôle...")
    if st.button("📉 Soumettre la demande"):
        st.success("Merci pour ta suggestion ! Elle a bien été enregistrée. 🔥")

# Onglet Test matériaux
with onglets[6]:
    st.header("🏪 Base de test des matériaux")
    st.markdown("Voici un aperçu comparatif de matériaux utilisés en découpe.")
    st.dataframe({
        "Matière": ["Acier", "Alu", "Inox"],
        "Densité (g/cm³)": [7.85, 2.7, 8.0],
        "Résistance (MPa)": [250, 150, 200],
        "Prix/kg (€)": [0.80, 1.50, 2.00]
    })
