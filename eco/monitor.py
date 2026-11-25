"""Dérive simulée et vraie qualité uniquement si les labels sont disponibles."""
import argparse,json
import numpy as np,pandas as pd
from scipy.stats import ks_2samp
from evidently import Report
from evidently.presets import DataDriftPreset
from sklearn.metrics import f1_score
from .common import BASE, NUMERIC, save_json

def main(current=None):
    reference=pd.read_csv(BASE/"data/penguins.csv")[NUMERIC].dropna()
    if current:
        observed=pd.read_csv(current)[NUMERIC].dropna(); simulated=False
    else:
        observed=reference.sample(n=150,random_state=7).copy()
        observed["body_mass_g"]+=1200;simulated=True
    if min(len(reference),len(observed))<50:raise ValueError("Au moins 50 observations par groupe")
    # Rapport Evidently autonome ; résultat statistique != preuve de baisse de qualité.
    snapshot=Report([DataDriftPreset()]).run(current_data=observed,reference_data=reference)
    (BASE/"reports").mkdir(exist_ok=True)
    snapshot.save_html(str(BASE/"reports/drift.html"))
    pvalues={c:float(ks_2samp(reference[c],observed[c]).pvalue) for c in NUMERIC}
    threshold=.01/len(NUMERIC)  # Bonferroni pour les 4 comparaisons de ce TP.
    save_json(BASE/"reports/drift.json",{"simulated":simulated,"ks_pvalues":pvalues,"threshold":threshold,"alert":any(p<threshold for p in pvalues.values()),"performance_known":False})
    print("Rapport reports/drift.html ; données simulées" if simulated else "Rapport sur le CSV fourni")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--current");a=p.parse_args();main(a.current)
