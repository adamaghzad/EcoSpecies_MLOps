import os, joblib
import numpy as np, pandas as pd, pytest
from fastapi.testclient import TestClient
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from eco.common import BASE, FEATURES
from eco.data import read_validate, normalize, preprocessor
from eco.api import app

def test_data_contract():
    df=read_validate(BASE/"data/penguins.csv")
    assert len(df)==344 and set(df.species)=={"Adelie","Gentoo","Chinstrap"}
def test_invalid_data(tmp_path):
    df=pd.read_csv(BASE/"data/penguins.csv");df.loc[0,"body_mass_g"]=-1
    f=tmp_path/"bad.csv";df.to_csv(f,index=False)
    with pytest.raises(Exception):read_validate(f)
def test_pipeline_and_missing():
    df=read_validate(BASE/"data/penguins.csv")
    model=Pipeline([("prep",preprocessor()),("model",LogisticRegression(max_iter=1000))]).fit(normalize(df[FEATURES]),df.species)
    row=df[FEATURES].iloc[:1].copy();row.loc[row.index[0],"sex"]=None
    assert model.predict(normalize(row))[0] in model.classes_
def test_api(monkeypatch,tmp_path):
    import eco.api as api
    df=read_validate(BASE/"data/penguins.csv")
    model=Pipeline([("prep",preprocessor()),("model",LogisticRegression(max_iter=1000))]).fit(normalize(df[FEATURES]),df.species)
    f=tmp_path/"model.joblib";joblib.dump({"model":model,"version":"test"},f)
    monkeypatch.setattr(api,"BUNDLE",f);monkeypatch.setattr(api,"LOG",tmp_path/"logs.db");monkeypatch.setenv("API_KEY","unit-test-only")
    body={"bill_length_mm":39.1,"bill_depth_mm":18.7,"flipper_length_mm":181,"body_mass_g":3750,"island":"Torgersen","sex":"Male"}
    with TestClient(app) as client:
        assert client.get("/health").status_code==200
        assert client.post("/api/v1/predict",json=body).status_code==401
        headers={"X-API-Key":"unit-test-only"}
        r=client.post("/api/v1/predict",json=body,headers=headers)
        assert r.status_code==200 and r.json()["model_version"]=="test"
        assert client.post("/api/v1/predict",json={**body,"body_mass_g":-1},headers=headers).status_code==422
        assert "eco_predictions_total" in client.get("/metrics").text
