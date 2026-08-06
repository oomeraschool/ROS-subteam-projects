# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from std_msgs.msg import String
import numpy as np

K = np.array([
    [1000.0,    0.0, 640.0],
    [   0.0, 1000.0, 360.0],
    [   0.0,    0.0,   1.0]
])

K_inv = np.linalg.inv(K)
R = np.eye(3)

def direction(message):
    x, y = message.split()
    x = int(x)
    y = int(y)
    X_cam = np.dot(R.T, np.dot(K_inv, [x, y, 1]))

    # Direction in camera coordinates
    dir_vec = X_cam / np.linalg.norm(X_cam)

    # Azimuth and elevation
    azimuth_rad = np.arctan2(dir_vec[0], dir_vec[2])
    elevation_rad = np.arctan2(dir_vec[1], dir_vec[2])

    azimuth_deg = np.degrees(azimuth_rad)
    elevation_deg = np.degrees(elevation_rad)

    return f"Azimuth={azimuth_deg:.2f}°, Elevation={elevation_deg:.2f}°"

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
    def listener_callback(self, msg):
        
        self.get_logger().info('Your information here: "%s"' % direction(msg.data))

def main(args=None):
    try:
        with rclpy.init(args=args):
            minimal_subscriber = MinimalSubscriber()

            rclpy.spin(minimal_subscriber)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()
