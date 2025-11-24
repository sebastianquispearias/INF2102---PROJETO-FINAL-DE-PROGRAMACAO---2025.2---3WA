import streamlit as st
import pandas as pd

from src.data_loader import load_csv
from src.filters import apply_date_filter, apply_vehicle_filter
from src.metrics import compute_basic_stats, compute_vehicle_ranking
from src.plots import make_nox_histogram, make_nox_boxplot, make_nox_timeseries, make_mean_nox_by_vehicle_bar, make_mean_nox_by_hour_line


st.set_page_config(page_title="Fleet NOx EDA", layout="wide")
st.title("Fleet NOx EDA Dashboard")

st.sidebar.header("Configuração de dados")
uploaded_files = st.sidebar.file_uploader(
    "Suba um ou mais arquivos CSV",
    type=["csv"],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Suba ao menos um CSV para começar.")
    st.stop()

dfs = []
for f in uploaded_files:
    try:
        df_tmp = load_csv(f)
        dfs.append(df_tmp)
    except Exception as e:
        st.error(f"Erro ao carregar {f.name}: {e}")

if not dfs:
    st.error("Nenhum arquivo pôde ser carregado.")
    st.stop()

df = pd.concat(dfs, ignore_index=True)

st.sidebar.subheader("Filtros")

min_ts = df["timestamp"].min()
max_ts = df["timestamp"].max()

start_date, end_date = st.sidebar.date_input(
    "Intervalo de datas",
    value=(min_ts.date(), max_ts.date()),
)

vehicle_ids = sorted(df["vehicle_id"].unique())
selected_vehicles = st.sidebar.multiselect(
    "Veículos",
    options=vehicle_ids,
    default=vehicle_ids,
)

threshold = st.sidebar.number_input(
    "Threshold de NOx",
    min_value=0.0,
    value=50.0,
    step=1.0,
)

df_filtered = apply_date_filter(df, start_date, end_date)
df_filtered = apply_vehicle_filter(df_filtered, selected_vehicles)

if df_filtered.empty:
    st.warning("Nenhum dado após aplicar filtros.")
    st.stop()

stats = compute_basic_stats(df_filtered)

st.subheader("Resumo geral")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Média NOx", f"{stats['global_mean_nox']:.2f}")
col2.metric("Mediana NOx", f"{stats['global_median_nox']:.2f}")
col3.metric("Nº veículos", stats["n_vehicles"])
col4.metric("Nº registros", stats["n_records"])

tab1, tab2, tab3, tab4 = st.tabs(["Histograma", "Boxplot", "Série temporal", "Ranking"])

with tab1:
    fig_hist = make_nox_histogram(df_filtered)
    st.plotly_chart(fig_hist, use_container_width=True)

with tab2:
    fig_box = make_nox_boxplot(df_filtered)
    st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    fig_ts = make_nox_timeseries(df_filtered)
    st.plotly_chart(fig_ts, use_container_width=True)

with tab4:
    ranking_df = compute_vehicle_ranking(df_filtered, threshold)
    st.dataframe(ranking_df)

    csv_ranking = ranking_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar ranking como CSV",
        data=csv_ranking,
        file_name="vehicle_ranking.csv",
        mime="text/csv",
    )
