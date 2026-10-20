import numpy as np
from numpy.linalg import norm
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
from lamberthub import vallado2013
import plotly.graph_objects as go
from tqdm import tqdm

from constants import DEG_TO_RAD, MU_EARTH, W_EARTH, R_EARTH
from angle import dcm_x, dcm_z

def kepler(M: float, e: float):
    """Vallado 4e eq. 2-4 p. 45 (pdf p. 72)

    Parameters
    ----------
    M : float
        Mean anomaly [rad]
    e : float
        Eccentricity [0, 1)

    Returns
    -------
    E : float
        Eccentric anomaly [rad]
    """
    E = fsolve(lambda E: E - e * np.sin(E) - M, M)[0]
    return E

###########################################################################
#                   RV <-- COE
###########################################################################

def rv_from_coe(a: float, e: float, i: float, raan: float, aop: float, M: float, mu: float) -> tuple[np.ndarray, np.ndarray]:
    """Convert classical orbital elements to inertial position and velocity (not just ECI)
    
    Vallado 4e Algorithm 10 p. 118 (pdf p. 145)

    Parameters
    ----------
    a : float
        Semimajor axis [km]
    e : float
        Eccentricity
    i, raan, aop, M : float
        Inclination, RAAN, argument of periapsis, mean anomaly [rad]
    mu : float
        Gravitational parameter of central body [km3/s2]

    Returns
    -------
    r_ijk, v_ijk : np.ndarray (3,)
        Inertial position [km] and velocity [km/s]
    """

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

###########################################################################
#                   PCPF <--> LLA
###########################################################################

def pcpf_from_lla(lat: float, lon: float, alt_km = 0.0, r_body_km = R_EARTH, deg = True):
    """Convert latitude, longitude, and altitude to planet-centered, planet-fixed.
    Spherical body.

    Parameters
    ----------
    lat, lon : float
        Lat,lon [deg if deg=True, else rad]
    alt_km : float
        Altitude above SPHERICAL surface [km]
    r_body_km : float
        Body radius [km]
    deg : bool
        Whether input angles are in degrees

    Returns
    -------
    r_pcpf : np.ndarray (3,)
        Body-fixed position [km]
    """
    if deg:
        lat *= DEG_TO_RAD
        lon *= DEG_TO_RAD
        
    rho = r_body_km + alt_km
    
    r_pcpf = np.array([
        rho * np.cos(lat) * np.cos(lon),
        rho * np.cos(lat) * np.sin(lon),
        rho * np.sin(lat)
    ])
    
    return r_pcpf

###########################################################################
#                   PCI <--> PCPF
###########################################################################

def calc_theta_g(t_utc: float, theta_ref: float, t_ref: float, w_body = W_EARTH):
    """Simple rotation from Greenwich rotation angle assuming constant rotation rate.

    Parameters
    ----------
    t_utc, t_ref : float
        Current and reference UTC timestamps [s]
    theta_ref : float
        Earth rotation angle at reference time [rad]
    w_body : float, optional
        default `W_EARTH` [rad/s]
        
    Returns
    ------
    theta_g : float
        Greenwich rotation angle [rad], wrapped to [0, 2*pi)
    """
    return (theta_ref + w_body * (t_utc - t_ref)) % (2 * np.pi)

def calc_pci_from_pcpf(r_pcpf: np.ndarray, v_pcpf: np.ndarray, t_utc: float, theta_ref: float, t_ref: float, w_body = W_EARTH):
    """Convert rotating-frame position and velocity to inertial coordinates.
    
    Somewhat simplified version of itrf-gcrs in Vallado 4e Section 3.7 pp. 203
    
    Uses a constant body rotation rate, neglecting precession and nutation.

    Parameters
    ----------
    r_pcpf, v_pcpf : np.ndarray (3,)
        Position [km] and rotating-frame velocity [km/s]
    t_utc, t_ref : float
        Current and reference UTC timestamps [s]
    theta_ref : float
        Rotation angle at reference epoch [rad]
    w_body : float
        Body rotation rate [rad/s]

    Returns
    -------
    r_pci, v_pci : np.ndarray (3,)
        Inertial position [km] and velocity [km/s]
    """
    # Earth rotation angle
    theta_pcpf_wrt_pci = calc_theta_g(t_utc, theta_ref, t_ref, w_body)
    
    dcm_pci_wrt_pcpf = dcm_z(theta_pcpf_wrt_pci).T
    
    r_pci = dcm_pci_wrt_pcpf @ r_pcpf
    v_pci = dcm_pci_wrt_pcpf @ (v_pcpf + np.cross([0,0,w_body], r_pcpf))
    
    return r_pci, v_pci

###########################################################################
#                   PCI <--> LLA
###########################################################################

def launch_pci(t_arr_utc: np.ndarray, lat: float, lon: float, alt: float, theta_ref: float, t_ref: float, r_body_km = R_EARTH, w_body = W_EARTH, deg = True):
    """Calculate inertial position and velocity of a stationary launch site over time on sphere

    Parameters
    ----------
    t_arr_utc : np.ndarray (N,)
        UTC timestamps [s]
    lat, lon : float
        Lat,lon [deg if deg=True, else rad]
    alt : float
        Altitude above SPHERICAL surface [km]
    theta_ref : float
        Greenwich angle at reference epoch [rad]
    t_ref : float
        Reference UTC timestamp [s]
    r_body_km : float
        Body radius [km]
    w_body : float
        Body rotation rate [rad/s]
    deg : bool
        Whether input angles are in degrees

    Returns
    -------
    launch_r_pci, launch_v_pci : np.ndarray (N, 3)
        Inertial positions [km] and velocities [km/s]
    """
    launch_r_pcpf = pcpf_from_lla(lat, lon, alt, r_body_km, deg)
    launch_v_pcpf = np.zeros(3)
    
    launch_arr_pci = np.array([calc_pci_from_pcpf(launch_r_pcpf, launch_v_pcpf, t, theta_ref, t_ref, w_body) for t in t_arr_utc])
    launch_r_pci = launch_arr_pci[:,0,:]
    launch_v_pci = launch_arr_pci[:,1,:]
    return launch_r_pci, launch_v_pci

###########################################################################
#                   Sanity
###########################################################################

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

