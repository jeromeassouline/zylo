from datetime import timedelta

import pandas as pd
import streamlit as st

COLUMNS_TO_KEEP = [
    "Titre",
    "Period",
    "Famille Client",
    "Chaîne",
    "Intitulé Client",
    "Ayant Droit Airtable2",
    "CA HT CONSO",
    "Contrat",
    "To exclud",
]


def load_csv_to_df(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath, low_memory=False)
        df = df[df["To exclud"].fillna("").str.lower() != "yes"]
        df = df[COLUMNS_TO_KEEP]
        df["Period"] = pd.to_datetime(df["Period"], errors="coerce", format="%m/%d/%y")
        df["Mois_Année"] = df["Period"].dt.strftime("%B %Y")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return pd.DataFrame()


st.title("📁 Vos décomptes")

df_raw = load_csv_to_df("data/data_conso.csv")
df = df_raw[df_raw["Ayant Droit Airtable2"] == "ASYLUM"]  # 🎯 Filtrage imposé

if not df.empty:
    # Filtre sur les 6 derniers mois
    latest_date = df["Period"].max()
    six_months_ago = latest_date - timedelta(days=180)
    df = df[df["Period"] >= six_months_ago]

    # Sélection du contrat (directement lié à "ASYLUM")
    contrats = df["Contrat"].dropna().unique()
    selected_contrat = st.selectbox("📑 Sélectionner un Contrat :", sorted(contrats))

    # Filtrage final
    df_final = df[df["Contrat"] == selected_contrat]

    # Mois disponibles
    mois_disponibles: list[str] = df_final["Mois_Année"].dropna().unique().tolist()
    mois_disponibles = sorted(
        mois_disponibles, key=lambda x: pd.to_datetime(x, format="%B %Y"), reverse=True
    )

    st.markdown("### 📦 Reporting à télécharger")

    for mois in mois_disponibles:
        df_filtered = df_final[df_final["Mois_Année"] == mois]

        if not df_filtered.empty:
            csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")

            st.download_button(
                label=f"⬇️ {mois} - Reporting FR",
                data=csv_bytes,
                file_name=f"{mois} - Reporting FR.csv",
                mime="text/csv",
            )
