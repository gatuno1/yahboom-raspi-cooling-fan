from gpiozero import CPUTemperature
import smbus2
import signal
import sys
from time import sleep
from enum import Enum
import logging
from systemd.journal import JournalHandler

DEVICE_ADDRESS = 0x0d
REGISTER_ADDRESS = 0x08
MODULE_NAME = "yahboom-fan-ctrl"

# Configuration variables
bus_number = 1
hysteresis_temp : float = 10.0
trigger_temp : float = 55.0
max_attempts = 3
sleep_seconds = 2.0
log_file = "./" + MODULE_NAME + ".log"
verbose = 1

# Reference for enums: https://docs.python.org/3/howto/enum.html
class FanActions(Enum):
    NONE = 0x00
    OFF = 0x01
    ON = 0x02

# Global variables
temperature : float
fan_action : FanActions

# Reference to get name: https://stackoverflow.com/a/35996948/17892898
# signal.Signals(signum) requires python 3.5 or higher
def signal_name(signum: int):
    try:
        if sys.version_info >= (3, 8):
            return signal.strsignal(signal.Signals(signum))
        else:
            sig = signal.Signals(signum)
            return sig.name
    except KeyError:
        return 'SIG_UNKNOWN'
    except ValueError:
        return 'SIG_UNKNOWN'

def tidyup(signal_num: int, frame):
    logger.info("Caught terminate signal '{}'. Turn fan off.\n".format(signal_name(signal_num)))
    set_fan(FanActions.OFF)
    exit(0)

def set_fan(action: FanActions):
    success = False
    attempt = 1
    value = 0x01 if action == FanActions.ON else 0x00
    while not success and attempt <= max_attempts:
        try:
            with smbus2.SMBus(bus_number) as i2c:
                i2c.enable_pec(True)
                i2c.write_byte_data(DEVICE_ADDRESS, REGISTER_ADDRESS, value)
                i2c.close()
        except:
            if attempt <= max_attempts:
                attempt += 1
                if verbose >= 2:
                    logger.exception("Write i2c error, attempt {}.".format(attempt), exc_info=True)
            else:
                msg = "Cannot write to i2c device after {} attempts.".format(attempt)
                logger.critical(msg, exc_info=True)
                exit(2)
        else:
            success = True

# System signal management
signal.signal(signal.SIGINT, tidyup)
signal.signal(signal.SIGQUIT, tidyup)
signal.signal(signal.SIGTERM, tidyup)

#Log management
# Reference: https://docs.python.org/3.9/howto/logging.html
logger = logging.getLogger(MODULE_NAME)
logger.addHandler(JournalHandler())
logger.setLevel(logging.DEBUG if verbose >=2 else logging.INFO)
# Reference for log to file: https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module
fh = logging.FileHandler(log_file)
fh.setLevel(logging.DEBUG if verbose >=2 else logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

# Check python version on runtime
if sys.version_info < (3, 5):
    msg = "Python version must be 3.5 or higher.\n"
    logger.critical(msg)
    exit(127)

#Init
logger.info("Starting {} log.".format(MODULE_NAME))
try:
    with smbus2.SMBus(bus_number) as i2c:
        i2c.enable_pec(True)
        i2c.write_byte_data(DEVICE_ADDRESS, REGISTER_ADDRESS, 0x00)
        i2c.close()
except Exception as e:
    msg = "Cannot open i2c device at bus {}, address '{}'! Aborting.\n".format(bus_number, hex(DEVICE_ADDRESS))
    logger.critical(msg)
    raise RuntimeError(msg) from e
else:
    logger.info("Connected successfully to i2c device at bus {}, address '{}'.".format(bus_number, hex(DEVICE_ADDRESS)))

logger.info("Initial Temp: {:.2f}°C, trigger temp: {:.2f}°C, hys. temp: {:.2f}°C ".format(CPUTemperature().temperature, trigger_temp, -hysteresis_temp))

#Main loop
while True:
    fan_action = FanActions.NONE
    temperature = CPUTemperature().temperature

    if temperature >= trigger_temp:
        fan_action = FanActions.ON
    elif temperature <= trigger_temp - hysteresis_temp:
        fan_action = FanActions.OFF

    if fan_action != FanActions.NONE:
        set_fan(fan_action)
        logger.info('Temp: {:.2f}°C, Fan action: {}'.format(CPUTemperature().temperature, fan_action))
    elif verbose >= 2:
        logger.debug('Temp: {:.2f}°C'.format(CPUTemperature().temperature))

    sleep(sleep_seconds)

#OFF: sudo i2cset -y 1 0x0d 0x08 0x00
#ON:  sudo i2cset -y 1 0x0d 0x08 0x01
