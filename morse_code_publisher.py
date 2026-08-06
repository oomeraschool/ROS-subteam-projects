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

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        
        # Start a background thread to handle user input without blocking ROS
        self.input_thread = threading.Thread(target=self.get_user_input, daemon=True)
        self.input_thread.start()

    def get_user_input(self):
        # This runs safely in the background
        while rclpy.ok():
            try:
                user_msg = input(">>> ")
                if user_msg.lower() == 'exit':
                    rclpy.shutdown()
                    break
                
                # Publish the message
                msg = String()
                msg.data = user_msg
                self.publisher_.publish(msg)
                self.get_logger().info(f'Publishing: "{user_msg}"')
            except EOFError:
                break

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()

    try:
        rclpy.spin(minimal_publisher)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
