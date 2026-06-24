# test_app.py
# But : tester tous les widgets Streamlit du lab

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Test Widgets", page_icon="🧪", layout="wide")

# ── PARTIE 1 : DISPLAY WIDGETS ──────────────────────────────────
st.title("🧪 Test de tous les widgets Streamlit")
st.header("1. Display Widgets")
st.subheader("Sous-titre avec subheader")
st.text("Texte brut avec st.text")
st.write("Texte avec st.write — affiche tout !")
st.markdown("**Gras**, *italique*, `code inline`, [lien](https://streamlit.io)")
st.code('print("Hello depuis st.code")', language="python")
st.success("✅ Message de succès")
st.error("❌ Message d'erreur")
st.warning("⚠️ Message d'avertissement")
st.info("ℹ️ Message d'information")
st.divider()

# ── PARTIE 2 : STREAMLIT MAGIC ──────────────────────────────────
st.header("2. Streamlit Magic")
st.write("Avec Streamlit Magic, tu affiches un DataFrame juste en l'écrivant :")

# MAGIC : juste écrire df l'affiche automatiquement !
df = pd.DataFrame({
    "App":     ["Calm", "Headspace", "BetterHelp"],
    "Score":   [4.8, 4.7, 4.5],
    "Gratuit": [True, True, False]
})
df  # <- Streamlit Magic : affiche automatiquement le DataFrame !

st.divider()

# ── PARTIE 3 : INPUT WIDGETS ────────────────────────────────────
st.header("3. Input Widgets")

col1, col2 = st.columns(2)

with col1:
    nom = st.text_input("Ton nom", placeholder="Ex: Ayoub")
    age = st.number_input("Ton âge", min_value=0, max_value=120, value=20)
    description = st.text_area("Description", height=80)

with col2:
    from datetime import date
    naissance = st.date_input("Date de naissance", value=date(2000, 1, 1))
    fichier = st.file_uploader("Uploade un fichier CSV", type=["csv"])
    if fichier:
        df_upload = pd.read_csv(fichier)
        st.dataframe(df_upload)

st.divider()

# ── PARTIE 4 : FILTER WIDGETS ───────────────────────────────────
st.header("4. Filter Widgets")

col1, col2 = st.columns(2)

with col1:
    agree = st.checkbox("J'accepte les conditions")
    toggle = st.toggle("Mode sombre")
    choix = st.radio("Choix unique", ["Option A", "Option B", "Option C"])

with col2:
    pays = st.selectbox("Pays", ["Maroc", "France", "USA", "Espagne"])
    langues = st.multiselect("Langues parlées", ["Python", "Java", "JS", "R"])
    note = st.slider("Note /5", 0.0, 5.0, 3.0, 0.1)
    plage = st.select_slider("Plage de prix", ["Gratuit", "< 5€", "5-10€", "> 10€"])

st.divider()

# ── PARTIE 5 : BUTTON WIDGETS ───────────────────────────────────
st.header("5. Button Widgets")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Bouton principal", type="primary"):
        st.write(f"Bonjour {nom or 'Anonyme'} !")

with col2:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger CSV", csv, "data.csv", "text/csv")

with col3:
    st.link_button("🔗 Streamlit Docs", "https://docs.streamlit.io")

st.divider()

# ── PARTIE 6 : DATA WIDGETS ─────────────────────────────────────
st.header("6. Data Widgets")

st.subheader("dataframe — Tableau interactif")
st.dataframe(df, use_container_width=True, column_config={
    "App":     st.column_config.TextColumn("Application"),
    "Score":   st.column_config.NumberColumn("Note ⭐", format="%.1f"),
    "Gratuit": st.column_config.CheckboxColumn("Gratuit ?"),
})

st.subheader("table — Tableau statique")
st.table(df)

st.subheader("data_editor — Tableau éditable")
df_edite = st.data_editor(df)
st.write("Données modifiées :", df_edite)

st.divider()

# ── PARTIE 7 : UX DESIGN ────────────────────────────────────────
st.header("7. UX Design — Layouts et Containers")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Données", "📈 Stats", "ℹ️ Info"])
with tab1:
    st.write("Contenu onglet 1")
    st.dataframe(df)
with tab2:
    st.write("Contenu onglet 2")
    st.metric("Score moyen", f"{df['Score'].mean():.2f}")
with tab3:
    st.write("Contenu onglet 3")

# Expander
with st.expander("Voir les détails cachés"):
    st.write("Ce contenu est caché par défaut !")
    st.code("hidden_code = True")

# Spinner
if st.button("Simuler un chargement"):
    with st.spinner("Chargement en cours..."):
        import time
        time.sleep(2)
    st.success("Chargé !")

st.divider()
st.caption("test_app.py — Lab 2 ENSIAS 2026")