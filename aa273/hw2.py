import numpy as np
from numpy.random import randn
from scipy.linalg import sqrtm, inv
import matplotlib.pyplot as plt

# If inside the ellipse
def in_error_ellipse(x: np.ndarray, mu: np.ndarray, Sigma: np.ndarray):
    P = 0.95
    nu = 1/ (2 * np.pi * sqrtm(Sigma))
    epsilon = (1-P) * nu
    print(x.shape)
    print( (x-mu).T @ inv(Sigma) @ (x-mu) <= -2*np.log(epsilon/nu))
    return (x-mu).T @ inv(Sigma) @ (x-mu) <= -2*np.log(epsilon/nu)


mu = np.array([4,5])
Sigma = np.array([
    [4,0.5], [0.5,8]
])

# Generate 1000 points and scale according to some parameters
x_arr = randn(1000,2) @ Sigma * 2 + mu

mu = mu.reshape((2,1))
points = np.array([x for x in x_arr if in_error_ellipse(x, mu, Sigma)])
plt.scatter(x_arr[:,0], x_arr[:,1])
plt.scatter(points[:,0], points[:,1])


plt.show()