"""Orchestration CT : le réentraînement ne promeut jamais automatiquement."""
from prefect import flow, task
from .validate import main as validate
from .train import main as train
@task(retries=1,retry_delay_seconds=2)
def validate_task():
    return validate()
@task(retries=0)
def train_task():
    # Pas de retry automatique : éviter des doublons d'expériences/versions.
    return train()
@flow(name="ecospecies-training",log_prints=True)
def pipeline():
    validate_task()
    return train_task()
if __name__=="__main__":pipeline()
