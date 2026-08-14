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

# ONLY RUN ON A PI
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import RPi.GPIO
from std_msgs.msg import String
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW)

MORSE_CODE_DICT = { 'A':'.-', 'B':'-...',
                    'C':'-.-.', 'D':'-..', 'E':'.',
                    'F':'..-.', 'G':'--.', 'H':'....',
                    'I':'..', 'J':'.---', 'K':'-.-',
                    'L':'.-..', 'M':'--', 'N':'-.',
                    'O':'---', 'P':'.--.', 'Q':'--.-',
                    'R':'.-.', 'S':'...', 'T':'-',
                    'U':'..-', 'V':'...-', 'W':'.--',
                    'X':'-..-', 'Y':'-.--', 'Z':'--..',
                    '1':'.----', '2':'..---', '3':'...--',
                    '4':'....-', '5':'.....', '6':'-....',
                    '7':'--...', '8':'---..', '9':'----.',
                    '0':'-----', ', ':'--..--', '.':'.-.-.-',
                    '?':'..--..', '/':'-..-.', '-':'-....-',
                    '(':'-.--.', ')':'-.--.-'}

# Function to encrypt the string
# according to the morse code chart
def encrypt(message):
    cipher = ''
    for letter in message:
        if letter != ' ':
            if letter.isalpha():
                letter = letter.upper()
            # Looks up the dictionary and adds the
            # corresponding morse code
            # along with a space to separate
            # morse codes for different characters
            cipher += MORSE_CODE_DICT[letter] + ' '
        else:
            # 1 space indicates different characters
            # and 2 indicates different words
            cipher += ' '

    return cipher
def morse(message):
    while message:
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)
        if message[0] == '.':
            GPIO.output(18, GPIO.HIGH)
            time.sleep(1)
            message = message[1:]
        elif message[0] == '-':
            GPIO.output(18, GPIO.HIGH)
            time.sleep(3)
            message = message[1:]
        elif message[0] == ' ' and message[1] == ' ':
            GPIO.output(18, GPIO.LOW)
            time.sleep(6)
            message = message[2:]
        else:
            GPIO.output(18, GPIO.LOW)
            time.sleep(3)
            message = message[1:]

    GPIO.output(18, GPIO.LOW)
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
        morse_message = encrypt(msg.data)
        self.get_logger().info('I heard: "%s"' % morse_message)
        morse(morse_message)
        


def main(args=None):
    try:
        with rclpy.init(args=args):
            minimal_subscriber = MinimalSubscriber()

            rclpy.spin(minimal_subscriber)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()
