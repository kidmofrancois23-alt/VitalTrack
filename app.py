import streamlit as st

import pandas as pd

import os

import re

import plotly.express as px



# --- CONFIGURATION ---

st.set_page_config(

    page_title="VitalTrack - NISSO KIDMO FRANÇOIS",

    page_icon="🩺",

    layout="wide"

)



DATA_FILE = 'sante_data.csv'

COLUMNS = ['Nom', 'Âge', 'Genre', 'Poids (kg)', 'Taille (cm)', 'Tension']



# --- FONCTIONS DE CALCUL ---

def calculer_imc(poids, taille_cm):

    try:

        return round(poids / ((taille_cm / 100) ** 2), 2) if taille_cm > 0 else 0

    except: return 0



def obtenir_statut_imc(imc):

    if imc <= 0: return "Inconnu"

    elif imc < 18.5: return "Insuffisance"

    elif 18.5 <= imc < 25: return "Poids Normal"

    elif 25 <= imc < 30: return "Surpoids"

    else: return "Obésité"



def obtenir_risques(imc):

    if imc <= 0: return "Données insuffisantes."

    elif imc < 18.5: return "Risque d'anémie et de fragilité osseuse."

    elif 18.5 <= imc < 25: return "Excellent équilibre métabolique."

    elif 25 <= imc < 30: return "Risque d'hypertension et de fatigue articulaire."

    else: return "Risques élevés : Diabète, maladies cardiaques et apnée du sommeil."



# --- PROTECTION ANTI-TRADUCTION ---

st.markdown('<div translate="no">', unsafe_allow_html=True)



# --- CHARGEMENT DES DONNÉES ---

if os.path.exists(DATA_FILE):

    df = pd.read_csv(DATA_FILE)

    df = df[COLUMNS].copy()

    df['IMC'] = df.apply(lambda x: calculer_imc(x['Poids (kg)'], x['Taille (cm)']), axis=1)

    df['Statut'] = df['IMC'].apply(obtenir_statut_imc)

else:

    df = pd.DataFrame(columns=COLUMNS + ['IMC', 'Statut'])



# --- STYLE CSS ---

st.markdown("""

    <style>

    .stTabs [aria-selected="true"] { background-color: #00a65a !important; color: white !important; }

    .metric-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border-left: 5px solid #00a65a; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }

    </style>

    """, unsafe_allow_html=True)



# --- SIDEBAR ---

with st.sidebar:

    st.header("NISSO KIDMO FRANÇOIS")

    st.write(f"**Matricule :** 22W2158")

    st.markdown("---")



# --- ONGLETS ---

tab1, tab2, tab3 = st.tabs(["➕ Nouvelle Saisie", "📊 Analyse Descriptive", "⚙️ Gestion & Modification"])



# --- ONGLET 1 : ENREGISTREMENT ---

with tab1:

    st.header("Enregistrement Patient")

    with st.form("form_saisie", clear_on_submit=True):

        nom_input = st.text_input("Nom complet")

        

        # --- AJOUT DE LA VALIDATION DU NOM ---

        if nom_input:

            if any(char.isdigit() for char in nom_input):

                st.warning("⚠️ Attention : Le nom ne doit pas contenir de chiffres.")

            elif not re.match(r"^[A-Za-z\sÀ-ÿ\-']+$", nom_input):

                st.warning("⚠️ Attention : Caractères spéciaux non autorisés dans le nom.")



        c1, c2 = st.columns(2)

        with c1:

            age = st.number_input("Âge", 0, 120, 25)

            poids = st.number_input("Poids (kg)", 1.0, 250.0, 70.0)

        with c2:

            genre = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"])

            taille = st.number_input("Taille (cm)", 40, 250, 170)

        tension = st.number_input("Tension Artérielle", 50, 200, 120)

        

        if st.form_submit_button("Enregistre"):

            # Vérification finale avant enregistrement

            if nom_input and not any(char.isdigit() for char in nom_input) and re.match(r"^[A-Za-z\sÀ-ÿ\-']+$", nom_input):

                new_row = pd.DataFrame([[nom_input, age, genre, poids, taille, tension]], columns=COLUMNS)

                if os.path.exists(DATA_FILE):

                    df_all = pd.concat([pd.read_csv(DATA_FILE)[COLUMNS], new_row], ignore_index=True)

                else:

                    df_all = new_row

                df_all.to_csv(DATA_FILE, index=False)

                st.success(f"✅ {nom_input} enregistré avec succès !")

                st.rerun()

            else:

                st.error("❌ Erreur : Veuillez saisir un nom valide (lettres uniquement, pas de chiffres).")



# --- ONGLET 2 : ANALYSE DESCRIPTIVE ---

with tab2:

    st.header("Analyses Statistiques")

    if not df.empty:

        st.subheader("📋 Base de données")

        st.dataframe(df, use_container_width=True)

        

        st.markdown(f'<div class="metric-card"><h3>Total Patients : {len(df)}</h3></div>', unsafe_allow_html=True)



        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Relation Âge vs Tension")

            st.plotly_chart(px.scatter(df, x="Âge", y="Tension", color="Genre", trendline="ols", hover_name="Nom"), use_container_width=True)

        with col2:

            st.subheader("Bilan Global de Santé (IMC)")

            df_stats = df['Statut'].value_counts().reset_index()

            df_stats.columns = ['Statut', 'Nombre']

            fig_donut = px.pie(df_stats, values='Nombre', names='Statut', hole=0.5,

                               color='Statut', color_discrete_map={

                                   "Poids Normal": "#28a745", "Surpoids": "#ffc107", 

                                   "Obésité": "#dc3545", "Insuffisance": "#17a2b8", "Inconnu": "#6c757d"

                               })

            fig_donut.update_traces(textposition='inside', textinfo='percent+label')

            st.plotly_chart(fig_donut, use_container_width=True)



        st.markdown("---")

        st.header("🚨 Module de Prévention")

        noms_liste = df['Nom'].unique().tolist()

        patient_choisi = st.selectbox("Sélectionner un patient pour diagnostic", options=noms_liste, key=f"prev_{len(df)}")

        

        if patient_choisi:

            p_data = df[df['Nom'] == patient_choisi].iloc[-1]

            v_imc = p_data['IMC']

            st.write(f"**Diagnostic pour {patient_choisi} :**")

            if v_imc >= 25 or v_imc < 18.5:

                st.error(f"Statut : {p_data['Statut']} (IMC: {v_imc})")

                st.warning(f"Risques : {obtenir_risques(v_imc)}")

            else:

                st.success(f"Statut : {p_data['Statut']} (IMC: {v_imc})")

                st.info(obtenir_risques(v_imc))

    else:

        st.info("Aucune donnée disponible.")



# --- ONGLET 3 : GESTION & MODIFICATION ---

with tab3:

    if not df.empty:

        st.header("Gestion et Modification")

        noms_gestion = df['Nom'].tolist()

        patient_sel = st.selectbox("Patient à modifier ou supprimer", options=noms_gestion, key="gest_sel")

        idx = df[df['Nom'] == patient_sel].index[0]

        

        with st.form("edit_form"):

            e_nom = st.text_input("Nom", value=df.at[idx, 'Nom'])

            if e_nom and any(char.isdigit() for char in e_nom):

                st.warning("⚠️ Attention : Le nom ne doit pas contenir de chiffres.")

            

            col_e1, col_e2 = st.columns(2)

            with col_e1:

                e_age = st.number_input("Âge", value=int(df.at[idx, 'Âge']))

                e_poi = st.number_input("Poids (kg)", value=float(df.at[idx, 'Poids (kg)']))

            with col_e2:

                e_gen = st.selectbox("Genre", ["Masculin", "Féminin", "Autre"], index=["Masculin", "Féminin", "Autre"].index(df.at[idx, 'Genre']))

                e_tai = st.number_input("Taille (cm)", value=int(df.at[idx, 'Taille (cm)']))

            e_ten = st.number_input("Tension", value=int(df.at[idx, 'Tension']))

            

            if st.form_submit_button("Enregistrer les modifications"):

                if e_nom and not any(char.isdigit() for char in e_nom):

                    df_upd = pd.read_csv(DATA_FILE)

                    df_upd.at[idx, 'Nom'] = e_nom

                    df_upd.at[idx, 'Âge'] = e_age

                    df_upd.at[idx, 'Genre'] = e_gen

                    df_upd.at[idx, 'Poids (kg)'] = e_poi

                    df_upd.at[idx, 'Taille (cm)'] = e_tai

                    df_upd.at[idx, 'Tension'] = e_ten

                    df_upd.to_csv(DATA_FILE, index=False)

                    st.success("Modifications enregistrées !")

                    st.rerun()

                else:

                    st.error("Modification impossible : Nom invalide.")

        

        st.markdown("---")

        if st.button("🔴 Supprimer définitivement ce Patient", type="primary"):

            df_del = pd.read_csv(DATA_FILE)

            df_del.drop(idx).to_csv(DATA_FILE, index=False)

            st.warning("Patient supprimé.")

            st.rerun()

    else:

        st.info("Aucun Patient à gérer.")



st.markdown('</div>', unsafe_allow_html=True)