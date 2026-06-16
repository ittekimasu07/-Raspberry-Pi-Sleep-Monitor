from gpiozero import DigitalInputDevice
from time import sleep

btn = DigitalInputDevice(
    26,
    pull_up=True
)

while True:
    print(btn.value)
    sleep(0.5)