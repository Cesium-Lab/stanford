import numpy as np
from numpy.linalg import norm
from scipy.integrate import solve_ivp

from constants import RAD_TO_DEG

def AA279jacobianshoot(odefun, tspan, y0in, dv, t_arr):
    """
    Returns 3x3 Jacobian for shooting method

    AA279 Function Library
    Last modified: 7 October 2026 by Andrew K. Barrows

    Jacobian describes sensitivity of final position to initial velocity

    State must be of the form [rx ry rz vx vy vz]'

    sample function call:
    J = jacobianshoot(@earthorbitbody, [0; 75*60], [r1; v1], 0.001)

    odefun function handle for state derivative function
    tspan trajectory start and end times [sec]
    y0in state at which J should be evaluated
    dv small velocity increment used for finite differences
    t_arr array to be evaluated at
    
    """

    J = np.zeros((3,3))
    y0in = np.asarray(y0in)

    # vx
    y0 = y0in + [0,0,0,dv,0,0]
    sol = solve_ivp(odefun, (t_arr[0], t_arr[-1]), y0, method='LSODA', t_eval=t_arr, rtol=1e-6, atol=1e-9)
    rhigh = sol.y[0:3, -1]
    y0 = y0in + [0,0,0,-dv,0,0]
    sol = solve_ivp(odefun, (t_arr[0], t_arr[-1]), y0, method='LSODA', t_eval=t_arr, rtol=1e-6, atol=1e-9)
    rlow = sol.y[0:3, -1]
    J[:, 0] = (rhigh-rlow)/(2*dv)

    # vx
    y0 = y0in + [0,0,0,0,dv,0]
    sol = solve_ivp(odefun, (t_arr[0], t_arr[-1]), y0, method='LSODA', t_eval=t_arr, rtol=1e-6, atol=1e-9)
    rhigh = sol.y[0:3, -1]
    y0 = y0in + [0,0,0,0,-dv,0]
    sol = solve_ivp(odefun, (t_arr[0], t_arr[-1]), y0, method='LSODA', t_eval=t_arr, rtol=1e-6, atol=1e-9)
    rlow = sol.y[0:3, -1]
    J[:, 1] = (rhigh-rlow)/(2*dv)

    # vx
    y0 = y0in + [0,0,0,0,0,dv]
    sol = solve_ivp(odefun, (t_arr[0], t_arr[-1]), y0, method='LSODA', t_eval=t_arr, rtol=1e-6, atol=1e-9)
    rhigh = sol.y[0:3, -1]
    y0 = y0in + [0,0,0,0,0,-dv]
    sol = solve_ivp(odefun, (t_arr[0], t_arr[-1]), y0, method='LSODA', t_eval=t_arr, rtol=1e-6, atol=1e-9)
    rlow = sol.y[0:3, -1]
    J[:, 2] = (rhigh-rlow)/(2*dv)

    return J



# eps=1e-8rad
def flyby_shoot(
    v_arrival_PCI: float,
    v_departure_PCI: float,
    delta_des: float,
    mu: float,
    deg=False,
    eps=1e-8,
    d=10,
    verbose=False,
) -> tuple[float, float, float, float, float]:

    delta_des = delta_des / RAD_TO_DEG if deg else delta_des

    def delta_tot(r_p):
        return np.arcsin(1 / (1 + r_p * v_arrival_PCI**2 / mu)), np.arcsin(
            1 / (1 + r_p * v_departure_PCI**2 / mu)
        )

    # Guess if circular velocity with e=2
    e = 2
    r_p = mu * (e - 1) / (v_arrival_PCI**2)

    iter = 20
    for i in range(iter):
        delta1, delta2 = delta_tot(r_p)

        d_delta = delta_des - (delta1 + delta2)

        if verbose:
            print(f"d_delta: {d_delta:.5f}m")

        if norm(d_delta) < eps:
            break

        J = (sum(delta_tot(r_p + d)) - sum(delta_tot(r_p - d))) / (2 * d)

        step = d_delta / J

        # Make sure periapsis is positive
        alpha = 1.0

        while r_p + alpha * step <= 0:
            alpha *= 0.5

        r_p += alpha * step

    else:
        raise ValueError

    # dv
    v_p1 = np.sqrt(v_arrival_PCI**2 + 2 * mu / r_p)
    v_p2 = np.sqrt(v_departure_PCI**2 + 2 * mu / r_p)
    dv = abs(v_p2 - v_p1)
    # e
    e1 = 1 + r_p * v_arrival_PCI**2 / mu
    e2 = 1 + r_p * v_departure_PCI**2 / mu

    return dv, v_p1, v_p2, r_p, e1, e2, delta1, delta2

