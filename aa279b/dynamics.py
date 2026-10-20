import numpy as np
from constants import MU_EARTH, MU_MOON, R_BC_EARTH, R_BC_MOON, W_EARTH_MOON, J2_EARTH, R_EARTH

def two_body(state: np.ndarray, mu=MU_EARTH) -> np.ndarray:
    """Two body dynamics
    
    [x, y, z, vx, vy, vz] -> [vx, vy, vz, ax, ay, az]

    Parameters
    ----------
    state : np.ndarray
        State - `[x, y, z, vx, vy, vz]`
    mu : float, optional
        Gravitational parameter of central body, by default `MU_EARTH` [km3/s2]

    Returns
    -------
    x_dot : np.ndarray (6,)
        State derivative - `[vx, vy, vz, ax, ay, az]`
    """
    r,v = state[0:3], state[3:6]
    a = -mu / np.linalg.norm(r)**3 * r
    state_dot = np.concatenate((v,a))
    
    return state_dot

def two_body_with_J2(state: np.ndarray, mu=MU_EARTH, j2=J2_EARTH, r_body=R_EARTH) -> np.ndarray:
    """Two body with J2. See `two_body()` docstring
    
    [x, y, z, vx, vy, vz] -> [vx, vy, vz, ax, ay, az]

    Additional Parameters from `two_body()`
    ----------
    j2 : float, optional
        J2 constant, by default `J2_EARTH`
    r_body : float, optional
        Equatorial radius of central body [km], by default `R_EARTH`
    """
    state_dot = two_body(state,mu)
    
    norm_r = np.linalg.norm(state[0:3])
    r_hat = state[0:3] / norm_r
    k_hat = np.array([0,0,1])
    z = state[2]
    
    a_J2 = -(mu*j2*r_body*r_body/2) * (
        6*z/norm_r**5 * k_hat +
        (3/norm_r**4 - 15*z*z/norm_r**6) * r_hat
    )
    state_dot[3:6] += a_J2
    return state_dot


def synodic_dynamics(state: np.ndarray, mu1: float, mu2: float, r1_bc: float, r2_bc: float, w_s: float) -> np.ndarray:
    """Circular restricted three-body problem (CR3BP). Constant `w_s` and circular orbits
    
    [x, y, z, vx, vy, vz] -> [vx, vy, vz, ax, ay, az]

    Parameters
    ----------
    state : np.ndarray
        State - `[x, y, z, vx, vy, vz]`
    mu1 : float
        Gravitational parameter of larger central body [km3/s2]
    mu2 : float
        Gravitational parameter of smaller central body [km3/s2]
    r1_bc : float
        Distance from larger central body to barycenter [km]
    r2_bc : float
        Distance from smaller central body to barycenter [km]
    w_s : float
        Angular velocity of system [rad/s]

    Returns
    -------
    state_dot : np.ndarray (6,)
        State derivative - `[vx, vy, vz, ax, ay, az]`
    """
    
    assert mu1 > mu2
    assert r1_bc < r2_bc
    
    x, y, z, x_dot, y_dot, z_dot = state
    
    r_1_sat = np.sqrt((x + r1_bc)**2 + y**2 + z**2)
    r_2_sat = np.sqrt((x - r2_bc)**2 + y**2 + z**2)
    
    x_ddot = (
        -mu1 * (x + r1_bc) / (r_1_sat**3)
        -mu2 * (x - r2_bc) / (r_2_sat**3)
        + 2 * w_s * y_dot
        + w_s**2 * x)
    
    y_ddot = (
        -mu1 * y / (r_1_sat**3)
        -mu2 * y / (r_2_sat**3)
        - 2 * w_s * x_dot
        + w_s**2 * y)
    
    z_ddot = (
        -mu1 * z / (r_1_sat**3)
        -mu2 * z / (r_2_sat**3))
    
    state_dot = np.array([x_dot, y_dot, z_dot, x_ddot, y_ddot, z_ddot])
    
    return state_dot

def earth_moon_synodic_dynamics(t, state):
    """Derivative to be used with `solve_ivp`. See `synodic_dynamics()` docstring"""
    del t
    return synodic_dynamics(state, MU_EARTH, MU_MOON, R_BC_EARTH, R_BC_MOON, W_EARTH_MOON)