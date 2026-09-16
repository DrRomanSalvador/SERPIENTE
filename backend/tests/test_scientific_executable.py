from datetime import datetime, timezone
import numpy as np
import pytest
from app.scientific_executable import linear_state_transition, observation_projection

T0=datetime(2026,9,16,10,tzinfo=timezone.utc)

def test_linear_state_transition_matches_equation():
    result=linear_state_transition([1.0,2.0],[3.0],[4.0],np.eye(2),np.array([[2.0],[1.0]]),np.array([[1.0],[3.0]]),[0.5,-0.5])
    assert result.next_state == (11.5,16.5)

def test_state_transition_rejects_bad_dimensions():
    with pytest.raises(ValueError): linear_state_transition([1.0],[1.0],[1.0],np.eye(2),np.ones((2,1)),np.ones((2,1)))

def test_observation_projection_is_explicit_measurement_map():
    assert np.allclose(observation_projection([2.0,3.0],[[1.0,0.0],[0.0,2.0]],[1.0,-1.0]),[3.0,5.0])
