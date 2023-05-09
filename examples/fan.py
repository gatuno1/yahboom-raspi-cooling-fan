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
state: int = 0
state_text: str = ""

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
    try:
        if state == 0:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x00)
            state_text = "0"
            time.sleep(2)
        elif state == 1:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x02)
            state_text = "20"
        elif state == 2:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x03)
            state_text = "30"
        elif state == 3:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x04)
            state_text = "40"
        elif state == 4:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x05)
            state_text = "50"
        elif state == 5:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x06)
            state_text = "60"
        elif state == 6:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x07)
            state_text = "70"
        elif state == 7:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x08)
            state_text = "80"
        elif state == 8:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x09)
            state_text = "90"
        elif state == 9:
            bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x01)
            state_text = "100"

    except Exception as e:
        print(
            f"Cannot write to i2c device at bus {bus_number}, address '{hex(DEVICE_ADDR)}'! Aborting.\n",
            file=sys.stderr)
        exit(1)

    print(f"Fan speed: {state_text}%")
    state += 1

    if state > 9:
        time.sleep(1.0)
        state = 0
    time.sleep(1.0)
