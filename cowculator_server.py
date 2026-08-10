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
import random
from cowculator.srv import Calculate


class CalculatorServer(Node):

    def __init__(self):
        super().__init__('calculator_server')

        self.srv = self.create_service(
            Calculate,
            'calculate',
            self.calculate_callback
        )

        self.get_logger().info('Calculator service ready!')

    def calculate_callback(self, request, response):

        operation = request.operation.lower()
        a = request.a
        b = request.b

        try:
            num = random.randint(1, 3)
            if num == 3:
                result = "the friendly cow is busy and cannot listen to ur silly requests. moooooooooooooo"
            else:
                if operation == '+':
                    result = a + b

                elif operation == '-':
                    result = a - b

                elif operation == '*':
                    result = a * b

                elif operation == '/':
                    if b == 0:
                        response.result = 'Error: the all knowing friendly cow predicted you would do this'
                        return response

                    result = a / b

                elif operation == '^':
                    result = a ** b

                elif operation == 'b':
                    result = bin(int(a))

                else:
                    response.result = f'Error: lol ur bad at this "{operation}"'
                    return response

                response.result = str(result)

        except Exception as e:
            response.result = f'Error: {e}'

        self.get_logger().info(
            f'{operation}: a={a}, b={b} -> {response.result}'
        )

        return response

def main(args=None):
    rclpy.init(args=args)

    node = CalculatorServer()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

    try:
        rclpy.spin(cowculator_server)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
