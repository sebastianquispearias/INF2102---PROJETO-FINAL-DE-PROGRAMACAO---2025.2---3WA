import pandas as pd


def _parse_position_to_lat_lon(position_str):
    """
    Converte uma string do tipo 'POINT(lon lat)' em (lat, lon) numéricos.
    Se não conseguir, retorna (None, None).
    """
    if pd.isna(position_str):
        return None, None

    try:
        s = str(position_str).strip()
        if not s.upper().startswith("POINT"):
            return None, None

        # pega o que está entre parênteses: "lon lat"
        inside = s[s.find("(") + 1 : s.find(")")]
        lon_str, lat_str = inside.split()
        lon = float(lon_str)
        lat = float(lat_str)
        # repara: internamente queremos (lat, lon)
        return lat, lon
    except Exception:
        return None, None


def load_csv(path_or_buffer):
    """
    Carrega um CSV de telemetria de frota no formato que você recebeu da empresa
    e o converte para um formato interno padrão usado pelo restante da aplicação.

    Entrada esperada (como no demo_fleet.csv real):
      - vehicle_number
      - vehicle_name
      - timestamp  (em milissegundos desde epoch)
      - NOx
      - O2
      - position   (string 'POINT(lon lat)')
      - outras colunas são mantidas, mas não são obrigatórias

    Saída (DataFrame) garantida:
      - timestamp  (datetime)
      - vehicle_id (string, derivado de vehicle_name ou vehicle_number)
      - NOx        (float)
      - O2         (float)
      - latitude   (float, pode ser NaN se não houver posição válida)
      - longitude  (float, pode ser NaN se não houver posição válida)
      + todas as colunas originais do CSV
    """
    # Lê o CSV
    df = pd.read_csv(path_or_buffer)

    # Normaliza nomes de colunas (tira espaços nas bordas, etc.)
    df.columns = [c.strip() for c in df.columns]

    # --- vehicle_id ---------------------------------------------------------
    if "vehicle_id" in df.columns:
        df["vehicle_id"] = df["vehicle_id"].astype(str)
    elif "vehicle_name" in df.columns:
        df["vehicle_id"] = df["vehicle_name"].astype(str)
    elif "vehicle_number" in df.columns:
        df["vehicle_id"] = df["vehicle_number"].astype(str)
    else:
        raise ValueError(
            "Não encontrei nenhuma coluna de veículo "
            "(vehicle_id, vehicle_name ou vehicle_number)."
        )

    # --- timestamp ----------------------------------------------------------
    if "timestamp" not in df.columns:
        raise ValueError("Coluna 'timestamp' não encontrada no CSV.")

    # Se for numérico, assumimos que está em milissegundos desde epoch
    if pd.api.types.is_numeric_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", errors="raise")
    else:
        # Se já vier como string legível (ISO etc.), apenas converte
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="raise")

    # --- NOx ----------------------------------------------------------------
    if "NOx" not in df.columns:
        raise ValueError("Coluna 'NOx' não encontrada no CSV.")
    df["NOx"] = pd.to_numeric(df["NOx"], errors="coerce")

    # --- O2 -----------------------------------------------------------------
    if "O2" not in df.columns:
        raise ValueError("Coluna 'O2' não encontrada no CSV.")
    df["O2"] = pd.to_numeric(df["O2"], errors="coerce")

    # --- latitude / longitude ----------------------------------------------
    if "latitude" in df.columns and "longitude" in df.columns:
        # Se algum dia você tiver CSVs já com lat/long separadas
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    elif "position" in df.columns:
        lats = []
        lons = []
        for pos in df["position"]:
            lat, lon = _parse_position_to_lat_lon(pos)
            lats.append(lat)
            lons.append(lon)
        df["latitude"] = lats
        df["longitude"] = lons
    else:
        # Se não houver nada de localização, preenche com NaN
        df["latitude"] = pd.NA
        df["longitude"] = pd.NA

    # Remove linhas sem timestamp ou NOx válido, para evitar erros nos gráficos
    df = df.dropna(subset=["timestamp", "NOx"])

    return df
