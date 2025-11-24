import os
from pathlib import Path

import pandas as pd

from src.data_loader import load_csv


def test_load_csv_with_real_sample():
    # caminho até sample_data/demo_fleet.csv a partir deste arquivo de teste
    base_dir = Path(__file__).resolve().parents[1]
    sample_path = base_dir / "sample_data" / "demo_fleet.csv"

    assert sample_path.exists(), f"Arquivo de exemplo não encontrado em {sample_path}"

    df = load_csv(sample_path)

    # Verifica que temos algumas linhas
    assert len(df) > 0, "DataFrame carregado está vazio, algo deu errado."

    # Verifica se as colunas internas principais existem
    for col in ["timestamp", "vehicle_id", "NOx", "O2", "latitude", "longitude"]:
        assert col in df.columns, f"Coluna esperada '{col}' não encontrada no DataFrame."

    # timestamp deve ser datetime
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"]), "timestamp não está em formato datetime."

    # vehicle_id não deve estar todo vazio
    assert df["vehicle_id"].notna().any(), "Todas as entradas de vehicle_id são NaN, algo está errado."
