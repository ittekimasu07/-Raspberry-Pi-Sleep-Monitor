import time

from gpiozero import AngularServo

servo = AngularServo(
    18,
    min_angle=0,
    max_angle=90
)

def open_curtain():

    servo.angle = 0

    time.sleep(1)

    servo.value = None

def close_curtain():

    servo.angle = 90

    time.sleep(1)

    servo.value = None