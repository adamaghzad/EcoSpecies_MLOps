"""API de prédiction authentifiée, métriques techniques et journal SQLite."""
from contextlib import asynccontextmanager
from pathlib import Path
import json, os, secrets, sqlite3, time, uuid
import joblib
import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from .common import BASE, FEATURES
from .data import normalize
BUNDLE=Path(os.getenv("MODEL_PATH",str(BASE/"artifacts/champion.joblib")))
LOG=Path(os.getenv("PREDICTION_DB",str(BASE/".state/predictions.db")))
COUNT=Counter("eco_predictions_total","Prédictions réussies")
LATENCY=Histogram("eco_prediction_seconds","Latence de prédiction",buckets=(.005,.01,.025,.05,.1,.25,.5,1))
ERRORS=Counter("eco_errors_total","Erreurs HTTP",["status"])
@asynccontextmanager
async def lifespan(app):
    if not os.getenv("API_KEY"):raise RuntimeError("Définir API_KEY avant de démarrer")
    app.state.bundle=joblib.load(BUNDLE)  # Artefact construit et vérifié localement.
    LOG.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(LOG) as db:
        db.execute("CREATE TABLE IF NOT EXISTS predictions(request_id TEXT PRIMARY KEY, timestamp TEXT DEFAULT CURRENT_TIMESTAMP, model_version TEXT, features TEXT, prediction TEXT)")
    yield
app=FastAPI(title="EcoSpecies API",version="1.0.0",lifespan=lifespan)
class Penguin(BaseModel):
    model_config=ConfigDict(extra="forbid",allow_inf_nan=False)
    bill_length_mm:float|None=Field(default=None,ge=20,le=80)
    bill_depth_mm:float|None=Field(default=None,ge=5,le=35)
    flipper_length_mm:float|None=Field(default=None,ge=100,le=300)
    body_mass_g:float|None=Field(default=None,ge=1000,le=10000)
    island:str=Field(pattern="^(Biscoe|Dream|Torgersen)$")
    sex:str|None=Field(default=None,pattern="^(Male|Female)$")
def auth(x_api_key:str|None=Header(default=None)):
    if not secrets.compare_digest(x_api_key or "",os.environ.get("API_KEY","")):
        raise HTTPException(401,"Clé absente ou invalide")
@app.middleware("http")
async def count_errors(request,call_next):
    response=await call_next(request)
    if response.status_code>=400:ERRORS.labels(status=str(response.status_code)).inc()
    return response
@app.get("/health")
def health():return {"status":"ok"}
@app.get("/ready")
def ready():return {"ready":True,"model_version":app.state.bundle["version"]}
@app.get("/metrics",include_in_schema=False)
def metrics():return Response(content=generate_latest(),headers={"Content-Type":CONTENT_TYPE_LATEST})
@app.post("/api/v1/predict",dependencies=[Depends(auth)])
def predict(values:Penguin):
    started=time.perf_counter();features=values.model_dump()
    if all(features[k] is None for k in FEATURES[:4]):raise HTTPException(422,"Au moins une mesure physique est requise")
    frame=normalize(pd.DataFrame([features],columns=FEATURES))
    bundle=app.state.bundle;prediction=str(bundle["model"].predict(frame)[0]);rid=str(uuid.uuid4())
    with sqlite3.connect(LOG) as db:
        db.execute("INSERT INTO predictions(request_id,model_version,features,prediction) VALUES(?,?,?,?)",(rid,bundle["version"],json.dumps(features),prediction))
    COUNT.inc();LATENCY.observe(time.perf_counter()-started)
    return {"request_id":rid,"species":prediction,"model_version":bundle["version"]}
