import numpy as np
from constants import MU_EARTH, MU_MOON, R_BC_EARTH, R_BC_MOON, W_EARTH_MOON

def synodic_dynamics(state, mu1, mu2, R1, R2, w_s):
    
    assert mu1 > mu2
    assert R1 < R2
    
    x, y, z, x_dot, y_dot, z_dot = state
    
    r_1_sat = np.sqrt((x + R1)**2 + y**2 + z**2)
    r_2_sat = np.sqrt((x - R2)**2 + y**2 + z**2)
    
    x_ddot = (
        -mu1 * (x + R1) / (r_1_sat**3)
        -mu2 * (x - R2) / (r_2_sat**3)
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
    
    return np.array([x_dot, y_dot, z_dot, x_ddot, y_ddot, z_ddot])

def earth_moon_synodic_dynamics(t, state):
    del t
    return synodic_dynamics(state, MU_EARTH, MU_MOON, R_BC_EARTH, R_BC_MOON, W_EARTH_MOON)