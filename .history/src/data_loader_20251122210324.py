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
    """Carrega um CSV de telemetria de frota.

    - Aceita caminho (str) ou file-like (ex: UploadedFile do Streamlit).
    - Garante que as colunas obrigatórias existem.
    - Converte timestamp para datetime.
    """
    df = pd.read_csv(path_or_buffer)

    # Normaliza nomes de colunas (ex: timestamp -> timestamp)
    df.columns = [c.strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Faltam colunas obrigatórias no CSV: {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="raise")

    return df
