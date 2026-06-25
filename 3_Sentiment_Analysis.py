# 3_Sentiment_Analysis.py — Page d'analyse de sentiment

import streamlit as st
import plotly.express as px
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_reviews, compute_sentiment

st.set_page_config(
    page_title="Sentiment Analysis",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Sentiment Analysis")
st.markdown("---")

# Vérifier que les données existent
if "search_results" not in st.session_state:
    st.warning("⚠️ No data found ! Please go to the **Search** page first.")
    st.stop()

df = st.session_state["search_results"]
query = st.session_state.get("search_query", "")

st.write(f"**Query :** {query} — {len(df)} apps available")
st.info("This page uses **DistilBERT** from HuggingFace to analyze the sentiment of user reviews.")
st.markdown("---")

# Sélection des apps à analyser
st.subheader("⚙️ Settings")
col1, col2 = st.columns(2)

with col1:
    app_options = df["title"].tolist()
    selected_apps = st.multiselect(
        "Select apps to analyze (max 5)",
        app_options,
        default=app_options[:3]
    )

with col2:
    n_reviews = st.number_input(
        "Number of reviews per app",
        min_value=5,
        max_value=30,
        value=10
    )

if st.button("🚀 Run Sentiment Analysis", type="primary"):
    if not selected_apps:
        st.warning("Please select at least one app !")
    else:
        all_results = []

        progress = st.progress(0)
        status = st.empty()

        for i, app_title in enumerate(selected_apps):
            status.text(f"Analyzing '{app_title}'... ({i+1}/{len(selected_apps)})")

            # Récupérer l'app_id depuis le titre
            app_row = df[df["title"] == app_title].iloc[0]
            app_id = app_row["app_id"]

            # Récupérer les reviews
            with st.spinner(f"Getting reviews for {app_title}..."):
                revs = get_reviews(app_id, count=n_reviews)

            if not revs:
                st.warning(f"No reviews found for {app_title}")
                continue

            # Calculer le sentiment
            with st.spinner(f"Computing sentiment for {app_title}..."):
                df_sent = compute_sentiment(revs, app_id, app_title)

            if not df_sent.empty:
                all_results.append(df_sent)

            progress.progress((i + 1) / len(selected_apps))

        status.empty()
        progress.empty()

        if all_results:
            df_all = pd.concat(all_results, ignore_index=True)
            st.session_state["sentiment_results"] = df_all
            st.success(f"✅ Analysis complete ! {len(df_all)} reviews analyzed.")
        else:
            st.error("No results. Try different apps.")

# Afficher les résultats
if "sentiment_results" in st.session_state:
    df_all = st.session_state["sentiment_results"]

    st.markdown("---")
    st.header("📊 Results")

    # ── MÉTRIQUES GLOBALES ──────────────────────────────────────
    total = len(df_all)
    pos = len(df_all[df_all["sentiment"] == "POSITIVE"])
    neg = len(df_all[df_all["sentiment"] == "NEGATIVE"])

    col1, col2, col3 = st.columns(3)
    col1.metric("📝 Total Reviews", total)
    col2.metric("😊 Positive", f"{pos} ({100*pos//total}%)")
    col3.metric("😞 Negative", f"{neg} ({100*neg//total}%)")

    st.markdown("---")

    # ── BAR CHART : Score par App ───────────────────────────────
    st.subheader("📊 Sentiment Score by App")

    sentiment_summary = df_all.groupby("app_name")["sentiment"].value_counts(normalize=True).reset_index()
    sentiment_summary.columns = ["app_name", "sentiment", "percentage"]
    sentiment_summary["percentage"] = (sentiment_summary["percentage"] * 100).round(1)

    fig1 = px.bar(
        sentiment_summary,
        x="app_name",
        y="percentage",
        color="sentiment",
        barmode="group",
        color_discrete_map={"POSITIVE": "#1D9E75", "NEGATIVE": "#E74C3C"},
        labels={"app_name": "App", "percentage": "% Reviews", "sentiment": "Sentiment"},
        title="Sentiment Distribution by App (%)"
    )
    fig1.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig1, use_container_width=True)

    # ── DÉTAIL PAR APP ──────────────────────────────────────────
    st.markdown("---")
    st.subheader("🔍 Details by App")

    apps_analyzed = df_all["app_name"].unique().tolist()
    selected_app = st.selectbox("Select an app for details", apps_analyzed)

    df_app = df_all[df_all["app_name"] == selected_app]

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart sentiment pour cette app
        sent_counts = df_app["sentiment"].value_counts().reset_index()
        sent_counts.columns = ["sentiment", "count"]
        fig2 = px.pie(
            sent_counts,
            values="count",
            names="sentiment",
            color="sentiment",
            color_discrete_map={"POSITIVE": "#1D9E75", "NEGATIVE": "#E74C3C"},
            title=f"Sentiment for {selected_app}"
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Distribution des notes vs sentiment
        fig3 = px.histogram(
            df_app,
            x="rating",
            color="sentiment",
            barmode="overlay",
            color_discrete_map={"POSITIVE": "#1D9E75", "NEGATIVE": "#E74C3C"},
            title="Rating Distribution by Sentiment"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Reviews détaillées
    st.subheader(f"📝 Sample Reviews — {selected_app}")
    st.dataframe(
        df_app[["review", "sentiment", "confidence", "rating"]],
        use_container_width=True,
        column_config={
            "review":     st.column_config.TextColumn("Review"),
            "sentiment":  st.column_config.TextColumn("Sentiment"),
            "confidence": st.column_config.NumberColumn("Confidence", format="%.2f"),
            "rating":     st.column_config.NumberColumn("Rating ⭐"),
        }
    )

st.markdown("---")
st.caption("Lab 2 — Sentiment Analysis with HuggingFace DistilBERT | ENSIAS 2026")
