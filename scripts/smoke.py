import os, requests
base=os.getenv("API_URL","http://127.0.0.1:8000")
r=requests.post(base+"/api/v1/predict",headers={"X-API-Key":os.environ["API_KEY"]},json={"bill_length_mm":39.1,"bill_depth_mm":18.7,"flipper_length_mm":181,"body_mass_g":3750,"island":"Torgersen","sex":"Male"},timeout=20)
r.raise_for_status();print(r.json())
