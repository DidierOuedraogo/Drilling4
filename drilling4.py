import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from io import StringIO

# Configuration de la page
st.set_page_config(layout="wide", page_title="Analyse de Forages Miniers")

# Fonction pour charger et mettre en cache les données
@st.cache_data
def load_data(file):
    if file is not None:
        return pd.read_csv(file)
    return None

# Initialisation du session state
if 'data' not in st.session_state:
    st.session_state.data = {
        'collars': None,
        'survey': None,
        'lithology': None,
        'assays': None,
        'columns_mapping': {}
    }

# Fonction pour télécharger les données
def download_data(df, name):
    if df is not None:
        csv = df.to_csv(index=False)
        st.download_button(
            label=f"Télécharger {name}",
            data=csv,
            file_name=f"{name}.csv",
            mime='text/csv'
        )

# Interface principale
st.title("Application d'Analyse de Forages Miniers")

# Création des onglets
tabs = st.tabs(["Chargement", "Aperçu", "Statistiques", "Visualisation 3D"])

# Onglet Chargement
with tabs[0]:
    st.header("Chargement et Configuration des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Chargement Collars
        st.subheader("Collars")
        collars_file = st.file_uploader("Fichier Collars", type=['csv'])
        if collars_file:
            st.session_state.data['collars'] = load_data(collars_file)
            if st.session_state.data['collars'] is not None:
                st.session_state.data['columns_mapping']['hole_id'] = st.selectbox(
                    "Colonne HOLE_ID",
                    st.session_state.data['collars'].columns
                )
                st.session_state.data['columns_mapping']['east'] = st.selectbox(
                    "Colonne EAST",
                    st.session_state.data['collars'].columns
                )
                st.session_state.data['columns_mapping']['north'] = st.selectbox(
                    "Colonne NORTH",
                    st.session_state.data['collars'].columns
                )
                st.session_state.data['columns_mapping']['elevation'] = st.selectbox(
                    "Colonne ELEVATION",
                    st.session_state.data['collars'].columns
                )
        
        # Chargement Survey
        st.subheader("Survey")
        survey_file = st.file_uploader("Fichier Survey", type=['csv'])
        if survey_file:
            st.session_state.data['survey'] = load_data(survey_file)
            
    with col2:
        # Chargement Lithology
        st.subheader("Lithology")
        litho_file = st.file_uploader("Fichier Lithology", type=['csv'])
        if litho_file:
            st.session_state.data['lithology'] = load_data(litho_file)
        
        # Chargement Assays
        st.subheader("Assays")
        assays_file = st.file_uploader("Fichier Assays", type=['csv'])
        if assays_file:
            st.session_state.data['assays'] = load_data(assays_file)

# Onglet Aperçu
with tabs[1]:
    st.header("Aperçu des Données")
    
    for name, df in st.session_state.data.items():
        if isinstance(df, pd.DataFrame):
            st.subheader(name.capitalize())
            st.dataframe(df.head())
            download_data(df, name)
            
            with st.expander(f"Informations sur {name}"):
                st.write("Dimensions:", df.shape)
                st.write("Types de données:", df.dtypes)
                st.write("Valeurs manquantes:", df.isnull().sum())

# Onglet Statistiques
with tabs[2]:
    st.header("Analyses Statistiques")
    
    if st.session_state.data['assays'] is not None:
        # Sélection des colonnes numériques
        num_cols = st.session_state.data['assays'].select_dtypes(include=[np.number]).columns
        selected_col = st.selectbox("Sélectionner une colonne pour l'analyse", num_cols)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Statistiques descriptives")
            stats = st.session_state.data['assays'][selected_col].describe()
            st.dataframe(stats)
            
        with col2:
            st.subheader("Histogramme")
            fig = go.Figure(data=[go.Histogram(x=st.session_state.data['assays'][selected_col])])
            fig.update_layout(
                title=f"Distribution de {selected_col}",
                xaxis_title=selected_col,
                yaxis_title="Fréquence"
            )
            st.plotly_chart(fig, use_container_width=True)

# Onglet Visualisation 3D
with tabs[3]:
    st.header("Visualisation 3D des Forages")
    
    if all(df is not None for df in [st.session_state.data['collars'], st.session_state.data['survey']]):
        # Création de la visualisation 3D
        fig = go.Figure(data=[go.Scatter3d(
            x=st.session_state.data['collars'][st.session_state.data['columns_mapping']['east']],
            y=st.session_state.data['collars'][st.session_state.data['columns_mapping']['north']],
            z=st.session_state.data['collars'][st.session_state.data['columns_mapping']['elevation']],
            mode='markers',
            marker=dict(
                size=5,
                color='blue',
                opacity=0.8
            ),
            name='Collars'
        )])
        
        fig.update_layout(
            scene=dict(
                aspectmode='data',
                xaxis_title='Est',
                yaxis_title='Nord',
                zaxis_title='Élévation'
            ),
            title="Visualisation 3D des Forages",
            height=800
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Veuillez charger les données Collars et Survey pour la visualisation 3D")

# Barre de progression
progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

# Simulation de chargement
for i in range(100):
    status_text.text(f"{i+1}% Chargé")
    progress_bar.progress(i + 1)
    time.sleep(0.01)

progress_bar.empty()
status_text.empty()

# Bouton de rafraîchissement
if st.sidebar.button("Rafraîchir les données"):
    st.experimental_rerun()