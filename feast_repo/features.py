from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, FeatureService
from feast.types import Float64, String
observation=Entity(name="observation",join_keys=["observation_id"])
source=FileSource(path="observations.parquet",timestamp_field="event_timestamp")
measurements=FeatureView(name="measurements",entities=[observation],ttl=timedelta(days=365),schema=[Field(name=n,dtype=Float64) for n in ["bill_length_mm","bill_depth_mm","flipper_length_mm","body_mass_g"]]+[Field(name="island",dtype=String),Field(name="sex",dtype=String)],source=source)
service=FeatureService(name="penguin_features",features=[measurements])
