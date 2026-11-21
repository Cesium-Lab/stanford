import numpy as np
from scipy.signal import convolve2d
from utils import StochOccupancyGrid2D


def window_counts(mask, window_size):
    """
    Number of True cells of mask in the window_size x window_size window centered on every cell.
    Cells outside the map are not counted.
    Inputs:
        mask: (ny, nx) boolean array
        window_size: odd integer
    Output:
        (ny, nx) array of counts

    HINT: this is a convolution with a window of ones (scipy.signal.convolve2d with mode="same").
    """
    ########## Code starts here ##########
    kernel = np.ones((window_size, window_size))
    counts = convolve2d(mask, kernel, mode="same")
    ########## Code ends here ##########
    return counts


def explore(occupancy: StochOccupancyGrid2D, window_size=11, min_unknown=0.25, min_free=0.35, occupied_thresh=50):
    """
    Frontier cells of an occupancy grid.
    A cell of occupancy.probs is unknown if its value is -1, occupied if it is >= occupied_thresh,
    and free otherwise. A cell is a frontier cell if, in the window_size x window_size window
    centered on it (cells outside the map are not counted, but the fractions are still of
    window_size^2),
        - at least min_unknown of the window_size^2 cells are unknown,
        - none of the cells are occupied, and
        - at least min_free of the window_size^2 cells are free.
    The cell itself may be free or unknown. Use the window_size argument, not occupancy.window_size.
    Output:
        frontier_states: (N, 2) array of (x, y) states of the frontier cells, in row-major order
        (increasing ky, then increasing kx, which is the order np.nonzero returns)

    HINT: work with grid indices and convert to states at the end with occupancy.grid2state.
          probs is indexed as probs[ky, kx], while grid2state expects (kx, ky).
    """
    probs = occupancy.probs
    ########## Code starts here ##########
    # probs = probs.T

    occupied_mask = probs >= occupied_thresh
    unknown_mask = probs < 0.0
    unoccupied_mask = (probs < occupied_thresh) & (probs >= 0.0)  # fix this later

    occupied_rslt = window_counts(occupied_mask, window_size)
    unknown_rslt = window_counts(unknown_mask, window_size)
    unoccupied_rslt = window_counts(unoccupied_mask, window_size)

    area = window_size**2

    frontier_states = np.argwhere(
        (occupied_rslt == 0)
        & ((unknown_rslt / area) >= min_unknown)
        & ((unoccupied_rslt / area) >= min_free)
    )[:, ::-1]

    # frontier_idx = np.argwhere(...)[:, ::-1]   # (ky, kx) -> (kx, ky)

    frontier_states = np.array([occupancy.grid2state(s) for s in frontier_states])

    ########## Code ends here ##########
    return frontier_states


def closest_frontier(frontier_states, current_state):
    """
    Output:
        (state, distance): the frontier state closest to current_state in Euclidean distance,
        and that distance. If several states are equally close, return the first one.
        Returns (None, np.inf) if there are no frontier states.
    """
    ########## Code starts here ##########
    if len(frontier_states) == 0:
        return None, np.inf

    dist = np.apply_along_axis(lambda x: np.linalg.norm(x - current_state), axis=1, arr=frontier_states)

    i = np.argmin(dist)
    return frontier_states[i], dist[i]
    ########## Code ends here ##########
