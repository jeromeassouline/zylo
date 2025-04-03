from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

COLUMNS_TO_KEEP = [
    "Titre",
    "Period",
    "Famille Client",
    "Chaîne",
    "Intitulé Client",
    "Ayant Droit Airtable2",
    "CA HT CONSO",
    "To exclud",
]


def load_csv_to_df(filepath: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(filepath, low_memory=False)
        df = df[df["To exclud"].fillna("").str.lower() != "yes"]
        df = df[COLUMNS_TO_KEEP]
        df["CA HT CONSO"] = pd.to_numeric(df["CA HT CONSO"], errors="coerce")
        df["views"] = np.random.randint(5000, 100001, size=len(df))
        df["Period"] = pd.to_datetime(df["Period"], errors="coerce", format="%m/%d/%y")
        df["Period_fmt"] = df["Period"].dt.strftime("%B %Y")
        return df
    except FileNotFoundError:
        st.error(f"Fichier non trouvé : {filepath}")
        return pd.DataFrame()
    except KeyError as e:
        st.error(f"Colonne manquante : {e}")
        return pd.DataFrame()


df_raw = load_csv_to_df("data/data_conso.csv")
df = df_raw[df_raw["Ayant Droit Airtable2"] == "ASYLUM"]

if not df.empty:
    all_periods = df["Period_fmt"].dropna().unique()
    all_periods_sorted = sorted(
        all_periods, key=lambda x: pd.to_datetime(x, format="%B %Y")
    )
    df_valid_titles = df[df["CA HT CONSO"].fillna(0) > 0]
    all_titles = df_valid_titles["Titre"].dropna().unique()
    title_options = ["(Aucun filtre)", *sorted(all_titles.tolist())]
    selected_title = st.selectbox("🎬 Filtrer par Titre :", options=title_options)

    if selected_title != "(Aucun filtre)":
        df_title = df[df["Titre"] == selected_title]
    else:
        df_title = df.copy()

    df_graph = df_title.copy()

    filter_options = {
        "(Aucun filtre)": None,
        "7 derniers jours": 7,
        "30 derniers jours": 30,
        "45 derniers jours": 45,
        "90 derniers jours": 90,
    }
    selected_label = st.selectbox("📅 Select a period", list(filter_options.keys()))
    days = filter_options[selected_label]
    if days is not None:
        latest_date = df_title["Period"].max()
        date_limit = latest_date - timedelta(days=days)
        df_filtered = df_title[df_title["Period"] >= date_limit]
    else:
        df_filtered = df_title.copy()

    if not df_filtered.empty:
        views_this_period = int(df_filtered["views"].sum())
        revenue_this_period = int(df_filtered["CA HT CONSO"].sum())
    else:
        views_this_period = 50000
        revenue_this_period = 100000

    st.subheader("📊 Analytics Overview")

    col1, col2 = st.columns(2)
    col1.metric(label="👁️ Views", value=f"{views_this_period:,}")
    col2.metric(label="💰 Revenues", value=f"{revenue_this_period:,}")

    df_grouped = (
        df_graph.groupby("Period_fmt")
        .agg({"views": "sum", "CA HT CONSO": "sum"})
        .reindex(all_periods_sorted, fill_value=0)
        .reset_index()
    )

    tab1, tab2 = st.tabs(["👁️ Views", "💰 Revenues"])

    with tab1:
        fig_views = px.line(
            df_grouped, x="Period_fmt", y="views", markers=True, title="Views"
        )
        fig_views.update_layout(
            title={"x": 0.45}, xaxis_title=None, yaxis_title="Views"
        )
        st.plotly_chart(fig_views, use_container_width=True)

    with tab2:
        fig_ca = px.line(
            df_grouped, x="Period_fmt", y="CA HT CONSO", markers=True, title="Revenue"
        )
        fig_ca.update_layout(title={"x": 0.45}, xaxis_title=None, yaxis_title="Revenue")
        st.plotly_chart(fig_ca, use_container_width=True)
