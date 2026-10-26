import numpy as np

# https://ssd.jpl.nasa.gov/

###########################################################################
#                   Conversion
###########################################################################

AU_TO_KM = 149597870.7  # km/AU
M_TO_KM = 1.0/1000

DEG_TO_RAD = np.pi/180.0
RAD_TO_DEG = 1.0/DEG_TO_RAD
RAD_TO_SIDEREAL_HOUR = 24.0/np.pi/2.0

YEAR_TO_DAY = 365
HOUR_TO_SEC = 60 * 60
DAY_TO_SEC = 24 * 60 * 60
MIN_TO_SEC = 60
CTY_TO_DAY = 36525.0
J2000_JD = 2451545.0

###########################################################################
#                   Planets
###########################################################################

# km3/s2
MU_SUN = 1.3271244004193938e11
MU_EARTH = 398600.4418
MU_MOON = 4903.0
MU_VENUS = 324858.630
MU_JUPITER = 126686511.000

MU_PLUTO = 870.9
MU_CHARON = 101.0

# km
R_EARTH = 6378.0
R_MOON = 1738.0
R_SUN = 695508.0 

R_VENUS_VOLUMETRIC = 6051.80
R_EARTH_VOLUMETRIC = 6371.01
R_JUPITER_VOLUMETRIC = 69911.00

R_PLUTO = 1184.0
R_CHARON = 603.5

# J2
J2_EARTH = 1.0826267e-3

# rad/s
W_EARTH = 0.0000729211585530

ECLIPTIC_ANGLE = 23.43928 * RAD_TO_DEG
"""Ecliptic angle [rad]"""

###########################################################################
#                   Distances
###########################################################################

# km
R_PLUTO_CHARON = 19571.0 
R_EARTH_MOON = 384400.0

###########################################################################
#                   Derived
###########################################################################

# km
R_BC_EARTH = MU_MOON / (MU_MOON + MU_EARTH) * R_EARTH_MOON
R_BC_MOON = MU_EARTH / (MU_MOON + MU_EARTH) * R_EARTH_MOON

# rad/s
W_EARTH_MOON = np.sqrt( (MU_EARTH + MU_MOON) / R_EARTH_MOON**3)
W_PLUTO_CHARON = np.sqrt( (MU_PLUTO + MU_CHARON) / R_PLUTO_CHARON**3)


