# Home.py
# Page d'accueil de l'application Streamlit - Competitor Analysis

import streamlit as st

st.set_page_config(
    page_title="App Competitor Analysis",
    page_icon="📱",
    layout="wide"
)

st.title("📱 Google Play Store — Competitor Analysis")
st.markdown("---")

st.markdown("""
## 🎯 Description du projet
Cette application permet d'analyser les applications concurrentes sur le **Google Play Store**
dans le domaine de la **santé mentale et du bien-être**.

## ✨ Fonctionnalités
- 🔍 **Recherche dynamique** : entrez un terme et récupérez les apps en temps réel
- 📊 **Tableau de résultats** : consultez les données détaillées de chaque app
- 📈 **Visualisations** : graphiques interactifs pour analyser la concurrence

## 🚀 Comment utiliser l'app
1. Allez sur la page **Results Table** dans le menu à gauche
2. Entrez un terme de recherche (ex: *mental health AI*)
3. Consultez les résultats dans le tableau
4. Allez sur **Visualizations** pour voir les graphiques

## 🛠️ Technologies utilisées
- `streamlit` — interface web
- `google-play-scraper` — récupération des données
- `pandas` — traitement des données
- `plotly` — visualisations interactives

## 📌 Améliorations possibles
- Ajouter des données depuis ProductHunt ou GitHub
- Analyse de sentiment sur les reviews
- Export PDF du rapport
""")

st.info("👈 Commencez par la page **Results Table** dans le menu à gauche !")