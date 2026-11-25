"""Contrat des données et prétraitement partagé train/inférence."""
import numpy as np
import pandas as pd
import pandera.pandas as pa
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .common import NUMERIC, CATEGORICAL, TARGET, config
RANGES={"bill_length_mm":(20,80),"bill_depth_mm":(5,35),"flipper_length_mm":(100,300),"body_mass_g":(1000,10000)}
def schema():
    columns={name:pa.Column(float, checks=pa.Check.in_range(*RANGES[name]), nullable=True, coerce=True) for name in NUMERIC}
    columns.update({"island":pa.Column(str,pa.Check.isin(["Biscoe","Dream","Torgersen"])),"sex":pa.Column(str,pa.Check.isin(["Male","Female"]),nullable=True),TARGET:pa.Column(str,pa.Check.isin(["Adelie","Chinstrap","Gentoo"]))})
    return pa.DataFrameSchema(columns,strict=True)
def read_validate(path):
    df=pd.read_csv(path)
    # Harmoniser la casse sans remplacer les valeurs absentes.
    if "sex" in df: df["sex"]=df["sex"].str.title()
    df=schema().validate(df,lazy=True)
    if df.isna().mean().max()>config()["max_missing_fraction"]:
        raise ValueError("Trop de valeurs manquantes")
    if len(df)<100 or df[TARGET].value_counts().min()<20:
        raise ValueError("Dataset trop petit ou classe insuffisante")
    return df

def normalize(frame):
    # Les valeurs JSON nulles deviennent NaN, comme lors de la lecture CSV.
    df=frame.copy()
    for col in NUMERIC:
        df[col]=pd.to_numeric(df[col],errors="raise")
    for col in CATEGORICAL:
        df[col]=df[col].astype(object).where(df[col].notna(),np.nan)
    return df

def preprocessor():
    numeric=Pipeline([("impute",SimpleImputer(strategy="median")),("scale",StandardScaler())])
    categorical=Pipeline([("impute",SimpleImputer(strategy="most_frequent")),("encode",OneHotEncoder(handle_unknown="ignore",sparse_output=False))])
    return ColumnTransformer([("numeric",numeric,NUMERIC),("category",categorical,CATEGORICAL)])
