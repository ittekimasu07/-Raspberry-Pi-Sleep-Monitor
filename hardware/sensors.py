import smbus
import spidev

from gpiozero import DigitalInputDevice

PIR_PIN = 17

pir = DigitalInputDevice(PIR_PIN)


# ADT7410　初期化
i2c = smbus.SMBus(1)

ADT_ADDRESS = 0x48
ADT_REGISTER = 0x00

# MCP3008　初期化
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

# 各センサーのデータ読み取り変数
def read_adt7410():

    word_data = i2c.read_word_data(
        ADT_ADDRESS,
        ADT_REGISTER
    )

    data = (
        ((word_data & 0xff00) >> 8)
        |
        ((word_data & 0xff) << 8)
    )

    data >>= 3

    if data & 0x1000 == 0:
        temperature = data * 0.0625
    else:
        temperature = (
            ((~data & 0x1fff) + 1)
            * -0.0625
        )

    return round(temperature, 2)

def read_adc(channel):

    adc = spi.xfer2(
        [1, (8 + channel) << 4, 0]
    )

    value = (
        ((adc[1] & 3) << 8)
        + adc[2]
    )

    return value


def read_ldr():
    return read_adc(0)

