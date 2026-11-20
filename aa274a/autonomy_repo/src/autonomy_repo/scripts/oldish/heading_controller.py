#!/usr/bin/env python3

import rclpy

from asl_tb3_lib.control import BaseHeadingController
from asl_tb3_lib.math_utils import wrap_angle
from asl_tb3_msgs.msg import TurtleBotControl, TurtleBotState

class HeadingController(BaseHeadingController):
    def __init__(self):
        super().__init__("heading_controller")
        
        self.kp = 2.0
        
    # overrides
    def compute_control_with_goal(self,
            state: TurtleBotState,
            goal: TurtleBotState
        ) -> TurtleBotControl:
        
        err = wrap_angle(goal.theta - state.theta)
        omega = self.kp * err
        
        msg = TurtleBotControl()
        msg.omega = omega
        
        return msg
    
if __name__ == "__main__":
    rclpy.init()
    
    heading_ctrl = HeadingController()
    rclpy.spin(heading_ctrl)
    rclpy.shutdown()