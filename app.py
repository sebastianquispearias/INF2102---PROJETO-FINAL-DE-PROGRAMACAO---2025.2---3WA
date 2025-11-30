import streamlit as st
import pandas as pd
import pydeck as pdk

from src.data_loader import load_csv
from src.filters import apply_date_filter, apply_vehicle_filter
from src.metrics import compute_basic_stats, compute_vehicle_ranking
from src.plots import make_nox_histogram, make_nox_boxplot, make_nox_timeseries, make_mean_nox_by_vehicle_bar, make_mean_nox_by_hour_line


st.set_page_config(page_title="Fleet NOx EDA", layout="wide")
st.title("Fleet NOx EDA Dashboard")
st.write("Ferramenta simples para explorar dados de NOx da frota.")

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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Histograma", "Boxplot", "Série temporal", "Média por veículo", "Média por hora", "Ranking", "Mapa temporal",])

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
    fig_mean_vehicle = make_mean_nox_by_vehicle_bar(df_filtered)
    st.plotly_chart(fig_mean_vehicle, use_container_width=True)

with tab5:
    fig_mean_hour = make_mean_nox_by_hour_line(df_filtered)
    st.plotly_chart(fig_mean_hour, use_container_width=True)

with tab6:  
    ranking_df = compute_vehicle_ranking(df_filtered, threshold)
    st.subheader("Ranking por veículo")
    st.dataframe(ranking_df)

    csv_ranking = ranking_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar ranking como CSV",
        data=csv_ranking,
        file_name="vehicle_ranking.csv",
        mime="text/csv",
    )

    st.subheader("Métricas globais")

    stats_df = pd.DataFrame(
        [
            {
                "global_mean_nox": stats["global_mean_nox"],
                "global_median_nox": stats["global_median_nox"],
                "n_vehicles": stats["n_vehicles"],
                "n_records": stats["n_records"],
                "threshold_nox": threshold,
            }
        ]
    )

    st.dataframe(stats_df)

    csv_stats = stats_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Baixar métricas globais como CSV",
        data=csv_stats,
        file_name="global_metrics.csv",
        mime="text/csv",
    )
with tab7:
    st.subheader("Mapa temporal (leituras com GPS)")

    required_cols = {"timestamp", "latitude", "longitude", "vehicle_id"}
    if not required_cols.issubset(df_filtered.columns):
        st.info(
            "O conjunto filtrado não contém colunas de timestamp, vehicle_id e latitude/longitude suficientes para o mapa temporal."
        )
    else:
        vehicle_ids_map = sorted(df_filtered["vehicle_id"].unique())
        vehicle_for_map = st.selectbox(
            "Veículo para o mapa",
            options=vehicle_ids_map,
        )

        df_time = df_filtered[df_filtered["vehicle_id"] == vehicle_for_map].copy()
        df_time["timestamp"] = pd.to_datetime(df_time["timestamp"], errors="coerce")
        df_time = df_time.dropna(subset=["timestamp", "latitude", "longitude"])

        if df_time.empty:
            st.info("Não há leituras válidas com timestamp e coordenadas GPS para o veículo selecionado.")
        else:
            min_ts_full = df_time["timestamp"].min()
            max_ts_full = df_time["timestamp"].max()

            total_minutes = max(
                1, int((max_ts_full - min_ts_full).total_seconds() // 60)
            )

            st.write(
                f"Intervalo total disponível para o veículo {vehicle_for_map}: "
                f"de {min_ts_full} até {max_ts_full} "
                f"({total_minutes} minutos aproximadamente)."
            )

            if "minute_index_map" not in st.session_state:
                st.session_state["minute_index_map"] = 0

            step_minutes = st.number_input(
                "Passo (min)",
                min_value=1,
                value=5,
                step=1,
            )

            row = st.columns([10, 1, 1])
            with row[1]:
                back = st.button("⏪", use_container_width=True)
            with row[2]:
                fwd = st.button("⏩", use_container_width=True)

            if back:
                st.session_state["minute_index_map"] = max(
                    0,
                    st.session_state["minute_index_map"] - int(step_minutes),
                )
            if fwd:
                st.session_state["minute_index_map"] = min(
                    total_minutes,
                    st.session_state["minute_index_map"] + int(step_minutes),
                )

            with row[0]:
                minute_index = st.slider(
                    "Minuto desde o início",
                    min_value=0,
                    max_value=total_minutes,
                    value=st.session_state["minute_index_map"],
                )

            st.session_state["minute_index_map"] = minute_index

            window_minutes = st.number_input(
                "Janela de tempo (minutos)",
                min_value=1,
                value=10,
                step=1,
            )

            point_radius = st.number_input(
                "Tamanho do ponto (raio base)",
                min_value=10,
                max_value=200,
                value=40,
                step=5,
            )

            t_end = min_ts_full + pd.Timedelta(minutes=int(minute_index))
            t_start = t_end - pd.Timedelta(minutes=int(window_minutes))

            df_window = df_time[
                (df_time["timestamp"] >= t_start)
                & (df_time["timestamp"] <= t_end)
            ].copy()

            if df_window.empty:
                st.info("Não há leituras na janela de tempo selecionada para esse veículo.")
            else:
                df_window = df_window.sort_values("timestamp")

                MAX_POINTS = 500
                df_plot = df_window.tail(MAX_POINTS).copy()

                df_plot["lat"] = df_plot["latitude"]
                df_plot["lon"] = df_plot["longitude"]
                df_plot["timestamp_str"] = df_plot["timestamp"].astype(str)

                trail_data = df_plot
                latest_point = df_plot.tail(1)

                center_lat = trail_data["lat"].mean()
                center_lon = trail_data["lon"].mean()

                trail_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=trail_data,
                    get_position="[lon, lat]",
                    get_radius=int(point_radius),
                    get_fill_color=[255, 0, 0, 80],
                    pickable=True,
                )

                latest_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=latest_point,
                    get_position="[lon, lat]",
                    get_radius=int(point_radius) * 2,
                    get_fill_color=[0, 255, 0, 255],
                    pickable=True,
                )


                view_state = pdk.ViewState(
                    latitude=center_lat,
                    longitude=center_lon,
                    zoom=11,
                    pitch=0,
                )

                parts = ["<b>Veículo:</b> {vehicle_id}"]
                if "order" in df_plot.columns:
                    parts.append("<b>Order:</b> {order}")
                if "NOx_dp" in df_plot.columns:
                    parts.append("<b>NOx dp:</b> {NOx_dp}")
                if "NOx" in df_plot.columns:
                    parts.append("<b>NOx:</b> {NOx}")
                parts.append("<b>Tempo:</b> {timestamp_str}")
                tooltip_html = "<br/>".join(parts)

                tooltip = {
                    "html": tooltip_html,
                    "style": {"backgroundColor": "steelblue", "color": "white"},
                }

                st.pydeck_chart(
                    pdk.Deck(
                        layers=[trail_layer, latest_layer],
                        initial_view_state=view_state,
                        tooltip=tooltip,
                    )
                )

                st.caption(
                    f"{len(df_plot)} pontos exibidos entre {t_start} e {t_end} "
                    f"para o veículo {vehicle_for_map} "
                    f"(limitado a {MAX_POINTS} pontos mais recentes da janela)."
                )
