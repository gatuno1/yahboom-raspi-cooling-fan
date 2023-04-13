import smbus
import re
import time
import subprocess as sp

DEV_ADDR = 0x0d
FAN_REG = 0x08
WRITE_RETRIES : int = 3
temperature : float
hysteresis_temp : float = 10.0
trigger_temp : float = 50.0
fan_status = "OFF"
last_fan_status = None
values_dict = {"OFF": 0x00, "ON": 0x01}

bus = smbus.SMBus(1)
pattern = re.compile(r'temp=(\d+\.\d+)')


def set_fan(state: str):
    retry = 0
    value = values_dict[state]
    if ++retry <= WRITE_RETRIES:
        bus.write_byte_data(DEV_ADDR, FAN_REG, value)


def read_temp():
    proc = sp.run(['vcgencmd', 'measure_temp'], stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True)
    if proc.returncode != 0:
        print('Error: temperature reading failed.')
        exit(1)
    match = pattern.search(proc.stdout)
    if match:
        temp_text = match.group(1)
    else:
        print('Error: temperature reading failed.')
        exit(1)
    temp = float(temp_text)
    return temp, temp_text


set_fan(fan_status)
print("Init Fan: " + fan_status)

while True:
    fan_status = None
    temperature, CPU_TEMP = read_temp(pattern)

    if temperature >= trigger_temp:
        last_fan_status = fan_status
        fan_status = "ON"
    elif temperature <= trigger_temp - hysteresis_temp:
        last_fan_status = fan_status
        fan_status = "OFF"

    if fan_status is not None and fan_status != last_fan_status:
        set_fan(fan_status)

    print("Temp: " + CPU_TEMP + "°C" + ", Fan: " + fan_status)
    time.sleep(1.5)
