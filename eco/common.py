from pathlib import Path
import hashlib, json, os
BASE = Path(__file__).resolve().parent.parent
NUMERIC = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
CATEGORICAL = ["island", "sex"]
FEATURES = NUMERIC + CATEGORICAL
TARGET = "species"
MODEL_NAME = "EcoSpecies"
def config():
    return json.loads((BASE / "config.json").read_text())
def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tracking_uri():
    return os.getenv("MLFLOW_TRACKING_URI", "sqlite:///" + str(BASE / "mlflow.db"))
def save_json(path, payload):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str))
