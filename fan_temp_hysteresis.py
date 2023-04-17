from gpiozero import CPUTemperature
import smbus
import signal
from time import sleep
from datetime import datetime

DEVICE_ADDRESS = 0x0d
REGISTER_ADDRESS = 0x08

bus_number = 1
hysteresis_temp : float = 10.0
trigger_temp : float = 52.0
max_attempts = 3
sleep_seconds = 2.0

temperature : float
last_fan_status = ""

def log(msg):
    print('{}: {}'.format(datetime.now(), msg))

def tidyup(msg, *args):
    log("Caught terminate signal. Cleanup fan off.")
    set_fan("OFF")
    exit(0)

def set_fan(state: str):
    success = False
    attempt = 1
    value = 0x01 if state == "ON" else 0x00
    while not success and attempt <= max_attempts:
        try:
            i2c.write_byte_data(DEVICE_ADDRESS, REGISTER_ADDRESS, value)
        except IOError as e:
            if attempt <= max_attempts:
                attempt += 1
            else:
                msg = "Cannot write to i2c device after {} attempts.".format(attempt)
                log(msg + " Aborting.")
                raise RuntimeError(msg) from e
        else:
            success = True

signal.signal(signal.SIGINT, tidyup)
signal.signal(signal.SIGTERM, tidyup)

#Reference of smbus module exceptions:
# https://github.com/Gadgetoid/py-smbus/blob/master/library/smbusmodule.c
try:
    i2c = smbus.SMBus(bus_number)
except OverflowError as e:
    msg = "Bus number is invalid when try opening bus '{}'".format(bus_number)
    log(msg)
    raise RuntimeError(msg) from e
except IOError as e:
    msg = "IO Error: Cannot open bus '{}'".format(bus_number)
    log(msg)
    raise RuntimeError(msg) from e

while True:
    fan_status = "NONE"
    temperature = CPUTemperature().temperature

    if temperature >= trigger_temp:
        fan_status = "ON"
    elif temperature <= trigger_temp - hysteresis_temp:
        fan_status = "OFF"

    if fan_status != "NONE" and fan_status != last_fan_status:
        last_fan_status = fan_status
        set_fan(fan_status)
        log('Temp: {}°C, Fan action: {}'.format(CPUTemperature().temperature, fan_status))
    else:
        print('Temp: {}°C'.format(CPUTemperature().temperature))
        
    sleep(sleep_seconds)

#OFF: i2cset -y 1 0x0d 0x08 0x00
#ON:  i2cset -y 1 0x0d 0x08 0x01
