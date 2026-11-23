#!/usr/bin/env python3

import numpy as np
import rclpy
from rclpy.node import Node
from scipy.signal import convolve2d
from asl_tb3_lib.grids import snap_to_grid, StochOccupancyGrid2D
from asl_tb3_lib.navigation import BaseNavigator
from asl_tb3_msgs.msg import TurtleBotState
from std_msgs.msg import Bool
from nav_msgs.msg import OccupancyGrid, Path


##########################################################################################
#                   Functions
##########################################################################################

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
    

##########################################################################################
#                   FrontierExplorer
##########################################################################################


class FrontierExplorer(Node):
    def __init__(self, window_size=11, min_unknown=0.25, min_free=0.35, occupied_thresh=50):
        super().__init__("frontier_explorer")
        
        self.window_size = window_size
        self.min_unknown = min_unknown
        self.min_free = min_free
        self.occupied_thresh = occupied_thresh
        
        self.success_sub = self.create_subscription(Bool, "/nav_success", self.success_callback, 10)
        
        self.state_sub = self.create_subscription(TurtleBotState, "/state", self.state_callback, 10)
        self.map_sub = self.create_subscription(OccupancyGrid, "/map", self.map_callback, 10)
        
        self.send_cmd_pub = self.create_publisher(TurtleBotState, "/cmd_nav", 10)

        # self.detector_sub = self.create_subscription(Bool, "/detector_bool", self.detector_callback, 10)
        # self.stop_sign_timer = self.create_timer(5.0, self.stop_sign_callback)
        # self.stop_sign_timer.cancel()
        self.stopped = False  # due to stop sign
        
        self.current_state = None
        self.occupancy = None

        self.started = False
        self.last_goal = None
        self.failed_goals = []


        
    def state_callback(self, msg: TurtleBotState) -> None:
        self.current_state = np.array([msg.x, msg.y])
        
    def map_callback(self, msg: OccupancyGrid) -> None:
        self.occupancy = StochOccupancyGrid2D(
            resolution=msg.info.resolution,
            size_xy=np.array([msg.info.width, msg.info.height]),
            origin_xy=np.array([msg.info.origin.position.x, msg.info.origin.position.y]),
            window_size=self.window_size,
            probs=msg.data,
            thresh=self.occupied_thresh
        )

        if not self.started and self.current_state is not None:
            self.started = True
            self.explore_cmd()

    def explore_cmd(self) -> None:
        
        # Nav failure OR success, need to replan
        frontier_states = explore(self.occupancy, self.window_size, self.min_unknown, self.min_free, self.occupied_thresh)

        frontier_states = np.array([s for s in frontier_states
            if all(np.linalg.norm(s - f) > 0.3 for f in self.failed_goals)]
        ).reshape(-1, 2)

        closest_state, distance = closest_frontier(frontier_states, self.current_state)
        self.last_goal = closest_state
        
        if closest_state is not None:
            self.get_logger().info(f"Closest frontier state: {closest_state}, distance: {distance}")
        else:
            self.get_logger().info("No frontier states found.")
            return
        
        cmd = TurtleBotState()
        cmd.x, cmd.y = closest_state
        self.send_cmd_pub.publish(cmd)

    def success_callback(self, msg: Bool) -> None:

        if self.stopped or (self.occupancy is None) or (self.current_state is None):
            return

        if (not msg.data) and (self.last_goal is not None):
            self.failed_goals.append(self.last_goal)

        self.explore_cmd()
        

    # def detector_callback(self, msg: Bool) -> None:
    #     if msg.data:
    #         self.stopped = True
    #         self.stop_sign_timer.reset()

    # def stop_sign_callback(self) -> None:
    #     # no timer, resumes 
    #     self.stopped = False
    #     self.stop_sign_timer.cancel()




    
if __name__ == "__main__":
    rclpy.init()
    node = FrontierExplorer()
    rclpy.spin(node)
    rclpy.shutdown()