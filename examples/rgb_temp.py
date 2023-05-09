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
RGB_OFF_REG = 0x07

# Program constants
MAX_LED = 3

# Global variables
bus_number: int = 1  # raspberry pi with 256MB uses bus_number = 0
state: int = 0
temperature: float = 0
level_temp: float = 0


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
        print(f"Error: Cannot find temperature file '{CPU_TEMP_FILE}'.")
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

    if abs(temperature - level_temp) >= 1:
        if temperature <= 45:
            level_temp = 45
            setRGB(MAX_LED, 0x00, 0x00, 0xff)
        elif temperature <= 47:
            level_temp = 47
            setRGB(MAX_LED, 0x1e, 0x90, 0xff)
        elif temperature <= 49:
            level_temp = 49
            setRGB(MAX_LED, 0x00, 0xbf, 0xff)
        elif temperature <= 51:
            level_temp = 51
            setRGB(MAX_LED, 0x5f, 0x9e, 0xa0)
        elif temperature <= 53:
            level_temp = 53
            setRGB(MAX_LED, 0xff, 0xff, 0x00)
        elif temperature <= 55:
            level_temp = 55
            setRGB(MAX_LED, 0xff, 0xd7, 0x00)
        elif temperature <= 57:
            level_temp = 57
            setRGB(MAX_LED, 0xff, 0xa5, 0x00)
        elif temperature <= 59:
            level_temp = 59
            setRGB(MAX_LED, 0xff, 0x8c, 0x00)
        elif temperature <= 61:
            level_temp = 61
            setRGB(MAX_LED, 0xff, 0x45, 0x00)
        elif temperature >= 63:
            level_temp = 63
            setRGB(MAX_LED, 0xff, 0x00, 0x00)

    time.sleep(0.5)
