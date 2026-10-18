#!/usr/bin/env python3

# import rclpy
# from rclpy.node import Node

from dataclasses import dataclass

import numpy as np
from asl_tb3_lib . math_utils import wrap_angle
from asl_tb3_lib . navigation import (
    BaseNavigator,
    TrajectoryPlan,
    TurtleBotControl,
    TurtleBotState,
)
from scipy.interpolate import splev

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
    
    # Differential Flatness Control
    kp_x: float
    kd_x: float
    kp_y: float
    kd_x: float

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
        
        self.t_prev = 0.0
        self.v_prev = 0.0
        self.om_prev = 0.0
    
    def load_traj(self, traj_time: np.ndarray, plan: TrajectoryPlan) -> None:
        """ Loads in a new trajectory to follow, and resets the time """
        self.traj_time = traj_time
        self.plan = plan
    
    def get_desired_flatness_vals(self, t: float) -> tuple[np.ndarray, np.ndarray, np.ndarray,
                                                    np.ndarray, np.ndarray, np.ndarray]:
        """
        Input:
            t: Current time
        Output:
            x_d, xd_d, xdd_d, y_d, yd_d, ydd_d: Desired state and derivatives
                at time t according to spline
        """
        
        x_d = splev(t, self.plan.path_x_spline, der=0)
        xd_d = splev(t, self.plan.path_x_spline, der=1)
        xdd_d = splev(t, self.plan.path_x_spline, der=2)
        
        y_d = splev(t, self.plan.path_y_spline, der=0)
        yd_d = splev(t, self.plan.path_y_spline, der=1)
        ydd_d = splev(t, self.plan.path_y_spline, der=2)

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
        x_d, xd_d, xdd_d, y_d, yd_d, ydd_d = self.get_desired_flatness_vals(t)
        
        if abs(self.v_prev) < self.v_prev_thresh:
            self.v_prev = self.v_prev_thresh
            
        xd_prev = self.v_prev*np.cos(th)
        yd_prev = self.v_prev*np.sin(th)
        
        # compute virtual controls
        u = np.array([xdd_d + self.params.kp_x*(x_d-x) + self.params.kp_y*(xd_d-xd_prev),
                      ydd_d + self.params.kd_x*(y_d-y) + self.params.kd_y*(yd_d-yd_prev)])
        
        # compute real controls by mapping what we can do to our ideal controls
        # by differentiating dynamics again and then mapping [a,om] to [xdd, ydd]
        J = np.array([[np.cos(th), -self.v_prev*np.sin(th)],
                          [np.sin(th), self.v_prev*np.cos(th)]])
        a, om = np.linalg.solve(J, u)
        vel = self.v_prev + a*dt
        
        # Control limit handled by base navigator class
        self.v_prev = vel
        self.om_prev = om
        
        return vel, om
        

        
        
        
    
    

