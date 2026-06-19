import time

from gpiozero import AngularServo

servo_left = AngularServo(
    18,
    min_angle=0,
    max_angle=90
)

servo_right = AngularServo(
    19,
    min_angle=0,
    max_angle=90
)

def open_curtain():

    servo_left.angle = 0
    servo_right.angle = 0

    time.sleep(1)

    servo_left.value = None
    servo_right.value = None

def close_curtain():

    servo_left.angle = 90
    servo_right.angle = 90

    time.sleep(1)

    servo_left.value = None
    servo_right.value = None