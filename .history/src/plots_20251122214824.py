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
