from datetime import datetime, timedelta, timezone

from app.contracts import Observation
from app.supervised import LongitudinalSupervisedFrameBuilder


def make(i: int, risk: int, x: float):
    t = datetime(2026,1,1,tzinfo=timezone.utc) + timedelta(days=i)
    return [
        Observation("s","d","risk","binary future risk","state", "Ceuta", t,t,t,"v1",0,float(risk),("official:risk",)),
        Observation("s","d","x","predictor","unit", "Ceuta", t,t,t,"v1",0,x,("official:x",)),
    ]


def test_future_target_is_separated_from_origin_features():
    observations = [item for i in range(12) for item in make(item, item % 2, float(item))]
    frame = LongitudinalSupervisedFrameBuilder().build(observations, target_variable="risk", horizon_steps=1)
    assert (frame["target_time"] > frame["time"]).all()
    assert frame["target"].isin([0.0, 1.0]).all()
