#!/usr/bin/env python3

from dataclasses import dataclass

import numpy as np
from asl_tb3_lib.grids import StochOccupancyGrid2D
from asl_tb3_lib . math_utils import wrap_angle
from asl_tb3_lib . navigation import (
    BaseNavigator,
    TrajectoryPlan,
    TurtleBotControl,
    TurtleBotState,
)
import rclpy
from scipy.interpolate import splev, splrep

from a_star import AStar

# from asl_tb3_lib . tf_utils import quaternion_to_yaw

"""
Docs:

TurtleBotControl
- v and omega

TrajectoryPlan
- x and y splines
- time duration
- path of both splines interpolated

BaseNavigator
- plan: TrajectoryPlan
- goal: TurtleBotState
- grid: StochOccupancyGrid2D
- params
"""

V_PREV_THRES = 0.0001

@dataclass
class NavigatorParams:
    
    # Heading Control
    kp_theta: float = 2.0
    
    # Differential Flatness Control
    kp_x: float = 0
    kd_x: float = 0
    kp_y: float = 0
    kd_y: float = 0

    # AStar Control
    v_desired: float = 0.15
    spline_alpha: float = 0.05
    
    # Normal
    V_max: float = 0.5
    om_max: float = 1.0


class Navigator(BaseNavigator):
    """
    
    Has:
    - mode, plan, params
    """
    def __init__(self, params: NavigatorParams | None = None, v_prev_thresh = V_PREV_THRES) -> None:
        # give it a default node name
        super().__init__("navigator")

        self.params = params if params is not None else NavigatorParams()
        self.v_prev_thresh = v_prev_thresh
        
        self.reset()
        
    ##### Helpers #####
    
    def reset(self) -> None:
        # self.traj_time = None
        # self.traj = None
        
        self.t_prev = 0.0
        self.v_prev = 0.0
        self.om_prev = 0.0
    
    # def load_traj(self, traj_time: np.ndarray, plan: TrajectoryPlan) -> None:
    #     """ Loads in a new trajectory to follow, and resets the time """
    #     self.traj_time = traj_time
    #     self.plan = plan
    
    @staticmethod
    def get_flatness_values(t: float, plan: TrajectoryPlan) -> tuple[np.ndarray, np.ndarray, np.ndarray,
                                                    np.ndarray, np.ndarray, np.ndarray]:
        """
        Input:
            t: Current time
            plan: TrajectoryPlan
        Output:
            x_d, xd_d, xdd_d, y_d, yd_d, ydd_d: Desired state and derivatives
                at time t according to spline
        """
        
        x_d = splev(t, plan.path_x_spline, der=0)
        xd_d = splev(t, plan.path_x_spline, der=1)
        xdd_d = splev(t, plan.path_x_spline, der=2)
        
        y_d = splev(t, plan.path_y_spline, der=0)
        yd_d = splev(t, plan.path_y_spline, der=1)
        ydd_d = splev(t, plan.path_y_spline, der=2)

        return x_d, xd_d, xdd_d, y_d, yd_d, ydd_d
        
    def compute_heading_control(self,
        state: TurtleBotState,
        goal: TurtleBotState
    ) -> TurtleBotControl:
        """ Compute only orientation target (used for NavMode.ALIGN and NavMode.Park)

        Returns:
            TurtleBotControl: control target
        """
        
        err = wrap_angle(goal.theta - state.theta)
        omega = self.params.kp_theta * err
        
        msg = TurtleBotControl()
        msg.omega = omega
        
        return msg
    
    def compute_trajectory_tracking_control(self,
        state: TurtleBotState,
        plan: TrajectoryPlan,
        t: float,
    ) -> TurtleBotControl:
        
        dt = t - self.t_prev
        x_d, xd_d, xdd_d, y_d, yd_d, ydd_d = self.get_flatness_values(t, plan)
        
        if abs(self.v_prev) < self.v_prev_thresh:
            self.v_prev = self.v_prev_thresh
            
        
        xd_prev = self.v_prev*np.cos(state.theta)
        yd_prev = self.v_prev*np.sin(state.theta)
        
        # compute virtual controls
        u = np.array([xdd_d + self.params.kp_x*(x_d-state.x) + self.params.kd_x*(xd_d-xd_prev),
                      ydd_d + self.params.kp_y*(y_d-state.y) + self.params.kd_y*(yd_d-yd_prev)])
        
        # compute real controls by mapping what we can do to our ideal controls
        # by differentiating dynamics again and then mapping [a,om] to [xdd, ydd]
        J = np.array([[np.cos(state.theta), -self.v_prev*np.sin(state.theta)],
                          [np.sin(state.theta), self.v_prev*np.cos(state.theta)]])
        a, om = np.linalg.solve(J, u)
        vel = self.v_prev + a*dt
        
        # Control limit handled by base navigator class
        self.t_prev = t
        self.v_prev = vel
        self.om_prev = om
        
        msg = TurtleBotControl()
        msg.v = vel
        msg.omega = om
        
        return msg
    
    def compute_trajectory_plan(self,
        state: TurtleBotState,
        goal: TurtleBotState,
        occupancy: StochOccupancyGrid2D,
        resolution: float,
        horizon: float,
    ) -> TrajectoryPlan | None:
        
        # Run A* using horizon, state, goal, occupancy, and resolution
        grid_size = occupancy.size_xy
        x_init = (state.x, state.y)
        x_goal=(goal.x, goal.y)
        statespace_lo=(0,0)
        statespace_hi=grid_size
        
        a_star = AStar(
            statespace_lo,
            statespace_hi,
            x_init,
            x_goal,
            occupancy,
            resolution=resolution,
            heuristic="l2",
            heuristic_weight=1.0,
        )
        
        # Solvability
        if not a_star.solve():
            print("No path found")
            return None
        if len(a_star.path) < 4:
            print(f"Solution ({len(a_star.path)} nodes) too short")
            return None

        # Reset control memory
        self.reset()

        # Path time
        path = np.asarray(a_star.path)
        path_lengths = np.linalg.norm(np.diff(path, axis=0), axis=1)
        t_arr = np.concatenate([[0.], np.cumsum(path_lengths / self.params.v_desired)])
        
        path_x_spline = splrep(t_arr, path[:,0], k = 3, s = self.params.spline_alpha)
        path_y_spline = splrep(t_arr, path[:,1], k = 3, s = self.params.spline_alpha)

        return TrajectoryPlan(
            path=a_star.path,
            path_x_spline=path_x_spline,
            path_y_spline=path_y_spline,
            duration=t_arr[-1],
        )
        
        
        
        # Unsolvable
        #  if A* problem is not solvable or length of path < 4 then
        # 3: return None
        # 4: end if
        
if __name__ == "__main__":
    rclpy.init()
    
    navigator = Navigator()
    rclpy.spin(navigator)
    rclpy.shutdown()
        
        
        
    
    

