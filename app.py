import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mock_data import get_mock_data

st.set_page_config(
    page_title="Amazon Product Monitor",
    page_icon="📦",
    layout="wide"
)

st.markdown("""
<style>
    .alert-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 10px 16px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .alert-box-danger {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px 16px;
        border-radius: 4px;
        margin-bottom: 8px;
    }
    .metric-label {
        font-size: 13px;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

df = get_mock_data()

st.title("📦 Amazon Product Monitor")
st.caption("Dashboard di monitoraggio prodotti Amazon — Lenovo vs Competitor")

with st.sidebar:
    st.header("Filtri")
    domini = ["Tutti"] + sorted(df["dominio"].unique().tolist())
    dominio_sel = st.selectbox("Dominio", domini)

    segmenti = ["Tutti"] + sorted(df["segmento_categoria"].unique().tolist())
    segmento_sel = st.selectbox("Categoria", segmenti)

    date_min = df["data_scansione"].min().date()
    date_max = df["data_scansione"].max().date()
    date_range = st.date_input("Periodo", value=(date_min, date_max), min_value=date_min, max_value=date_max)

    owner_sel = st.multiselect("Visualizza", ["LENOVO", "competitor"], default=["LENOVO", "competitor"])

dff = df.copy()
if dominio_sel != "Tutti":
    dff = dff[dff["dominio"] == dominio_sel]
if segmento_sel != "Tutti":
    dff = dff[dff["segmento_categoria"] == segmento_sel]
if len(date_range) == 2:
    dff = dff[(dff["data_scansione"].dt.date >= date_range[0]) & (dff["data_scansione"].dt.date <= date_range[1])]
if owner_sel:
    dff = dff[dff["owner_competitor"].isin(owner_sel)]

tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🥊 Lenovo vs Competitor", "⭐ Sentiment", "🚨 Alert Cambiamenti"])

with tab1:
    st.subheader("Overview prodotti")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Prodotti totali", dff["asin_prodotto"].nunique())
    col2.metric("Brand unici", dff["nome_brand"].nunique())
    col3.metric("Posizione media", round(dff["posizione"].mean(), 1))
    col4.metric("Prezzo medio", f"€{round(dff['prezzo'].mean(), 2)}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Prodotti per brand nel periodo selezionato**")
        brand_count = (
            dff.groupby("nome_brand")["asin_prodotto"]
            .nunique()
            .reset_index()
            .rename(columns={"asin_prodotto": "count"})
            .sort_values("count", ascending=False)
        )
        fig_brand = px.bar(
            brand_count, x="nome_brand", y="count",
            color="nome_brand",
            labels={"nome_brand": "Brand", "count": "N° prodotti"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_brand.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_brand, use_container_width=True)

    with col_b:
        st.markdown("**Distribuzione range di posizione**")
        pos_dist = dff["range_posizione"].value_counts().reset_index()
        pos_dist.columns = ["range", "count"]
        fig_pos = px.pie(
            pos_dist, names="range", values="count",
            color_discrete_sequence=["#2ecc71", "#f39c12", "#e74c3c"]
        )
        fig_pos.update_layout(height=350)
        st.plotly_chart(fig_pos, use_container_width=True)

    st.markdown("**Andamento prodotti per brand nel tempo**")
    trend = (
        dff.groupby(["data_scansione", "nome_brand"])["asin_prodotto"]
        .nunique()
        .reset_index()
        .rename(columns={"asin_prodotto": "count"})
    )
    fig_trend = px.line(
        trend, x="data_scansione", y="count", color="nome_brand",
        labels={"data_scansione": "Data scansione", "count": "N° prodotti", "nome_brand": "Brand"},
        markers=True
    )
    fig_trend.update_layout(height=350)
    st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("Lenovo vs Competitor")

    latest_date = dff["data_scansione"].max()
    dff_latest = dff[dff["data_scansione"] == latest_date]

    col1, col2, col3 = st.columns(3)

    lenovo_count = dff_latest[dff_latest["owner_competitor"] == "LENOVO"]["asin_prodotto"].nunique()
    comp_count = dff_latest[dff_latest["owner_competitor"] == "competitor"]["asin_prodotto"].nunique()
    total = lenovo_count + comp_count

    col1.metric("Prodotti Lenovo", lenovo_count, f"{round(lenovo_count/total*100, 1)}% del totale" if total else "")
    col2.metric("Prodotti Competitor", comp_count, f"{round(comp_count/total*100, 1)}% del totale" if total else "")
    col3.metric("Posizione media Lenovo",
        round(dff_latest[dff_latest["owner_competitor"] == "LENOVO"]["posizione"].mean(), 1))

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Confronto metriche di contenuto**")
        metrics_comp = dff_latest.groupby("owner_competitor").agg(
            img_media=("n_immagini", "mean"),
            titolo_medio=("lunghezza_titolo", "mean"),
            aplus_pct=("presenza_a_plus", "mean"),
            bullet_medi=("n_bullet_points", "mean")
        ).reset_index()
        metrics_comp["aplus_pct"] = (metrics_comp["aplus_pct"] * 100).round(1)
        metrics_comp = metrics_comp.round(1)

        fig_radar = go.Figure()
        for _, row in metrics_comp.iterrows():
            fig_radar.add_trace(go.Bar(
                name=row["owner_competitor"],
                x=["Immagini medie", "Bullet points", "A+ (%)"],
                y=[row["img_media"], row["bullet_medi"], row["aplus_pct"]]
            ))
        fig_radar.update_layout(barmode="group", height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_b:
        st.markdown("**Distribuzione prezzi**")
        fig_box = px.box(
            dff_latest, x="owner_competitor", y="prezzo",
            color="owner_competitor",
            labels={"owner_competitor": "", "prezzo": "Prezzo (€)"},
            color_discrete_map={"LENOVO": "#3498db", "competitor": "#e74c3c"}
        )
        fig_box.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("**Quota di mercato per posizione (ultima scansione)**")
    pos_owner = dff_latest.groupby(["range_posizione", "owner_competitor"])["asin_prodotto"].nunique().reset_index()
    pos_owner.columns = ["range_posizione", "owner_competitor", "count"]
    fig_stack = px.bar(
        pos_owner, x="range_posizione", y="count",
        color="owner_competitor", barmode="stack",
        labels={"range_posizione": "Range posizione", "count": "N° prodotti"},
        color_discrete_map={"LENOVO": "#3498db", "competitor": "#e74c3c"},
        category_orders={"range_posizione": ["1-4", "5-8", "9-60"]}
    )
    fig_stack.update_layout(height=350)
    st.plotly_chart(fig_stack, use_container_width=True)

with tab3:
    st.subheader("Sentiment da rating")

    def sentiment_label(r):
        if r >= 4.5:
            return "Positivo"
        elif r >= 3.5:
            return "Neutro"
        else:
            return "Negativo"

    dff["sentiment"] = dff["rating"].apply(sentiment_label)

    col1, col2, col3 = st.columns(3)
    sent_counts = dff["sentiment"].value_counts()
    col1.metric("Positivo (≥4.5)", sent_counts.get("Positivo", 0))
    col2.metric("Neutro (3.5-4.4)", sent_counts.get("Neutro", 0))
    col3.metric("Negativo (<3.5)", sent_counts.get("Negativo", 0))

    st.markdown("---")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Distribuzione sentiment**")
        sent_dist = dff["sentiment"].value_counts().reset_index()
        sent_dist.columns = ["sentiment", "count"]
        fig_sent = px.pie(
            sent_dist, names="sentiment", values="count",
            color="sentiment",
            color_discrete_map={"Positivo": "#2ecc71", "Neutro": "#f39c12", "Negativo": "#e74c3c"}
        )
        fig_sent.update_layout(height=350)
        st.plotly_chart(fig_sent, use_container_width=True)

    with col_b:
        st.markdown("**Sentiment per brand**")
        sent_brand = dff.groupby(["nome_brand", "sentiment"])["asin_prodotto"].count().reset_index()
        sent_brand.columns = ["nome_brand", "sentiment", "count"]
        fig_sb = px.bar(
            sent_brand, x="nome_brand", y="count",
            color="sentiment", barmode="stack",
            color_discrete_map={"Positivo": "#2ecc71", "Neutro": "#f39c12", "Negativo": "#e74c3c"},
            labels={"nome_brand": "Brand", "count": "N°"}
        )
        fig_sb.update_layout(height=350)
        st.plotly_chart(fig_sb, use_container_width=True)

    st.markdown("**Rating medio per brand nel tempo**")
    rating_trend = dff.groupby(["data_scansione", "nome_brand"])["rating"].mean().reset_index()
    fig_rt = px.line(
        rating_trend, x="data_scansione", y="rating",
        color="nome_brand", markers=True,
        labels={"data_scansione": "Data", "rating": "Rating medio"}
    )
    fig_rt.add_hline(y=4.5, line_dash="dot", line_color="green", annotation_text="Positivo")
    fig_rt.add_hline(y=3.5, line_dash="dot", line_color="orange", annotation_text="Neutro")
    fig_rt.update_layout(height=350)
    st.plotly_chart(fig_rt, use_container_width=True)

with tab4:
    st.subheader("Alert cambiamenti tra scansioni")
    st.caption("Confronto tra scansione corrente e precedente per ogni prodotto")

    dff_sorted = df.sort_values(["asin_prodotto", "dominio", "data_scansione"])
    dff_sorted["prev_aplus"] = dff_sorted.groupby(["asin_prodotto", "dominio"])["presenza_a_plus"].shift(1)
    dff_sorted["prev_immagini"] = dff_sorted.groupby(["asin_prodotto", "dominio"])["n_immagini"].shift(1)
    dff_sorted["prev_titolo"] = dff_sorted.groupby(["asin_prodotto", "dominio"])["lunghezza_titolo"].shift(1)

    alerts = dff_sorted[
        (dff_sorted["prev_aplus"].notna()) & (
            (dff_sorted["presenza_a_plus"] != dff_sorted["prev_aplus"]) |
            (dff_sorted["n_immagini"] != dff_sorted["prev_immagini"]) |
            (dff_sorted["lunghezza_titolo"] != dff_sorted["prev_titolo"])
        )
    ].copy()

    if dominio_sel != "Tutti":
        alerts = alerts[alerts["dominio"] == dominio_sel]
    if segmento_sel != "Tutti":
        alerts = alerts[alerts["segmento_categoria"] == segmento_sel]
    if owner_sel:
        alerts = alerts[alerts["owner_competitor"].isin(owner_sel)]

    st.metric("Cambiamenti rilevati", len(alerts))
    st.markdown("---")

    if len(alerts) == 0:
        st.info("Nessun cambiamento rilevato con i filtri selezionati.")
    else:
        for _, row in alerts.iterrows():
            changes = []
            if row["presenza_a_plus"] != row["prev_aplus"]:
                old = "presente" if row["prev_aplus"] == 1 else "assente"
                new = "presente" if row["presenza_a_plus"] == 1 else "assente"
                changes.append(f"A+ content: {old} → {new}")
            if row["n_immagini"] != row["prev_immagini"]:
                changes.append(f"Immagini: {int(row['prev_immagini'])} → {int(row['n_immagini'])}")
            if row["lunghezza_titolo"] != row["prev_titolo"]:
                changes.append(f"Lunghezza titolo: {int(row['prev_titolo'])} → {int(row['lunghezza_titolo'])} caratteri")

            change_text = " | ".join(changes)
            is_aplus = "presenza_a_plus" in change_text or "A+" in change_text
            css_class = "alert-box-danger" if is_aplus else "alert-box"

            st.markdown(f"""
            <div class="{css_class}">
                <strong>{row['nome_brand']} — {row['asin_prodotto']}</strong>
                &nbsp;&nbsp;<span style="color:#6c757d; font-size:13px">{row['dominio']} | {row['data_scansione'].strftime('%d/%m/%Y')}</span><br>
                {change_text}
            </div>
            """, unsafe_allow_html=True)
