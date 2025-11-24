import plotly.express as px


def make_nox_histogram(df):
    """
    Histograma simples dos valores de NOx no período/veículos filtrados.
    """
    fig = px.histogram(
        df,
        x="NOx",
        nbins=10,
        title="Histograma de NOx",
        labels={"NOx": "NOx (ppm)", "count": "Contagem"},
    )
    fig.update_layout(
        bargap=0.05,
    )
    return fig


def make_nox_boxplot(df):
    """
    Boxplot de NOx por veículo para comparar distribuição entre veículos.
    """
    fig = px.box(
        df,
        x="vehicle_id",
        y="NOx",
        title="Boxplot de NOx por veículo",
        labels={"vehicle_id": "Veículo", "NOx": "NOx (ppm)"},
    )
    return fig


def make_nox_timeseries(df):
    """
    Série temporal de NOx, com uma linha por veículo.
    """
    df_sorted = df.sort_values("timestamp")

    fig = px.line(
        df_sorted,
        x="timestamp",
        y="NOx",
        color="vehicle_id",
        title="Série temporal de NOx por veículo",
        labels={
            "timestamp": "Tempo",
            "NOx": "NOx (ppm)",
            "vehicle_id": "Veículo",
        },
    )

    fig.update_layout(legend_title_text="Veículo")
    return fig


def make_mean_nox_by_vehicle_bar(df):
    """
    Gráfico de barras com NOx médio por veículo.
    Útil para comparar rapidamente quais veículos emitem mais NOx em média.
    """
    grouped = df.groupby("vehicle_id", as_index=False)["NOx"].mean()

    fig = px.bar(
        grouped,
        x="vehicle_id",
        y="NOx",
        title="NOx médio por veículo",
        labels={"vehicle_id": "Veículo", "NOx": "NOx médio (ppm)"},
    )
    return fig


def make_mean_nox_by_hour_line(df):
    """
    Linha com NOx médio por hora do dia (0–23).
    Útil para ver em que horários a frota tende a emitir mais.
    """
    # cria coluna de hora (0–23) a partir do timestamp
    df_hour = df.copy()
    df_hour["hour"] = df_hour["timestamp"].dt.hour

    grouped = df_hour.groupby("hour", as_index=False)["NOx"].mean()

    fig = px.line(
        grouped,
        x="hour",
        y="NOx",
        markers=True,
        title="NOx médio por hora do dia",
        labels={"hour": "Hora do dia", "NOx": "NOx médio (ppm)"},
    )
    return fig
