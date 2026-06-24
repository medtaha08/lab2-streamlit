# pages/2_Visualizations.py
# Page 2 : Visualisations des données récupérées en Page 1

import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Visualizations", page_icon="📊", layout="wide")

st.title("📊 Visualisations — Competitor Analysis")

# ── VÉRIFIER QUE DATA EST DISPONIBLE ──
if "results" not in st.session_state:
    st.warning("⚠️ Aucune donnée disponible. Allez d'abord sur **Results Table** et faites une recherche !")
    st.stop()

df = st.session_state["results"].copy()
query = st.session_state.get("query", "")
st.markdown(f"Analyse basée sur la recherche : **{query}** — {len(df)} apps")

# ── SIDEBAR FILTER ──
st.sidebar.header("🔧 Filtres")
genres = ["Tous"] + sorted(df["genre"].dropna().unique().tolist())
selected_genre = st.sidebar.selectbox("Filtrer par catégorie", genres)
free_only = st.sidebar.checkbox("Apps gratuites uniquement")
min_score = st.sidebar.slider("Note minimale", 0.0, 5.0, 0.0, 0.1)

# Appliquer les filtres
if selected_genre != "Tous":
    df = df[df["genre"] == selected_genre]
if free_only:
    df = df[df["free"] == True]
df = df[df["score"].fillna(0) >= min_score]

st.markdown(f"*{len(df)} apps après filtrage*")
st.divider()

# ── CHARTS ──
col1, col2 = st.columns(2)

with col1:
    st.subheader("⭐ Distribution des notes")
    fig = px.histogram(df, x="score", nbins=10, color_discrete_sequence=["#636EFA"])
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🆓 Apps Gratuites vs Payantes")
    free_counts = df["free"].value_counts().reset_index()
    free_counts.columns = ["Type", "Count"]
    free_counts["Type"] = free_counts["Type"].map({True: "Gratuit", False: "Payant"})
    fig = px.pie(free_counts, values="Count", names="Type",
                 color_discrete_sequence=["#00CC96", "#EF553B"])
    st.plotly_chart(fig, use_container_width=True)

st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("📂 Distribution par catégorie")
    genre_counts = df["genre"].value_counts().reset_index()
    genre_counts.columns = ["Genre", "Count"]
    fig = px.bar(genre_counts, x="Genre", y="Count",
                 color_discrete_sequence=["#AB63FA"])
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("🏆 Top 10 apps par note")
    top10 = df.nlargest(10, "score")[["title", "score", "installs"]].dropna()
    fig = px.bar(top10, x="score", y="title", orientation="h",
                 color="score", color_continuous_scale="Blues")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📥 Top 10 apps par installations")
df["minInstalls"] = pd.to_numeric(df["minInstalls"], errors="coerce")
top_installs = df.nlargest(10, "minInstalls")[["title", "minInstalls"]].dropna()
fig = px.bar(top_installs, x="minInstalls", y="title", orientation="h",
             color_discrete_sequence=["#FFA15A"])
st.plotly_chart(fig, use_container_width=True)