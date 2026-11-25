"""Comparer sur validation ; ouvrir le test une seule fois pour le candidat choisi."""
import json, platform
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, classification_report
from .data import read_validate, normalize, preprocessor
from .common import BASE, FEATURES, TARGET, MODEL_NAME, config, tracking_uri, save_json, digest

def main():
    cfg=config(); df=read_validate(BASE/"data/penguins.csv")
    X,y=normalize(df[FEATURES]),df[TARGET]
    X_dev,X_test,y_dev,y_test=train_test_split(X,y,test_size=.2,stratify=y,random_state=cfg["seed"])
    X_train,X_val,y_train,y_val=train_test_split(X_dev,y_dev,test_size=.25,stratify=y_dev,random_state=cfg["seed"])
    mlflow.set_tracking_uri(tracking_uri());mlflow.set_experiment("EcoSpecies")
    candidates={"logistic":LogisticRegression(max_iter=1000,random_state=42),"forest":RandomForestClassifier(n_estimators=120,min_samples_leaf=2,random_state=42)}
    baseline=Pipeline([("prep",preprocessor()),("classifier",DummyClassifier(strategy="most_frequent"))]).fit(X_train,y_train)
    baseline_f1=f1_score(y_val,baseline.predict(X_val),average="macro")
    results=[]
    for name, classifier in candidates.items():
        with mlflow.start_run(run_name=name) as run:
            model=Pipeline([("prep",preprocessor()),("classifier",classifier)])
            model.fit(X_train,y_train)
            score=f1_score(y_val,model.predict(X_val),average="macro")
            mlflow.log_params({"algorithm":name,"seed":cfg["seed"],"train_rows":len(X_train),"validation_rows":len(X_val)})
            mlflow.set_tags({"data_sha256":digest(BASE/"data/penguins.csv"),"config_sha256":digest(BASE/"config.json"),"python":platform.python_version()})
            mlflow.log_metrics({"validation_f1_macro":score,"baseline_validation_f1_macro":baseline_f1})
            info=mlflow.sklearn.log_model(model,name="model",serialization_format="cloudpickle",signature=infer_signature(X_train,model.predict(X_train)),input_example=X_train.head(2))
            results.append({"algorithm":name,"score":score,"run_id":run.info.run_id,"uri":info.model_uri,"model":model})
    best=max(results,key=lambda r:r["score"])
    # Le test n'est pas utilisé pour choisir entre les deux candidats.
    predictions=best["model"].predict(X_test)
    test_f1=f1_score(y_test,predictions,average="macro")
    passed=best["score"]>=cfg["min_validation_f1"] and best["score"]>baseline_f1 and test_f1>=cfg["min_test_f1"]
    with mlflow.start_run(run_id=best["run_id"]):
        mlflow.log_metrics({"test_f1_macro":test_f1,"test_accuracy":accuracy_score(y_test,predictions)})
        mlflow.set_tag("quality_gate", "passed" if passed else "failed")
    version=mlflow.register_model(best["uri"],MODEL_NAME)
    mlflow.MlflowClient().set_model_version_tag(MODEL_NAME,version.version,"quality_gate","passed" if passed else "failed")
    report={"version":str(version.version),"run_id":best["run_id"],"model_name":MODEL_NAME,"algorithm":best["algorithm"],"validation_f1":best["score"],"baseline_validation_f1":baseline_f1,"test_f1":test_f1,"passed":passed,"data_sha256":digest(BASE/"data/penguins.csv"),"test_report":classification_report(y_test,predictions,output_dict=True),"splits":{"train":len(X_train),"validation":len(X_val),"test":len(X_test)}}
    save_json(BASE/"reports/candidate.json",report)
    print(json.dumps({k:v for k,v in report.items() if k!="test_report"},indent=2))
    if not passed:raise RuntimeError("Candidat refusé ; champion inchangé")
    return report
if __name__=="__main__":main()
