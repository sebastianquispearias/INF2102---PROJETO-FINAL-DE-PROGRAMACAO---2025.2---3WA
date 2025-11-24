def apply_date_filter(df, start_date, end_date):
    mask = (df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)
    return df.loc[mask]

def apply_vehicle_filter(df, vehicle_ids):
    if not vehicle_ids:
        return df
    return df[df["vehicle_id"].isin(vehicle_ids)]
