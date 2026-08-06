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
import threading
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import cv2
import numpy as np

class Camera(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        
        # Start a background thread to handle user input without blocking ROS
        self.input_thread = threading.Thread(target=self.get_user_input, daemon=True)
        self.input_thread.start()

    def get_user_input(self):
        # This runs safely in the background
        while rclpy.ok():
            self.cap = cv2.VideoCapture(0)

            if not self.cap.isOpened():
                self.get_logger().error("Cannot open webcam")
                return

            ret, frame = self.cap.read()
            if ret:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Create mask for the color range
                mask = cv2.inRange(hsv, np.array((0, 120, 70)), np.array((10, 255, 255)))

                # Get coordinates where mask is non-zero
                coords = np.column_stack(np.where(mask > 0))

                # Convert from (row, col) to (x, y)
                coords_list = [(int(x), int(y)) for y, x in coords]

                # Example: Detect pure red range in HSV
                # HSV ranges vary depending on lighting; adjust as needed
                if coords_list:
                    try:
                        msg = String()
                        msg.data = f"{coords_list[0][0]} {coords_list[0][1]}"
                        self.publisher_.publish(msg)
                        self.get_logger().info(f'Publishing: "{msg.data}"')
                    except:
                        pass
                else:
                    msg = String()
                    msg.data = f"640 360"
                    self.publisher_.publish(msg)
                    self.get_logger().info(f'Wow, no red in your picture. Publishing: "{msg.data}"')
            else:
                self.get_logger().error("Failed to capture image.")

def main(args=None):
    rclpy.init(args=args)
    camera = Camera()

    try:
        rclpy.spin(camera)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
