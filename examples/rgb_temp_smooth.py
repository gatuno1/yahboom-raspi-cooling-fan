#!/usr/bin/env python3
#
# Controls the RGB's based on the Pi's temperature. Uses an
# algorithm to compute the color dynamically.
#

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
RGB_OFF_REG = 0x07
# Fan control register
FAN_SPEED_REG = 0x08

# Program constants
MAX_LED = 3
RGB_COLD = (0x00, 0x00, 0xff)
RGB_HOT = (0xFF, 0x00, 0x00)

# Global variables
bus_number: int = 1  # raspberry pi with 256MB use bus_number = 0
temperature: float = 0.0
previousColor = 0


def calculateColor(temperature):
    """
    Blend COLD and HOT together using a weighted average
    technique. The weight is calculated from the temperature,
    given expected bounds of 45 and 63.
    """
    lowerBound = 45
    upperBound = 50

    bracketedTemp = min(max(lowerBound, temperature), upperBound)
    percentHot = float(bracketedTemp - lowerBound) / (upperBound - lowerBound)
    percentNot = 1 - percentHot

    avgColor = []
    for i in (0, 1, 2):
        avgByte = int(RGB_HOT[i] * percentHot + RGB_COLD[i] * percentNot)
        avgColor.append(avgByte)

    print("Calulated average: " + avgColor.__repr__())

    return avgColor


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


def get_cpu_temp() -> float:
    CPU_TEMP_FILE = "/sys/class/thermal/thermal_zone0/temp"
    temp: float = -173.15
    try:
        with open(CPU_TEMP_FILE, 'r') as f:
            temp_str = f.readline()
            temp = float(temp_str.strip()) / 1000.0
    except FileNotFoundError:
        print(
            f"Error: Cannot find temperature file '{CPU_TEMP_FILE}'.",
            file=sys.stderr)
        exit(3)
    except PermissionError:
        print(
            f"Error: Permission denied to access temperature file '{CPU_TEMP_FILE}'.",
            file=sys.stderr)
        exit(3)
    except:
        print(
            f"Error: Unknown error reading temperature file '{CPU_TEMP_FILE}'.",
            file=sys.stderr)
        exit(3)
    return temp


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

while True:
    temperature = get_cpu_temp()
    print("CPU Temperature: ", temperature)
    color = calculateColor(temperature)

    if color != previousColor:
        setRGB(MAX_LED, color[0], color[1], color[2])
        previousColor = color

    time.sleep(0.5)
