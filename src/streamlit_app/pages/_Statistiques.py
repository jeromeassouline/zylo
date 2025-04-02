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
        df = df[COLUMNS_TO_KEEP]
        return df
    except FileNotFoundError:
        st.error(f"Fichier non trouvé : {filepath}")
        return pd.DataFrame()


def build_df(
    df: pd.DataFrame,
    group_by: str,
    value_col: str = "CA HT CONSO",
    title_col: str = "Titre",
    sort_order: str = "asc",
) -> pd.DataFrame:
    try:
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
        grouped = df.groupby(group_by)
        summary_df = grouped.agg(
            CA_total=(value_col, "sum"), nb_titres=(title_col, pd.Series.nunique)
        )
        summary_df["CA_moyen_par_titre"] = (
            summary_df["CA_total"] / summary_df["nb_titres"]
        ).round(2)
        summary_df["CA_total"] = summary_df["CA_total"].round(2)
        summary_df = summary_df.sort_index(ascending=(sort_order == "asc"))
        return summary_df.reset_index()
    except KeyError as e:
        st.error(f"Colonne manquante pour le résumé : {e}")
        return pd.DataFrame()


def display_summary(
    df: pd.DataFrame,
    titre: str,
    graph_type: str = "bar",
    label_col: str = "",
    value_col: str = "CA_total",
) -> None:
    """Display title, dataframe and corresponding graph."""
    st.subheader(titre)

    if label_col == "Period":
        df[label_col] = pd.to_datetime(
            df[label_col], format="%m/%d/%y", errors="coerce"
        )
        df = df.sort_values(label_col)

    st.dataframe(df)

    if graph_type == "bar":
        if label_col == "Period":
            # Barres groupées : CA_total + CA_moyen_par_titre
            fig = px.bar(
                df,
                x=label_col,
                y=["CA_total", "CA_moyen_par_titre"],
                barmode="group",
                text_auto=True,
                labels={
                    "value": "Montant",
                    "variable": "Indicateur",
                    label_col: "Période",
                },
            )

            fig.update_layout(xaxis={"tickformat": "%b %Y", "title": "Période"})
        else:
            fig = px.bar(df, x=label_col, y=value_col, text_auto=True)

    elif graph_type == "pie":
        fig = px.pie(df, names=label_col, values=value_col, hole=0.3)

    st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.title("Analytics")
    df = load_csv_to_df("data/data_conso.csv")

    if not df.empty:
        df_period = build_df(df, group_by="Period", sort_order="asc")
        df_famille = build_df(df, group_by="Famille Client", sort_order="asc")
        df_chaines = build_df(df, group_by="Chaîne", sort_order="asc")

        display_summary(
            df_period, "Évolution du CA", graph_type="bar", label_col="Period"
        )
        display_summary(
            df_famille,
            "Répartition du CA par famille de client",
            graph_type="pie",
            label_col="Famille Client",
        )
        display_summary(
            df_chaines,
            "Répartition du CA par chaîne",
            graph_type="pie",
            label_col="Chaîne",
        )


if __name__ == "__main__":
    main()
