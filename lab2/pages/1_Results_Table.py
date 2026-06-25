# 1_Results_Table.py — Page de recherche et résultats

import streamlit as st
import sys
import os

# Import de utils.py depuis le dossier parent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import search_apps

st.set_page_config(page_title="Search", page_icon="🔍", layout="wide")

st.title("🔍 Search Apps")
st.markdown("---")

# Zone de recherche
st.header("Search Google Play Store")

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input(
        "Search query",
        value="mental health ai",
        placeholder="Ex: mental health ai, wellness app..."
    )
with col2:
    n_hits = st.number_input("Number of results", min_value=5, max_value=50, value=20)

# Bouton de recherche
if st.button("🔍 Search", type="primary"):
    if not query.strip():
        st.warning("Please enter a search term !")
    else:
        with st.spinner(f"Searching '{query}' on Google Play..."):
            df = search_apps(query, n_hits=n_hits)

        if df.empty:
            st.error("No results found. Try a different search term.")
        else:
            # Sauvegarder dans session_state pour la page 2 et 3
            st.session_state["search_results"] = df
            st.session_state["search_query"] = query
            st.success(f"✅ {len(df)} apps found for '{query}' !")

# Afficher les résultats si disponibles
if "search_results" in st.session_state:
    df = st.session_state["search_results"]
    query_saved = st.session_state.get("search_query", "")

    st.markdown("---")

    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📱 Apps Found", len(df))
    col2.metric("⭐ Avg Score", f"{df['score'].mean():.2f}")
    col3.metric("🆓 Free Apps", len(df[df["free"] == "Free"]))
    col4.metric("💰 Paid Apps", len(df[df["free"] == "Paid"]))

    st.markdown("---")

    # Filtres
    st.subheader("🔧 Filters")
    col1, col2, col3 = st.columns(3)

    with col1:
        genres = ["All"] + sorted(df["genre"].dropna().unique().tolist())
        genre_filter = st.selectbox("Genre", genres)

    with col2:
        type_filter = st.radio("Type", ["All", "Free", "Paid"], horizontal=True)

    with col3:
        score_min = st.slider("Min Score", 0.0, 5.0, 0.0, 0.1)

    # Appliquer les filtres
    df_filtered = df.copy()
    if genre_filter != "All":
        df_filtered = df_filtered[df_filtered["genre"] == genre_filter]
    if type_filter != "All":
        df_filtered = df_filtered[df_filtered["free"] == type_filter]
    df_filtered = df_filtered[df_filtered["score"] >= score_min]

    st.subheader(f"📊 {len(df_filtered)} Results")

    # Tableau interactif
    st.dataframe(
        df_filtered[[
            "title", "developer", "score", "ratings",
            "installs", "free", "genre"
        ]],
        use_container_width=True,
        column_config={
            "title":     st.column_config.TextColumn("App Name"),
            "developer": st.column_config.TextColumn("Developer"),
            "score":     st.column_config.NumberColumn("Score ⭐", format="%.2f"),
            "ratings":   st.column_config.NumberColumn("# Ratings"),
            "installs":  st.column_config.TextColumn("Installs"),
            "free":      st.column_config.TextColumn("Type"),
            "genre":     st.column_config.TextColumn("Genre"),
        }
    )

    # Téléchargement
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv, "results.csv", "text/csv")

else:
    st.info("👆 Enter a search term and click Search to get started !")
