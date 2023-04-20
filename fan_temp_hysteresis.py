from gpiozero import CPUTemperature
import smbus2
import signal
from time import sleep
import logging
from systemd import journal

DEVICE_ADDRESS = 0x0d
REGISTER_ADDRESS = 0x08
MODULE_NAME = "yahboom-fan-ctrl"

bus_number = 1
hysteresis_temp : float = 10.0
trigger_temp : float = 52.0
max_attempts = 3
sleep_seconds = 2.0
log_file = "./" + MODULE_NAME + ".log"
verbose = 1

temperature : float
last_fan_status = ""

def tidyup(signal, frame):
    logger.info("Caught terminate signal '{}'. Turn fan off.\n".format(signal))
    set_fan("OFF")
    exit(0)

def set_fan(state: str):
    success = False
    attempt = 1
    value = 0x01 if state == "ON" else 0x00
    while not success and attempt <= max_attempts:
        try:
            with smbus2.SMBus(bus_number) as i2c:
                i2c.enable_pec(True)
                i2c.write_byte_data(DEVICE_ADDRESS, REGISTER_ADDRESS, value)
                i2c.close()
        except (FileNotFoundError, PermissionError, IOError) as e:
            if attempt <= max_attempts:
                attempt += 1
                if verbose >= 2:
                    logger.exception("Write i2c error, attempt {}.".format(attempt), exc_info=True)
            else:
                msg = "Cannot write to i2c device after {} attempts.".format(attempt)
                logger.critical(msg + " Aborting\n.", exc_info=True)
                raise RuntimeError(msg) from e
        else:
            success = True

# System signal management
signal.signal(signal.SIGINT, tidyup)
signal.signal(signal.SIGKILL, tidyup)
signal.signal(signal.SIGTERM, tidyup)

#Log management
# Reference: https://docs.python.org/3.9/howto/logging.html
logger = logging.getLogger(MODULE_NAME)
logger.setLevel(logging.DEBUG if verbose >=2 else logging.INFO)
# Reference for log to file: https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG if verbose >=2 else logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

#Init
logger.info("Starting {} log.".format(MODULE_NAME))
try:
    with smbus2.SMBus(bus_number) as i2c:
        i2c.enable_pec(True)
        i2c.write_byte_data(DEVICE_ADDRESS, REGISTER_ADDRESS, 0x00)
        i2c.close()
except Exception as e:
    msg = "Cannot open i2c device at address '{}'! Aborting\n.".format(hex(DEVICE_ADDRESS))
    logger.critical(msg)
    raise RuntimeError(msg) from e
else:
    logger.info("Connected successfully to i2c device at address '{}'".format(hex(DEVICE_ADDRESS)))

#Main loop
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
        logger.info('Temp: {}°C, Fan action: {}'.format(CPUTemperature().temperature, fan_status))
    elif verbose >= 2:
        logger.debug('Temp: {}°C'.format(CPUTemperature().temperature))

    sleep(sleep_seconds)

#OFF: sudo i2cset -y 1 0x0d 0x08 0x00
#ON:  sudo i2cset -y 1 0x0d 0x08 0x01
