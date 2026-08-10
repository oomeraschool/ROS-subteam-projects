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
from rclpy.node import Node
from cowculator.srv import Calculate

cow = r"""
                                       /;    ;\
                                   __  \\____//
                                  /{_\_/   `'\____
                                  \___   (o)  (o  }
       _____________________________/          :--'
   ,-,'`@@@@@@@@       @@@@@@         \_    `__\
  ;:(  @@@@@@@@@        @@@             \___(o'o)
  :: )  @@@@          @@@@@@        ,'@@(  `===='
  :: : @@@@@:          @@@@         `@@@:
  :: \  @@@@@:       @@@@@@@)    (  '@@@'
  ;; /\      /`,    @@@@@@@@@\   :@@@@@)
  ::/  )    {_----------------:  :~`,~~;
 ;;'`; :   )                  :  / `; ;   
;;;; : :   ;                  :  ;  ; :
`'`' / :  :                   :  :  : :
    )_ \__;      ";"          :_ ;  \_\       `,','
    :__\  \    * `,'*         \  \  :  \   *  8`;'*  *
        `^'     \ :/           `^'  `-^-'   \v/ :  \/⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

class CalculatorClient(Node):

    def __init__(self):
        super().__init__('calculator_client')

        self.client = self.create_client(
            Calculate,
            'calculate'
        )

        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(
                'the friendly cow is on vacation u must wait...'
            )

    def send_request(self, operation, a, b):
        request = Calculate.Request()

        request.operation = operation
        request.a = a
        request.b = b

        return self.client.call_async(request)

def main(args=None):
    password = input("Enter the secure password: ")
    if password != "moomoo the friendly cow":
        print("Access denied. MOOOOOOOO!!!")
        exit()
    print("***** Welcome to the Cowculator *****")
    print(cow)
    rclpy.init(args=args)
    node = CalculatorClient()
    operation = ""
    while operation != "exit":
        operation = input("ur operation here: ")
        a = float(input("ur first num here: "))
        b = float(input("ur second num here: "))
        
        future = node.send_request(operation, a, b)

        rclpy.spin_until_future_complete(node, future)
        response = future.result()

        node.get_logger().info(
            f'Result: {response.result}'
        )

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
