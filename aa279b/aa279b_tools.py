import numpy as np
from numpy.linalg import norm
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from lamberthub import vallado2013
import plotly.graph_objects as go
from tqdm import tqdm

from constants import DEG_TO_RAD, MU_EARTH

def wrap_to_pi(x):
  return (x + np.pi) % (2 * np.pi) - np.pi

def kepler(M, e):
    """Vallado 4e eq. 2-4 p. 45 (pdf p. 72)"""
    E = fsolve(lambda E: E - e * np.sin(E) - M, M)[0]
    return E


def dcm_x(theta):
    """theta: angle of frame 2 wrt frame 1"""
    return np.array(
        [
            [1, 0, 0],
            [0, np.cos(theta), np.sin(theta)],
            [0, -np.sin(theta), np.cos(theta)],
        ]
    )


def dcm_y(theta):
    """theta: angle of frame 2 wrt frame 1"""
    return np.array(
        [
            [np.cos(theta), 0, -np.sin(theta)],
            [0, 1, 0],
            [np.sin(theta), 0, np.cos(theta)],
        ]
    )


def dcm_z(theta):
    """theta: angle of frame 2 wrt frame 1"""
    return np.array(
        [
            [np.cos(theta), np.sin(theta), 0],
            [-np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )


def rv_from_coe(a, e, i, raan, aop, M, mu) -> tuple[np.ndarray, np.ndarray]:
    """Vallado 4e Algorithm 10 p. 118 (pdf p. 145)"""

    # semiparameter - Vallado 4e p. 96 (pdf p. 123)
    p = a * (1 - e * e)

    E = kepler(M, e)

    # true anomaly - Vallado 4e. eq. 2-10 p. 47 (pdf p. 74)
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))
    r_pqw = np.array([p * np.cos(nu), p * np.sin(nu), 0]) / (1 + e * np.cos(nu))

    v_pqw = np.array([-np.sin(nu), e + np.cos(nu), 0]) * np.sqrt(mu / p)

    dcm_ijk_wrt_pqw = dcm_z(-raan) @ dcm_x(-i) @ dcm_z(-aop)
    r_ijk = dcm_ijk_wrt_pqw @ r_pqw
    v_ijk = dcm_ijk_wrt_pqw @ v_pqw

    return r_ijk, v_ijk


# Vallado 4e example 2-6 p. 119 (pdf p. 146)
assert np.allclose(
    np.array(
        rv_from_coe(
            a=36126.6428348052,
            e=0.83285,
            i=87.87 * DEG_TO_RAD,
            raan=227.89 * DEG_TO_RAD,
            aop=53.38 * DEG_TO_RAD,
            M=7.60494 * DEG_TO_RAD,
            mu=MU_EARTH,
        )
    ),
    np.array([[6525.344, 6861.535, 6449.125], [4.902276, 5.533124, -1.975709]]),
)
