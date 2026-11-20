#!/usr/bin/env python3

import rclpy

from asl_tb3_lib.control import BaseHeadingController
from asl_tb3_lib.math_utils import wrap_angle
from asl_tb3_msgs.msg import TurtleBotControl, TurtleBotState
from std_msgs.msg import String, Bool

class PerceptionController(BaseHeadingController):
    def __init__(self):
        super().__init__("perception_controller")
        
        self.active = True # do we nneed this?
        self.declare_parameter("active", True)
        
        self.image_detected = False
        

        self.detector_sub = self.create_subscription(Bool, "/detector_bool", self.detector_callback, 10)

        
    @property
    def val_active(self) -> bool:
        return self.get_parameter("active").value
        
    # overrides
    def compute_control_with_goal(self,
            state: TurtleBotState,
            goal: TurtleBotState
        ) -> TurtleBotControl:
        
        msg = TurtleBotControl()
        msg.omega = 0.2 if not self.image_detected else 0.0
        
        return msg
    
    
    def detector_callback(self, msg: Bool) -> None:
        self.image_detected = msg.data
    
if __name__ == "__main__":
    rclpy.init()
    
    perception_ctrl = PerceptionController()
    rclpy.spin(perception_ctrl)
    rclpy.shutdown()