#!/usr/bin/env python3
import smbus2
import sys
import time

# Device address
DEVICE_ADDR = 0x0d
# LED registers
LED_SELECT_REG = 0x00
LED_R_VALUE_REG = 0x01
LED_G_VALUE_REG = 0x02
LED_B_VALUE_REG = 0x03
# RGB effects registers
RGB_EFFECT_REG = 0x04
RGB_SPEED_REG = 0x05
RGB_COLOR_REG = 0x06
RGB_OFF_REG = 0x07

# Program constants
MAX_LED = 3

# Global variables
bus_number: int = 1  #raspberry pi with 256MB uses bus_number = 0

def setRGB(num, r, g, b):
    if num >= MAX_LED:
        bus.write_byte_data(
            DEVICE_ADDR, LED_SELECT_REG, 0xff)   # Brightness
        bus.write_byte_data(DEVICE_ADDR, LED_R_VALUE_REG, r & 0xff)
        bus.write_byte_data(DEVICE_ADDR, LED_G_VALUE_REG, g & 0xff)
        bus.write_byte_data(DEVICE_ADDR, LED_B_VALUE_REG, b & 0xff)
    elif num >= 0:
        bus.write_byte_data(DEVICE_ADDR, LED_SELECT_REG, num & 0xff)
        bus.write_byte_data(DEVICE_ADDR, LED_R_VALUE_REG, r & 0xff)
        bus.write_byte_data(DEVICE_ADDR, LED_G_VALUE_REG, g & 0xff)
        bus.write_byte_data(DEVICE_ADDR, LED_B_VALUE_REG, b & 0xff)


def setRGBEffect(effect):
    if effect >= 0 and effect <= 4:
        bus.write_byte_data(DEVICE_ADDR, RGB_EFFECT_REG, effect & 0xff)


def setRGBSpeed(speed):
    if speed >= 1 and speed <= 3:
        bus.write_byte_data(DEVICE_ADDR, RGB_SPEED_REG, speed & 0xff)


def setRGBColor(color):
    if color >= 0 and color <= 6:
        bus.write_byte_data(DEVICE_ADDR, RGB_COLOR_REG, color & 0xff)


# Initialize i2c bus
try:
    bus = smbus2.SMBus(bus_number)
    bus.enable_pec(True)  # Enable "Packet Error Checking"
except Exception as e:
    print(
        f"Cannot open i2c device at bus {bus_number}, address '{hex(DEVICE_ADDR)}'! Aborting.\n",
        file=sys.stderr)
    exit(1)

bus.write_byte_data(DEVICE_ADDR, RGB_OFF_REG, 0x00)
time.sleep(1.0)

setRGBEffect(1)
setRGBSpeed(3)
setRGBColor(4)
