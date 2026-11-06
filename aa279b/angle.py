import numpy as np

def wrap_to_pi(x):
  return (x + np.pi) % (2 * np.pi) - np.pi

def wrap_to_2pi(x):
    """Wrap angle(s) [rad] to `[0, 2*pi)`"""
    return x % (2 * np.pi)

def dcm_x(theta: float):
    """Passive DCM from frame 1 to frame 2, rotated by theta [rad]."""
    return np.array(
        [
            [1, 0, 0],
            [0, np.cos(theta), np.sin(theta)],
            [0, -np.sin(theta), np.cos(theta)],
        ]
    )


def dcm_y(theta: float):
    """Passive DCM from frame 1 to frame 2, rotated by theta [rad]."""
    return np.array(
        [
            [np.cos(theta), 0, -np.sin(theta)],
            [0, 1, 0],
            [np.sin(theta), 0, np.cos(theta)],
        ]
    )


def dcm_z(theta: float):
    """Passive DCM from frame 1 to frame 2, rotated by theta [rad]."""
    return np.array(
        [
            [np.cos(theta), np.sin(theta), 0],
            [-np.sin(theta), np.cos(theta), 0],
            [0, 0, 1],
        ]
    )


def angle_between(u, v):
    """Returns the angle between two vectors in radians."""
    u_norm = np.linalg.norm(u)
    v_norm = np.linalg.norm(v)

    # Avoid division by zero for zero vectors
    if u_norm < 1e-12 or v_norm < 1e-12:
        return np.nan
        # raise ValueError("Zero vectors do not have a defined angle.")

    dot_product = np.dot(u, v)
    cosine_similarity = dot_product / (u_norm * v_norm)

    # Avoid numerical overflow / floating point inaccuracies
    angle_in_radians = np.arccos(np.clip(cosine_similarity, -1.0, 1.0))

    return angle_in_radians