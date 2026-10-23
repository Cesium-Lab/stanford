import numpy as np

T = np.array([
    [0.999, 0.05], 
    [0.001, 0.95]
])

M_y0 = np.array([
    [0.9, 0], 
    [0, 0.01]
])

M_y1 = np.array([
    [0.1, 0], 
    [0, 0.99]
])

# Initial conditions
pi0 = np.array([[1], [0]])
pi = pi0

for i in range(98):

    pi = (M_y0 @ T @ pi /
          (np.ones((1,2)) @ M_y0 @ T @ pi)[0][0])
    
print((np.ones((1,2)) @ M_y1 @ T @ pi)[0][0])
pi_final = (M_y1 @ T @ pi /
          (np.ones((1,2)) @ M_y1 @ T @ pi)[0][0])


print(f"pi_0:\n{pi0}\n")
print(f"pi_98:\n{pi}\n")
print(f"pi_99:\n{pi_final}\n")
print(f"Probability of being sick on step 99:\n{pi_final[1][0]:.5f}\n")
