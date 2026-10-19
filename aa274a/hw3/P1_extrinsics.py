import numpy as np


def checkerboard_points(nx, ny, square_size: float):
    """
    World coordinates of the checkerboard corners on the Z = 0 plane.
    Inputs:
        nx, ny: number of inner corners along x and y
        square_size: side length of one square (m)
    Output:
        (nx * ny, 2) array of (X, Y), with X varying fastest:
        (0, 0), (s, 0), ..., ((nx-1)s, 0), (0, s), ...
    """
    ########## Code starts here ##########
    x = np.arange(0,nx)
    y = np.arange(0,ny)
    
    coords = np.array(np.meshgrid(x,y)).reshape(2,-1) * square_size
    return coords.T

    ########## Code ends here ##########


def compute_homography(world_xy, uv) -> np.ndarray:
    """
    Homography H with [u, v, 1]^T ~ H [X, Y, 1]^T, estimated with the DLT and the SVD.
    Inputs:
        world_xy: (N, 2) points on the board, N >= 4
        uv: (N, 2) corresponding pixel coordinates
    Output:
        (3, 3) homography, scaled so that H[2, 2] = 1
    """
    ########## Code starts here ##########
    rows = []
    
    for _xy,_uv in zip(world_xy, uv):
        rows.append([-_xy[0], -_xy[1], -1, 0,       0,       0,    _uv[0]*_xy[0], _uv[0]*_xy[1], _uv[0]])
        rows.append([0,       0,       0,  -_xy[0], -_xy[1], -1,   _uv[1]*_xy[0], _uv[1]*_xy[1], _uv[1]])
        
    M = np.array(rows)
    
    # svd
    # 2. Compute the Singular Value Decomposition (SVD)
    _, _, h_stack = np.linalg.svd(M)
    
    # Smallest singular value (and scaled)
    H = h_stack[-1].reshape(3,3)
    H = H / H[2,2]

    return H
    ########## Code ends here ##########


def pose_from_homography(K, H):
    """
    Camera pose from a board homography, so that P_cam = R P_world + t.
    Inputs:
        K: (3, 3) intrinsics, H: (3, 3) homography
    Output:
        R: (3, 3) rotation matrix (orthonormal, det = +1)
        t: (3,) translation, with t[2] > 0 (board in front of the camera)

    HINT: H is only known up to scale, including its sign. Normalize by the
          norm of the first column, pick the sign that gives t[2] > 0, and
          replace [r0, r1, r0 x r1] by the closest rotation matrix (SVD).
    """
    ########## Code starts here ##########
    KH = np.linalg.inv(K) @ H
    KH = KH / np.linalg.norm(KH[:,0]) * np.sign(KH[2,2])
    # print(np.linalg.norm(KH[:,0]))
    # print(np.linalg.norm(KH[:,1]))
    # print(np.linalg.norm(KH[:,2]))
    # print(KH)
    r0 = KH[:,0]
    r1 = KH[:,1]
    r2 = np.cross(r0, r1)
    # _, _, h_stack = np.linalg.svd(M)
    U,S,V =  np.linalg.svd(np.vstack((r0,r1,r2)).T)

    R = U @ np.diag((1,1,np.linalg.det(U@V))) @ V

    t = KH[:,2]
    
    print(R)
    print(t)
    
    # r1 = KH[:,1]
    # raise NotImplementedError
    # R,t = None, None
    ########## Code ends here ##########
    return R, t


def project_points(K: np.ndarray, R: np.ndarray, t: np.ndarray, X: np.ndarray):
    """
    Inputs:
        K, R: (3, 3), t: (3,)
        X: (N, 3) points in the world frame
    Output:
        (N, 2) pixel coordinates (u, v)
    """
    ########## Code starts here ##########
    P_prime = X @ R + t
    return P_prime[:,:2] / P_prime[0,2]
    ########## Code ends here ##########


def reprojection_rmse(uv, uv_proj):
    """
    Output:
        Root-mean-square pixel distance between (N, 2) arrays uv and uv_proj
    """
    ########## Code starts here ##########
    raise NotImplementedError
    ########## Code ends here ##########
