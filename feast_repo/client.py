def main():
    import json, os
    import pandas as pd, requests
    from feast import FeatureStore
    store=FeatureStore(repo_path=".")
    service=store.get_feature_service("penguin_features")
    # Jointure historique point-in-time ; mêmes noms de caractéristiques qu'en ligne.
    entities=pd.read_parquet("entities.parquet")
    historical=store.get_historical_features(entity_df=entities,features=service).to_df()
    print("Historique",historical.shape)
    features=store.get_online_features(features=service,entity_rows=[{"observation_id":"0"}]).to_dict()
    values={k:v[0] for k,v in features.items() if k!="observation_id"}
    if any(v is None for v in values.values()):raise RuntimeError("Valeurs non matérialisées")
    print(json.dumps(values,indent=2))
    if os.getenv("API_KEY"):
        r=requests.post("http://127.0.0.1:8000/api/v1/predict",json=values,headers={"X-API-Key":os.environ["API_KEY"]},timeout=20)
        r.raise_for_status();print(r.json())

if __name__ == "__main__":
    main()
