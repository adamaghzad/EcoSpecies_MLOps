def main():
    """Dates de disponibilité fictives pour le TP ; aucun label dans la feature view."""
    from pathlib import Path
    import pandas as pd
    base=Path(__file__).resolve().parent
    frame=pd.read_csv(base.parent/"data/penguins.csv").dropna().reset_index(drop=True)
    frame["sex"]=frame["sex"].str.title()
    frame["observation_id"]=frame.index.astype(str)
    frame["event_timestamp"]=pd.Timestamp.now(tz="UTC")-pd.Timedelta(days=1)
    frame.drop(columns=["species"]).to_parquet(base/"observations.parquet",index=False)
    frame[["observation_id","event_timestamp"]].head(5).to_parquet(base/"entities.parquet",index=False)
    print("Source préparée ; horodatages de démonstration")

if __name__ == "__main__":
    main()
