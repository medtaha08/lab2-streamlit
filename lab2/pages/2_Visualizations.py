# 2_Visualizations.py — Page de visualisations

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Competitor Analysis",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Competitor Analysis")
st.markdown("---")

# Vérifier que les données existent
if "search_results" not in st.session_state:
    st.warning("⚠️ No data found ! Please go to the **Search** page first.")
    st.stop()

df = st.session_state["search_results"]
query = st.session_state.get("search_query", "")
st.subheader(f"Analysis for : **{query}** — {len(df)} apps")

# ── SIDEBAR : Filtres ──────────────────────────────────────────
st.sidebar.header("🔧 Filters")

app_ids = ["All"] + df["app_id"].tolist()
app_filter = st.sidebar.selectbox("Filter by App ID", app_ids)

genres_dispo = ["All"] + sorted(df["genre"].dropna().unique().tolist())
genre_filter = st.sidebar.selectbox("Genre", genres_dispo)

type_filter = st.sidebar.radio("Type", ["All", "Free", "Paid"])
score_min = st.sidebar.slider("Min Score", 0.0, 5.0, 0.0)

# Appliquer les filtres
df_viz = df.copy()
if app_filter != "All":
    df_viz = df_viz[df_viz["app_id"] == app_filter]
if genre_filter != "All":
    df_viz = df_viz[df_viz["genre"] == genre_filter]
if type_filter != "All":
    df_viz = df_viz[df_viz["free"] == type_filter]
df_viz = df_viz[df_viz["score"] >= score_min]

st.sidebar.metric("Apps displayed", len(df_viz))
st.markdown("---")

# ── MÉTRIQUES ─────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("📱 Total Apps", len(df_viz))
col2.metric("⭐ Avg Score", f"{df_viz['score'].mean():.2f}" if len(df_viz) > 0 else "N/A")
col3.metric("🆓 Free", len(df_viz[df_viz["free"] == "Free"]))
col4.metric("💰 Paid", len(df_viz[df_viz["free"] == "Paid"]))

st.markdown("---")

# ── GRAPHIQUES LIGNE 1 : Top Apps + Distribution Scores ───────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 10 Apps by Score")
    top10 = df_viz.nlargest(10, "score")
    fig1 = px.bar(
        top10, x="score", y="title", orientation="h",
        color="score", color_continuous_scale="Blues",
        labels={"score": "Score", "title": "App"}
    )
    fig1.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📊 Score Distribution")
    fig2 = px.histogram(
        df_viz, x="score", nbins=10,
        color_discrete_sequence=["#2E75B6"],
        labels={"score": "Score", "count": "Number of Apps"}
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ── GRAPHIQUES LIGNE 2 : Pie Chart + Top Ratings ──────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("🆓 Free vs Paid Apps")
    free_counts = df_viz["free"].value_counts().reset_index()
    free_counts.columns = ["type", "count"]
    fig3 = px.pie(
        free_counts, values="count", names="type",
        color_discrete_sequence=["#1D9E75", "#2E75B6"]
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("📈 Top 10 Apps by Number of Ratings")
    top_ratings = df_viz.nlargest(10, "ratings")
    fig4 = px.bar(
        top_ratings, x="title", y="ratings",
        color="score", color_continuous_scale="Viridis",
        labels={"ratings": "# Ratings", "title": "App"}
    )
    fig4.update_layout(xaxis_tickangle=-45, height=400)
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ── GRAPHIQUES LIGNE 3 : Genre Distribution ───────────────────
st.subheader("🎯 Genre Distribution")
genre_counts = df_viz["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]
fig5 = px.bar(
    genre_counts, x="genre", y="count",
    color="count", color_continuous_scale="Blues",
    labels={"genre": "Genre", "count": "Number of Apps"}
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ── WORDCLOUD ─────────────────────────────────────────────────
st.subheader("☁️ WordCloud from Descriptions")
try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt

    texte = " ".join(df_viz["description"].dropna().tolist())
    if texte.strip():
        wc = WordCloud(
            width=800, height=350,
            background_color="white",
            colormap="Blues",
            max_words=100
        ).generate(texte)

        fig, ax = plt.subplots(figsize=(12, 4))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.info("Not enough descriptions for WordCloud")
except ImportError:
    st.warning("Install wordcloud : pip install wordcloud")

st.markdown("---")
st.caption("Lab 2 — Data Applications with Streamlit | ENSIAS 2026")
