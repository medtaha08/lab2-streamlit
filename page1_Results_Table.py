# pages/1_Results_Table.py
# Page 1 : Recherche et affichage des résultats sous forme de tableau

import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import search_apps

st.set_page_config(page_title="Results Table", page_icon="🔍", layout="wide")

st.title("🔍 Résultats de recherche")
st.markdown("Entrez un terme pour rechercher des applications sur le Google Play Store.")

# ── INPUT UTILISATEUR ──
query = st.text_input("🔎 Terme de recherche", placeholder="Ex: mental health AI")
n_results = st.slider("Nombre de résultats", 5, 50, 20)

# ── BOUTON RECHERCHE ──
if st.button("Rechercher", type="primary"):
    if not query:
        st.warning("⚠️ Entrez un terme de recherche !")
    else:
        with st.spinner(f"Recherche en cours pour '{query}'..."):
            df = search_apps(query, n_results)

        if df.empty:
            st.error("❌ Aucun résultat trouvé.")
        else:
            # Sauvegarder dans session_state pour la page 2
            st.session_state["results"] = df
            st.session_state["query"] = query
            st.success(f"✅ {len(df)} applications trouvées !")

# ── AFFICHAGE DU TABLEAU ──
if "results" in st.session_state:
    df = st.session_state["results"]
    st.markdown(f"### 📋 Résultats pour : *{st.session_state.get('query', '')}*")

    st.dataframe(
        df[["title", "developer", "genre", "score", "ratings", "installs", "free", "price"]],
        use_container_width=True,
        column_config={
            "title":     st.column_config.TextColumn("Application"),
            "developer": st.column_config.TextColumn("Développeur"),
            "genre":     st.column_config.TextColumn("Catégorie"),
            "score":     st.column_config.NumberColumn("Note ⭐", format="%.2f"),
            "ratings":   st.column_config.NumberColumn("Nb Notes"),
            "installs":  st.column_config.TextColumn("Installations"),
            "free":      st.column_config.CheckboxColumn("Gratuit ?"),
            "price":     st.column_config.NumberColumn("Prix ($)"),
        }
    )