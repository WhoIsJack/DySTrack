# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 00:31:36 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `constraints.py`.
"""

import os
from time import sleep

import numpy as np
import pytest

from dystrack.pipelines.utilities import constraints


def test_constrain_z_movement():
    """Test image analysis pipelien output constraint on z-movement."""

    # Check cases requiring no change
    assert 9.5 == constraints.constrain_z_movement(9.5, 21)
    assert 13.5 == constraints.constrain_z_movement(13.5, 21, limit_fract=0.2)

    # Check too much negative movement
    with pytest.warns(UserWarning) as w:
        z_out = constraints.constrain_z_movement(6.0, 25)
    assert z_out == 9.6
    assert "using z_limit_bot!" in w[0].message.args[0]

    # Check again to ensure warning is re-emitted
    with pytest.warns(UserWarning) as w:
        z_out = constraints.constrain_z_movement(6.0, 25)

    # Check too much positive movement
    with pytest.warns(UserWarning) as w:
        z_out = constraints.constrain_z_movement(29, 41, limit_fract=0.2)
    assert z_out == 28.0
    assert "using z_limit_top!" in w[0].message.args[0]
