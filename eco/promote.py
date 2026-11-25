"""Promotion explicite et export d'un bundle avec version et provenance."""
import argparse, json, os
import joblib, mlflow, mlflow.sklearn
from .common import BASE, MODEL_NAME, tracking_uri, save_json

def main(version, rollback=False):
    mlflow.set_tracking_uri(tracking_uri()); client=mlflow.MlflowClient()
    mv=client.get_model_version(MODEL_NAME,str(version))
    if mv.tags.get("quality_gate")!="passed":
        raise ValueError("Cette version n'a pas passé le contrôle qualité")
    model=mlflow.sklearn.load_model(f"models:/{MODEL_NAME}/{version}")
    target=BASE/"artifacts";target.mkdir(exist_ok=True)
    # Export d'abord, alias ensuite : l'API charge une version figée au démarrage.
    temp=target/"champion.tmp"
    joblib.dump({"model":model,"version":str(version),"run_id":mv.run_id,"model_name":MODEL_NAME},temp)
    os.replace(temp,target/"champion.joblib")
    registered=client.get_registered_model(MODEL_NAME)
    old=registered.aliases.get("champion")
    if old and old!=str(version):client.set_registered_model_alias(MODEL_NAME,"previous",old)
    client.set_registered_model_alias(MODEL_NAME,"champion",str(version))
    save_json(target/"manifest.json",{"version":str(version),"run_id":mv.run_id,"previous":old})
    print(f"Champion version {version}. Redémarrer ou redéployer l'API.")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--version",required=True);a=p.parse_args();main(a.version)
