#!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node

from asl_tb3_lib . math_utils import wrap_angle
from asl_tb3_lib . navigation import BaseNavigator, TurtleBotControl, TurtleBotState, TrajectoryPlan
from dataclasses import dataclass
import numpy as np

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
    kp_theta: float
    kp_v: float
    kd_theta: float
    kd_v: float

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

        if params is None:
            params = NavigatorParams(kp_theta=2.0)
        self.params = params
        self.v_prev_thresh = v_prev_thresh

        # Resets trajectory and previous control memory
        self.reset()
        
    ##### Helpers #####
    
    def reset(self) -> None:
        self.traj_time = None
        self.traj = None
        
        self.V_prev = 0.0
        self.t_prev = 0.0
        # self.om_prev = 0.
        # self.t_prev = 0.
    
    def load_traj(self, traj_time: np.ndarray, traj: TrajectoryPlan) -> None:
        """ Loads in a new trajectory to follow, and resets the time """
        self.traj_time = traj_time
        self.plan = traj
    
    def get_desired_state(self, t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray,
                                                    np.ndarray, np.ndarray, np.ndarray]:
        """
        Input:
            t: Current time
        Output:
            x_d, xd_d, xdd_d, y_d, yd_d, ydd_d: Desired state and derivatives
                at time t according to self.coeffs
        """
        
        if self.traj_time is None or self.traj is None:
            raise RuntimeError("Must load trajectory first")
        
        x_d, xd_d, xdd_d, y_d, yd_d, ydd_d = self.plan.desired_state(t)

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
    
    def compute_trajectory_tracking_control(self, x: float, y: float, th: float, t: float) -> tuple[float, float]:
        
        dt = t - self.t_prev
        x_d, xd_d, xdd_d, y_d, yd_d, ydd_d = self.get_desired_state(t)

        
        
        
    
    

