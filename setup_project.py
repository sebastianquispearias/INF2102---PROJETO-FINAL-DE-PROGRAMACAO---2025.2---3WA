import os
from textwrap import dedent

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Carpetas
dirs = [
    "src",
    "sample_data",
    "tests",
]

for d in dirs:
    path = os.path.join(BASE_DIR, d)
    os.makedirs(path, exist_ok=True)

# Archivos de src/
src_files = {
    os.path.join("src", "__init__.py"): "",
    os.path.join("src", "data_loader.py"): dedent("""
        import pandas as pd

        REQUIRED_COLUMNS = [
            "timestamp",
            "vehicle_id",
            "NOx",
            "O2",
            "latitude",
            "longitude",
        ]

        def load_csv(path_or_buffer):
            \"\"\"Carrega um CSV de telemetria de frota.

            - Aceita caminho (str) ou file-like (ex: UploadedFile do Streamlit).
            - Garante que as colunas obrigatórias existem.
            - Converte timestamp para datetime.
            \"\"\"
            df = pd.read_csv(path_or_buffer)

            # Normaliza nomes de colunas (ex: timestamp -> timestamp)
            df.columns = [c.strip() for c in df.columns]

            missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
            if missing:
                raise ValueError(f"Faltam colunas obrigatórias no CSV: {missing}")

            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="raise")

            return df
    """).strip() + "\n",
    os.path.join("src", "filters.py"): dedent("""
        def apply_date_filter(df, start_date, end_date):
            mask = (df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)
            return df.loc[mask]

        def apply_vehicle_filter(df, vehicle_ids):
            if not vehicle_ids:
                return df
            return df[df["vehicle_id"].isin(vehicle_ids)]
    """).strip() + "\n",
    os.path.join("src", "metrics.py"): dedent("""
        import numpy as np

        def compute_basic_stats(df):
            return {
                "global_mean_nox": float(df["NOx"].mean()),
                "global_median_nox": float(df["NOx"].median()),
                "n_vehicles": int(df["vehicle_id"].nunique()),
                "n_records": int(len(df)),
            }

        def compute_vehicle_ranking(df, threshold):
            grouped = df.groupby("vehicle_id")
            stats = []

            for vid, g in grouped:
                mean_nox = g["NOx"].mean()
                median_nox = g["NOx"].median()
                fraction_above = np.mean(g["NOx"] > threshold)
                stats.append({
                    "vehicle_id": vid,
                    "mean_nox": mean_nox,
                    "median_nox": median_nox,
                    "fraction_time_above_threshold": fraction_above,
                })

            import pandas as pd
            ranking_df = pd.DataFrame(stats)
            ranking_df = ranking_df.sort_values(
                by="fraction_time_above_threshold",
                ascending=False
            )
            return ranking_df
    """).strip() + "\n",
    os.path.join("src", "plots.py"): dedent("""
        import plotly.express as px

        def make_nox_histogram(df):
            fig = px.histogram(df, x="NOx", nbins=30, title="Histograma de NOx")
            return fig

        def make_nox_boxplot(df):
            fig = px.box(
                df,
                x="vehicle_id",
                y="NOx",
                title="Boxplot de NOx por veículo",
            )
            return fig

        def make_nox_timeseries(df):
            fig = px.line(
                df.sort_values("timestamp"),
                x="timestamp",
                y="NOx",
                color="vehicle_id",
                title="Série temporal de NOx por veículo",
            )
            return fig
    """).strip() + "\n",
}

# app.py mínimo
app_py_content = dedent("""
    import streamlit as st
    import pandas as pd

    from src.data_loader import load_csv
    from src.filters import apply_date_filter, apply_vehicle_filter
    from src.metrics import compute_basic_stats, compute_vehicle_ranking
    from src.plots import make_nox_histogram, make_nox_boxplot, make_nox_timeseries

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
""").strip() + "\n"

# demo_fleet.csv simples
demo_csv_content = dedent("""\
timestamp,vehicle_id,NOx,O2,latitude,longitude
2025-01-01T08:00:00,TRUCK_01,30,20,-22.90,-43.17
2025-01-01T08:05:00,TRUCK_01,60,21,-22.91,-43.18
2025-01-01T08:10:00,TRUCK_02,45,19,-22.92,-43.16
2025-01-01T08:15:00,TRUCK_02,80,18,-22.93,-43.15
2025-01-01T08:20:00,TRUCK_03,55,20,-22.94,-43.14
""")

# README y requirements
readme_content = dedent("""
    # Fleet NOx EDA

    Aplicação Streamlit para análise exploratória de dados de emissões de NOx em frotas de veículos.
    """)

requirements_content = "streamlit\npandas\nplotly\n"

# tests mínimos
tests_files = {
    os.path.join("tests", "test_metrics.py"): dedent("""
        import pandas as pd
        from src.metrics import compute_basic_stats, compute_vehicle_ranking

        def test_compute_basic_stats_simple():
            df = pd.DataFrame({
                "timestamp": pd.date_range("2025-01-01", periods=3, freq="H"),
                "vehicle_id": ["A", "A", "B"],
                "NOx": [10, 20, 30],
                "O2": [20, 20, 20],
                "latitude": [0, 0, 0],
                "longitude": [0, 0, 0],
            })
            stats = compute_basic_stats(df)
            assert stats["n_vehicles"] == 2
            assert stats["n_records"] == 3

        def test_compute_vehicle_ranking_threshold():
            df = pd.DataFrame({
                "timestamp": pd.date_range("2025-01-01", periods=4, freq="H"),
                "vehicle_id": ["A", "A", "B", "B"],
                "NOx": [10, 60, 70, 40],
                "O2": [20, 20, 20, 20],
                "latitude": [0, 0, 0, 0],
                "longitude": [0, 0, 0, 0],
            })
            ranking = compute_vehicle_ranking(df, threshold=50)
            assert set(ranking.columns) >= {
                "vehicle_id",
                "mean_nox",
                "median_nox",
                "fraction_time_above_threshold"
            }
    """).strip() + "\n"
}

# Crear archivos
files_to_write = {
    "app.py": app_py_content,
    "README.md": readme_content.strip() + "\n",
    "requirements.txt": requirements_content,
    os.path.join("sample_data", "demo_fleet.csv"): demo_csv_content,
}
files_to_write.update(src_files)
files_to_write.update(tests_files)

for rel_path, content in files_to_write.items():
    path = os.path.join(BASE_DIR, rel_path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Estructura del proyecto creada con éxito.")
