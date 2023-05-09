#!/usr/bin/env python3
import smbus2
import sys
import time

# Device address
DEVICE_ADDR = 0x0d
# Fan control register
FAN_SPEED_REG = 0x08

# Global variables
bus_number: int = 1  # raspberry pi with 256MB uses bus_number = 0
temperature: float = 0.0
level_temp: float = 0.0
state_text = ""
range_text = ""


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

while True:
    temperature = get_cpu_temp()

    if abs(temperature - level_temp) >= 1:
        try:
            if temperature <= 45:
                level_temp = 45
                bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x00)
                range_text = "<= 45"
                state_text = "0"
            elif temperature <= 47:
                level_temp = 47
                bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x04)
                range_text = "<= 47"
                state_text = "40"
            elif temperature <= 49:
                level_temp = 49
                bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x06)
                range_text = "<= 49"
                state_text = "60"
            elif temperature <= 51:
                level_temp = 51
                bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x08)
                range_text = "<= 51"
                state_text = "80"
            elif temperature <= 53:
                level_temp = 53
                bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x09)
                range_text = "<= 53"
                state_text = "90"
            else:
                level_temp = 55
                bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x01)
                range_text = "> 53"
                state_text = "100"

        except Exception as e:
            print(
                f"Cannot write to i2c device at bus {bus_number}, address '{hex(DEVICE_ADDR)}'! Aborting.\n")
            exit(2)

        print(f"Fan speed: {state_text}%, at range {range_text}°C.")

    time.sleep(1.0)
