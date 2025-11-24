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

    # Deixa a legenda mais limpa
    fig.update_layout(legend_title_text="Veículo")
    return fig
