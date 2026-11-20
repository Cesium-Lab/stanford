#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

# import the message type to use
from std_msgs.msg import String, Bool
from geometry_msgs.msg import Twist


class Heartbeat(Node):
    def __init__(self) -> None:
        # initialize base class (must happen before everything else)
        super().__init__("heartbeat")

        # a heartbeat counter
        self.hb_counter = 0

        # create publisher with: self.create_publisher(<msg type>, <topic>, <qos>)
        self.hb_pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.kill_sub = self.create_subscription(Bool, "/kill", self.kill_callback, 10)


        # create a timer with: self.create_timer(<second>, <callback>)
        self.hb_timer = self.create_timer(0.2, self.hb_callback)

        # create subscription with: self.create_subscription(<msg type>, <topic>,
        # <callback>, <qos>)
        self.motor_sub = self.create_subscription(
            Bool, "/health/motor", self.health_callback, 10
        )

    def hb_callback(self) -> None:
        """
        Heartbeat callback triggered by the timer
        """
        # construct heartbeat message
        msg = Twist()
        msg.linear.x = 0.1
        msg.angular.z = 0.0

        # publish heartbeat message
        self.hb_pub.publish(msg)

        # print message
        print(msg)

        # increment counter
        self.hb_counter += 1

    def kill_callback(self, msg: Bool) -> None:
        if msg.data:
            self.hb_timer.cancel()

            message = Twist()
            self.hb_pub.publish(message)


    def health_callback(self, msg: Bool) -> None:
        """
        Sensor health callback triggered by subscription
        """
        if not msg.data:
            self.get_logger().fatal("Heartbeat stopped")
            self.hb_timer.cancel()


if __name__ == "__main__":
    rclpy.init()
    node = Heartbeat()
    rclpy.spin(node)
    rclpy.shutdown()