import streamlit as st
import pandas as pd
import plotly.express as px

# Configiration de l'application
st.set_page_config(
    page_title="eCO2mix – France vs Auvergne-Rhône-Alpes",
    layout="wide"
)

# Fonctions
# Préparation des dataframes
def prepare_df(df, zone):
    # datetime
    df["datetime"] = pd.to_datetime(
        df["Date"] + " " + df["Heures"],
        errors="coerce"
    )
    df = df.sort_values("datetime")

    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["day"] = df["datetime"].dt.day
    df["hour"] = df["datetime"].dt.hour

    # Jours de semaine
    jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    df["weekday_num"] = df["datetime"].dt.dayofweek
    df["weekday_fr"] = df["weekday_num"].map(dict(enumerate(jours_fr)))
    df["is_weekend"] = df["weekday_fr"].isin(["Samedi", "Dimanche"])

    # Mix énergétique global
    prod_cols = [c for c in [
        "Nucléaire", "Gaz", "Charbon", "Fioul",
        "Hydraulique", "Eolien", "Solaire", "Bioénergies"
    ] if c in df.columns]

    if prod_cols:
        df["production_totale"] = df[prod_cols].sum(axis=1)
    else:
        df["production_totale"] = pd.NA

    # Colonne pour identifier la zone
    df["zone"] = zone

    return df


@st.cache_data
def load_data():
    # Datasets
    df_nat = pd.read_csv("https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/prod/eCO2mix_RTE_Annuel-Definitif.csv")
    df_reg = pd.read_csv("https://renergies99-bucket.s3.eu-west-3.amazonaws.com/public/prod/eCO2mix_RTE_Auvergne-Rhone-Alpes.csv")

    df_nat_prep = prepare_df(df_nat, zone="France")
    df_reg_prep = prepare_df(df_reg, zone="Auvergne-Rhône-Alpes")

    return df_nat_prep, df_reg_prep


# Principes de navigation
st.sidebar.title("Navigation")
mode = st.sidebar.radio(
    "Choix type de dashboard :",
    ["Descriptif", "Prédiction"],
    index=0
)

# Chargement des données en cache
df_nat, df_reg = load_data()


# MODE 1 : DESCRIPTIF
if mode == "Descriptif":

    # Sidebar filtres
    st.sidebar.subheader("Filtres descriptifs")

    vue = st.sidebar.radio(
        "Vue",
        ["France", "Auvergne-Rhône-Alpes", "Comparaison"],
        index=2
    )

    # Filtrage simple
    if vue == "France":
        df_current = df_nat.copy()
    elif vue == "Auvergne-Rhône-Alpes":
        df_current = df_reg.copy()
    else:
        df_current = pd.concat([df_nat, df_reg], ignore_index=True)

    # Sélection période (filtre par année)
    annees_dispo = sorted(df_current["year"].dropna().unique())
    annee_min, annee_max = int(annees_dispo[0]), int(annees_dispo[-1])

    annee_range = st.sidebar.slider(
        "Filtre sur l'année",
        min_value=annee_min,
        max_value=annee_max,
        value=(annee_min, annee_max),
        step=1
    )

    mask_year = (df_current["year"] >= annee_range[0]) & (df_current["year"] <= annee_range[1])
    df_current = df_current[mask_year]

    # Titre principal
    st.title("eCO2mix – Comparaison France / Auvergne-Rhône-Alpes")

    if vue == "Comparaison":
        st.caption("Comparaison des indicateurs entre la France entière et la région Auvergne-Rhône-Alpes.")
    else:
        st.caption(f"Vue détaillée : **{vue}**")

    # ----- Onglets principaux -----
    tab_cons, tab_mix, tab_co2, tab_ech = st.tabs(
        [" Consommation", "Mix énergétique", "CO₂", "Échanges"]
    )

    # 1. Consommation
    with tab_cons:
        st.subheader("Évolution de la consommation")

        # Consommation moyenne quotidienne
        df_daily = (
            df_current.dropna(subset=["Date", "Consommation"])
                     .groupby(["Date", "zone"], as_index=False)["Consommation"]
                     .mean()
        )
        df_daily["Date"] = pd.to_datetime(df_daily["Date"], errors="coerce")

        if vue == "Comparaison":
            fig = px.line(
                df_daily,
                x="Date",
                y="Consommation",
                color="zone",
                title="Consommation moyenne quotidienne – France vs Auvergne-Rhône-Alpes"
            )
        else:
            fig = px.line(
                df_daily,
                x="Date",
                y="Consommation",
                title=f"Consommation moyenne quotidienne – {vue}"
            )

        st.plotly_chart(fig, use_container_width=True)

        # Saisonnalité horaire
        st.markdown("### Profil horaire moyen de consommation")

        df_hour = (
            df_current.dropna(subset=["hour", "Consommation"])
                      .groupby(["hour", "zone"], as_index=False)["Consommation"]
                      .mean()
        )

        if vue == "Comparaison":
            fig2 = px.line(
                df_hour,
                x="hour",
                y="Consommation",
                color="zone",
                markers=True,
                title="Consommation moyenne par heure de la journée"
            )
        else:
            fig2 = px.bar(
                df_hour,
                x="hour",
                y="Consommation",
                title=f"Consommation moyenne par heure de la journée – {vue}"
            )

        st.plotly_chart(fig2, use_container_width=True)

        # Heatmap heure x jour de semaine
        st.markdown("### Consommation moyenne par heure et jour de semaine")

        if vue == "Comparaison":
            zone_heatmap = st.selectbox(
                "Zone pour la heatmap",
                ["France", "Auvergne-Rhône-Alpes"],
                index=0
            )
            df_heat = df_current[df_current["zone"] == zone_heatmap]
        else:
            df_heat = df_current

        pivot = (
            df_heat.dropna(subset=["weekday_fr", "hour", "Consommation"])
                   .groupby(["weekday_fr", "hour"], as_index=False)["Consommation"]
                   .mean()
        )

        # Forcer l'ordre des jours
        jours_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        pivot["weekday_fr"] = pd.Categorical(pivot["weekday_fr"], categories=jours_fr, ordered=True)
        pivot = pivot.sort_values(["weekday_fr", "hour"])

        fig3 = px.density_heatmap(
            pivot,
            x="hour",
            y="weekday_fr",
            z="Consommation",
            nbinsx=24,
            histfunc="avg",
            color_continuous_scale="YlOrRd",
            title=f"Consommation moyenne par heure et jour de semaine – {vue if vue != 'Comparaison' else zone_heatmap}"
        )
        st.plotly_chart(fig3, use_container_width=True)

    # 2. Mix énergétique
    with tab_mix:
        st.subheader("Répartition du mix énergétique")

        prod_cols = [c for c in [
            "Nucléaire", "Gaz", "Charbon", "Fioul",
            "Hydraulique", "Eolien", "Solaire", "Bioénergies"
        ] if c in df_current.columns]

        if not prod_cols:
            st.warning("Colonnes de production non trouvées dans le dataset courant.")
        else:
            mix_global = (
                df_current.groupby("zone")[prod_cols]
                          .mean()
                          .reset_index()
                          .melt(
                              id_vars="zone",
                              value_vars=prod_cols,
                              var_name="source",
                              value_name="production_moyenne"
                          )
            )

            if vue == "Comparaison":
                fig_mix = px.bar(
                    mix_global,
                    x="source",
                    y="production_moyenne",
                    color="zone",
                    barmode="group",
                    title="Production moyenne par filière – France vs Auvergne-Rhône-Alpes"
                )
            else:
                fig_mix = px.pie(
                    mix_global[mix_global["zone"] == df_current["zone"].iloc[0]],
                    names="source",
                    values="production_moyenne",
                    title=f"Répartition moyenne du mix énergétique – {vue}",
                    hole=0.4
                )
                fig_mix.update_traces(textposition="inside", textinfo="percent+label")

            st.plotly_chart(fig_mix, use_container_width=True)

            st.markdown("### Profil horaire moyen de production par filière")

            df_hour_prod = (
                df_current.groupby(["hour", "zone"])[prod_cols]
                          .mean()
                          .reset_index()
                          .melt(
                              id_vars=["hour", "zone"],
                              var_name="source",
                              value_name="production_moyenne"
                          )
            )

            if vue == "Comparaison":
                fig_hp = px.line(
                    df_hour_prod,
                    x="hour",
                    y="production_moyenne",
                    color="source",
                    line_dash="zone",
                    title="Profil horaire moyen de production par filière (France vs Auvergne-Rhône-Alpes)"
                )
            else:
                fig_hp = px.line(
                    df_hour_prod,
                    x="hour",
                    y="production_moyenne",
                    color="source",
                    title=f"Profil horaire moyen de production par filière – {vue}"
                )

            st.plotly_chart(fig_hp, use_container_width=True)

    # 3. CO₂
    with tab_co2:
        st.subheader("Intensité carbone")

        if "Taux de Co2" not in df_current.columns:
            st.info("La colonne 'Taux de Co2' n'est pas disponible dans ce dataset.")
        else:
            df_co2 = df_current.dropna(subset=["datetime", "Taux de Co2"])

            if vue == "Comparaison":
                fig_co2 = px.line(
                    df_co2.sort_values("datetime"),
                    x="datetime",
                    y="Taux de Co2",
                    color="zone",
                    title="Évolution du taux de CO₂ (gCO₂/kWh) – France vs Auvergne-Rhône-Alpes"
                )
            else:
                fig_co2 = px.line(
                    df_co2.sort_values("datetime"),
                    x="datetime",
                    y="Taux de Co2",
                    title=f"Évolution du taux de CO₂ (gCO₂/kWh) – {vue}"
                )

            st.plotly_chart(fig_co2, use_container_width=True)

            # Profil horaire moyen
            st.markdown("### Taux moyen de CO₂ par heure de la journée")

            df_hour_co2 = (
                df_co2.groupby(["hour", "zone"], as_index=False)["Taux de Co2"]
                      .mean()
            )

            if vue == "Comparaison":
                fig_h_co2 = px.line(
                    df_hour_co2,
                    x="hour",
                    y="Taux de Co2",
                    color="zone",
                    markers=True,
                    title="Taux moyen de CO₂ par heure – comparaison des zones"
                )
            else:
                fig_h_co2 = px.bar(
                    df_hour_co2,
                    x="hour",
                    y="Taux de Co2",
                    title=f"Taux moyen de CO₂ par heure – {vue}"
                )

            st.plotly_chart(fig_h_co2, use_container_width=True)

    # 4. Échanges
    with tab_ech:
        st.subheader("Échanges physiques")

        # Colonne commune "Ech. physiques"
        if "Ech. physiques" not in df_current.columns:
            st.info("La colonne 'Ech. physiques' n'est pas disponible dans ce dataset.")
        else:
            df_ech = (
                df_current.groupby(["Date", "zone"], as_index=False)["Ech. physiques"]
                          .mean()
                          .dropna()
            )
            df_ech["Date"] = pd.to_datetime(df_ech["Date"], errors="coerce")

            if vue == "Comparaison":
                fig_ech = px.line(
                    df_ech,
                    x="Date",
                    y="Ech. physiques",
                    color="zone",
                    title="Solde global des échanges physiques (import + / export -)"
                )
            else:
                fig_ech = px.line(
                    df_ech,
                    x="Date",
                    y="Ech. physiques",
                    title=f"Solde global des échanges physiques – {vue}"
                )

            fig_ech.add_hline(y=0, line_dash="dash")
            st.plotly_chart(fig_ech, use_container_width=True)

        st.caption("À faire : ajouter les visualisations détaillant les flux par pays / région")


# MODE 2 : PRÉDICTION
elif mode == "Prédiction":
    st.title("eCO2mix – Module de prédiction")

    st.markdown("""
    Ce module héberge les modèles de prévision.
    """)

    st.info("A développer")