import smbus
import re
import time
import subprocess as sp
from typing import Tuple

DEV_ADDR = 0x0d
FAN_REG = 0x08
WRITE_RETRIES : int = 3

temp_value : float
hysteresis_temp : float = 10.0
trigger_temp : float = 52.0
fan_status = ""
last_fan_status : str = "FLOAT"

values_dict = {"OFF": 0x00, "ON": 0x01}

bus = smbus.SMBus(1)
pattern = re.compile(r'temp=(\d+\.\d+)')


def set_fan(state: str):
    attempt = 1
    success = False
    value : int = values_dict[state]
    print("State: '{}', value: {}".format(state,value))
    while not success and attempt <= WRITE_RETRIES:
        try:
            bus.write_byte_data(DEV_ADDR, FAN_REG, value)
        except BaseException as e:
            print("Failed attempt #{} to write.".format(attempt))
            attempt += 1
            if attempt > WRITE_RETRIES:
                print("Giving up after {} attempts.".format(WRITE_RETRIES))
                raise e
            time.sleep(0.2)
        else:
            success = True
            if attempt >= 1:
                print("Write success on attempt #{}.".format(attempt))



def read_temp() -> Tuple[float, str]:
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
    return temp, temp_text;


# set_fan(fan_status)
# print("Init Fan: " + fan_status)

while True:
    fan_status = None
    temp_value, temperature = read_temp()

    if temp_value >= trigger_temp:
        fan_status = "ON"
    elif temp_value <= trigger_temp - hysteresis_temp:
        fan_status = "OFF"

    if fan_status != None:
    #if fan_status != "" and fan_status != last_fan_status:
        #last_fan_status = fan_status
        set_fan(fan_status)
        print("Temp: {}°C, Fan: {}".format(temperature, fan_status))
    else:
        print("Temp: {}°C".format(temperature))

    time.sleep(1.5)

#OFF: i2cset -y 1 0x0d 0x08 0x00
#ON:  i2cset -y 1 0x0d 0x08 0x01
