"""Rattache des labels réels au journal ; n'invente pas les réponses correctes."""
import argparse, sqlite3
import pandas as pd
from sklearn.metrics import f1_score
from .api import LOG
from .common import BASE, save_json

def main(labels_path):
    labels=pd.read_csv(labels_path,dtype={"request_id":str})
    if labels.request_id.duplicated().any():raise ValueError("request_id dupliqué dans les labels")
    if not set(labels.species).issubset({"Adelie","Gentoo","Chinstrap"}):raise ValueError("Espèce invalide")
    with sqlite3.connect(LOG) as db:pred=pd.read_sql_query("SELECT request_id,model_version,prediction FROM predictions",db)
    merged=pred.merge(labels,on="request_id",validate="one_to_one")
    if merged.empty:raise ValueError("Aucun label correspondant")
    scores={str(v):{"rows":len(g),"f1_macro":float(f1_score(g.species,g.prediction,average="macro",labels=["Adelie","Chinstrap","Gentoo"],zero_division=0))} for v,g in merged.groupby("model_version")}
    save_json(BASE/"reports/performance.json",{"coverage":len(merged)/max(len(pred),1),"by_model":scores})
    print(scores)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--labels",required=True);a=p.parse_args();main(a.labels)
