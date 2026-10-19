import numpy as np
from scipy.spatial import cKDTree


def apply_transform(T, X):
    """Applies a (4, 4) homogeneous transform to (N, 3) points."""
    return X @ T[:3, :3].T + T[:3, 3]


def nearest_neighbors(src, dst):
    """
    Inputs:
        src: (N, 3), dst: (M, 3)
    Output:
        dist: (N,) distance from each src point to its nearest dst point
        idx: (N,) index into dst of that nearest point

    HINT: build a scipy.spatial.cKDTree on dst once and query it.
    """
    ########## Code starts here ##########
    tree = cKDTree(dst)
    dist,idx = tree.query(src)
        # raise NotImplementedError
    ########## Code ends here ##########
    return dist, idx


def best_fit_transform(A, B):
    """
    Least-squares rigid transform mapping corresponding points A onto B,
    i.e. minimizing sum_i ||R a_i + t - b_i||^2.
    
    Inputs:
        A, B: (N, 3) corresponding points
    Output:
        (4, 4) homogeneous transform T = [[R, t], [0, 1]] with det(R) = +1

    HINT: center both sets, take the SVD of the 3x3 cross-covariance, and
          flip the sign of the last singular direction if det(R) < 0.
    """
    ########## Code starts here ##########
    a_bar = np.mean(A, axis=0)
    b_bar = np.mean(B, axis=0)
    A_bar = np.asarray(A) - a_bar  # (N,3)
    B_bar = np.asarray(B) - b_bar  # (N,3)
    
    U, _, Vt = np.linalg.svd(A_bar.T @ B_bar)  # Transposed other way to get (3,3)
    R = U @ np.diag((1,1,np.linalg.det(U@Vt))) @ Vt
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = U @ np.diag((1,1,np.linalg.det(U@Vt))) @ Vt

        

    t = b_bar - a_bar@R
    
    T = np.eye(4)
    T[:3,:3] = R.T  # Because row and column flipped
    T[:3,3] = t
    
    ########## Code ends here ##########
    return T


def icp(src: np.ndarray, dst: np.ndarray, T_init: np.ndarray,
        max_iters=50, tol=1e-6, reject_dist=None):
    """
    Point-to-point ICP aligning src to dst.
    
    Inputs:
        src: (N, 3) source points, dst: (M, 3) target points
        T_init: (4, 4) initial guess for the transform from src to dst
        max_iters: maximum number of iterations
        tol: stop when the mean nearest-neighbor distance changes by less than tol
        reject_dist: if not None, only pairs closer than reject_dist are used to
            fit the transform at each iteration (outlier rejection)
    Output:
        T: (4, 4) final transform from the original src to dst
        errors: list of the mean nearest-neighbor distance (over all src points)
            at the start of each iteration

    Each iteration: transform src by the current T, find nearest neighbors,
    fit the incremental transform with best_fit_transform on the kept pairs,
    and compose it with T.
    """
    T = T_init.copy()
    errors = []
    ########## Code starts here ##########
    
    src_pose = np.column_stack([src, np.ones(len(src))])
    
    for i in range(max_iters):
        src_prime = src_pose @ T.T  # (N,4)
        dist, idx = nearest_neighbors(src_prime[:,:3], dst)
        
        errors.append(np.mean(dist))
        if errors[-1] < tol:
            break
        
        # Outlier Rejection
        if reject_dist is None:
            A = src_prime[:,:3]
        else:
            idx = idx[dist < reject_dist]
            A = src_prime[dist < reject_dist,:3]
        dT = best_fit_transform(A, dst[idx])
        
        T = dT@T

        
    # raise NotImplementedError
    ########## Code ends here ##########
    return T, errors
