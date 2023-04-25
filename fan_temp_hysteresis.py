import smbus2
import signal
import sys
import configparser
import os
from time import sleep
from enum import Enum
import logging
from systemd.journal import JournalHandler

DEVICE_ADDR = 0x0d
"""i2c device address used by yahboom RBG fan hat."""
FAN_REGISTER_ADDR = 0x08
"""i2c register address to regulate fan speed."""
MODULE_NAME = "yahboom-fan-ctrl"
"""Module name used for configuration file and log file."""

# Configuration global variables
bus_number : int = 1
"""i2c bus number."""
log_file : str = "./" + MODULE_NAME + ".log"
"""Log file path."""
verbose : int = 1
"""Verbosity level of messages."""

hysteresis_temp : float = 10.0
"""Temperature hysteresis to turn off fan, in Celsius."""
trigger_temp : float = 55.0
"""Temperature at which fan is turned on in Celsius."""
max_attempts = 3
"""Maximum number of attempts to write to i2c device."""
sleep_seconds = 2.0
"""Time to sleep between temperature checks, in seconds."""

# Reference for enums: https://docs.python.org/3/howto/enum.html
class FanActions(Enum):
    """Possible actions for fan."""
    NONE = 0x00
    """No action to be taken."""
    OFF = 0x01
    """Turn fan off."""
    ON = 0x02
    """Turn fan on."""

# Global variables
temperature : float
"""Current CPU temperature in Celsius."""
fan_action : FanActions
"""Action to be taken by fan."""
logger : logging.Logger
"""Logger object to write to log file and stdout."""

# Reference to get name: https://stackoverflow.com/a/35996948/17892898
# Note: Method signal.Signals(signum) requires python 3.5 or higher.
def signal_name(signum: int) -> str:
    """Get signal name from signal value.

    Args:
        signum (int): signal value

    Returns:
        str: Code name of signal
    """
    try:
        if sys.version_info >= (3, 8):
            return "{} - {}".format(signal.Signals(signum).name, signal.strsignal(signal.Signals(signum)))
        else:
            sig = signal.Signals(signum).name
            return sig.name
    except KeyError:
        return 'SIG_UNKNOWN'
    except ValueError:
        return 'SIG_UNKNOWN'

def tidyup(signal_num: int, frame):
    """Write to log, turn off fan and exit program.

    Args:
        signal_num (int): signal value
    """
    logger.info("Caught terminate signal '{}'. Turn fan off.\n".format(signal_name(signal_num)))
    set_fan(FanActions.OFF)
    exit(0)

def get_cpu_temp() -> float:
    """Get CPU temperature.

    Returns:
        float: CPU temperature in Celsius
    """
    CPU_TEMP_FILE = "/sys/class/thermal/thermal_zone0/temp"
    temp: float = -173.15
    try:
        with open(CPU_TEMP_FILE, 'r') as f:
            temp_str = f.readline()
            temp = float(temp_str.strip()) / 1000.0
    except FileNotFoundError:
        msg = "Error: Cannot find temperature file '{}'.".format(CPU_TEMP_FILE)
        logger.critical(msg, exc_info=True)
        exit(3)
    except PermissionError:
        msg = "Error: Permission denied to access temperature file '{}'.".format(CPU_TEMP_FILE)
        logger.critical(msg, exc_info=True)
        exit(3)
    except:
        msg = "Error: Unknown error reading temperature file '{}'.".format(CPU_TEMP_FILE)
        logger.critical(msg, exc_info=True)
        exit(3)
    return temp

def set_fan(action: FanActions):
    """Activate/deactivate fan, calling i2c write function.

    Args:
        action (FanActions): Requested action
    """
    success = False
    attempt = 1
    value = 0x01 if action == FanActions.ON else 0x00
    while not success and attempt <= max_attempts:
        try:
            with smbus2.SMBus(bus_number) as i2c:
                i2c.enable_pec(True)
                i2c.write_byte_data(DEVICE_ADDR, FAN_REGISTER_ADDR, value)
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

def read_config():
    """Read configuration from file or command line arguments.
    """
    # Read configuration from file
    config = configparser.ConfigParser()

    # Search for config file in /etc/yahboom-fan-ctrl/ and ./ directories
    config_file_paths = ["/etc/{}/{}.conf".format(MODULE_NAME, MODULE_NAME), "./{}.conf".format(MODULE_NAME)]
    for config_file_path in config_file_paths:
        if os.path.exists(config_file_path):
            config.read(config_file_path)
            break

    # Set configuration variables from file or default values
    bus_number = config.getint('DEFAULT', 'bus_number', fallback=bus_number)
    log_file = config.get('DEFAULT', 'log_file', fallback=log_file)
    verbose = config.getint('DEFAULT', 'verbose', fallback=verbose)

    hysteresis_temp = config.getfloat('FAN-CTRL', 'hysteresis_temp', fallback=hysteresis_temp)
    trigger_temp = config.getfloat('FAN-CTRL', 'trigger_temp', fallback=trigger_temp)
    max_attempts = config.getint('FAN-CTRL', 'max_attempts', fallback=max_attempts)
    sleep_seconds = config.getfloat('FAN-CTRL', 'sleep_seconds', fallback=sleep_seconds)


# # Read configuration from command line arguments
# parser = argparse.ArgumentParser(prog="MODULE_NAME", description="Yahboom fan control program")
# parser.add_argument("-b", "--bus_number", type=int, metavar="BUS_NUMBER",
#     dest="bus_number", help="I2C bus number (default: %(default)s)")
# parser.add_argument("-y", "--hysteresis_temp", type=float, metavar="HYSTERESIS_TEMP",
#     dest="hysteresis_temp", help="Hysteresis  (in degrees Celsius) (default: %(default)s)")
# parser.add_argument("-t", "--trigger_temp", type=float, metavar="TRIGGER_TEMP", dest="trigger_temp",
#     help="Temperature threshold to turn on the fan (in degrees Celsius) (default: %(default)s)")
# parser.add_argument("--max_attempts", type=int, metavar="MAX_ATTEMPTS", dest="max_attempts",
#     help="Maximum number of attempts to read temperature sensor (default: %(default)s)")
# parser.add_argument("-s", "--sleep_seconds", type=float, metavar="SLEEP_SECONDS", dest="sleep_seconds",
#     help="Time to wait between attempts to read temperature sensor (in seconds) (default: %(default)s)")
# parser.add_argument("-l", "--log_file", type=str, metavar="LOG_FILE", dest="log_file",
#     help="Path to log file (default: %(default)s)")
# parser.add_argument("-v", "--verbose", type=int, choices=[0, 1, 2], metavar="VERBOSITY_LEVEL",
#     dest="verbose",help="Verbosity level (0 = no output, 1 = info output, 2 = debug output) (default: %(default)s)")
# args = parser.parse_args()

# # Update configuration variables with command line arguments
# try:
#     if args.bus_number:
#         bus_number = args.bus_number
#     if args.hysteresis_temp:
#         hysteresis_temp = args.hysteresis_temp
#     if args.trigger_temp:
#         trigger_temp = args.trigger_temp
#     if args.max_attempts:
#         max_attempts = args.max_attempts
#     if args.sleep_seconds:
#         sleep_seconds = args.sleep_seconds
#     if args.log_file:
#         log_file = args.log_file
#     if args.verbose:
#         verbose = args.verbose
# except argparse.ArgumentError as exc:
#     print(exc)
#     parser.print_usage()

# # Check for invalid command line arguments
# invalid_args = []
# for arg in vars(args):
#     value = getattr(args, arg)
#     if value is None:
#         invalid_args.append(arg)

# if invalid_args:
#     print(f"Error: Invalid argument(s): {', '.join(invalid_args)}")
#     parser.print_usage()


def setup_logging(log_file: str, verbose_level: int) -> logging.Logger:
    """Setup of Log management, to file and journalctl.

    Args:
        log_file (str): file path to log file
        verbose_level (int): verbosity level

    Returns:
        logging.Logger: logger object
    """
    #
    # Reference: https://docs.python.org/3.9/howto/logging.html
    new_logger = logging.getLogger(MODULE_NAME)
    new_logger.addHandler(JournalHandler())
    new_logger.setLevel(logging.DEBUG if verbose_level >=2 else logging.INFO)
    # Reference for log to file: https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG if verbose_level >=2 else logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    new_logger.addHandler(fh)
    return new_logger

def init_communication():
    """Initialize communication with i2c device, also writing to log.
       If communication fails, exit with error code 2.
    """
    logger.info("Starting {} log.".format(MODULE_NAME))

    try:
        with smbus2.SMBus(bus_number) as i2c:
            i2c.enable_pec(True)
            i2c.write_byte_data(DEVICE_ADDR, FAN_REGISTER_ADDR, 0x00)
    except Exception as e:
        msg = "Cannot open i2c device at bus {}, address '{}'! Aborting.\n".format(bus_number, hex(DEVICE_ADDR))
        logger.critical(msg, exc_info=True)
        exit(2)
    else:
        logger.info("Connected successfully to i2c device at bus {}, address '{}'.".format(bus_number, hex(DEVICE_ADDR)))

    logger.info("Initial Temp: {:.2f}°C, trigger temp: {:.2f}°C, hys. temp: >={:.2f}°C ".format(get_cpu_temp(), trigger_temp, -hysteresis_temp))


def main():
    """Main function of the program.
       If python version is not 3.5 or higher, exit with error code 127.
    """
    # Log management
    logger = setup_logging(log_file, verbose)

    # Check python version on runtime
    if sys.version_info < (3, 5):
        msg = "Python version must be 3.5 or higher to run this program.\n"
        logger.critical(msg)
        exit(127)

    # Read configuration from file(s), affecting global configuration variables
    read_config()

    # System signal management
    signal.signal(signal.SIGINT, tidyup)
    signal.signal(signal.SIGQUIT, tidyup)
    signal.signal(signal.SIGTERM, tidyup)

    #Init
    init_communication()

    #Main loop
    while True:
        fan_action = FanActions.NONE
        temperature = get_cpu_temp()

        if temperature >= trigger_temp:
            fan_action = FanActions.ON
        elif temperature <= trigger_temp - hysteresis_temp:
            fan_action = FanActions.OFF

        if fan_action != FanActions.NONE:
            set_fan(fan_action)
            logger.info('Temp: {:.2f}°C, Fan action: {}'.format(temperature, fan_action.name))
        elif verbose >= 2:
            logger.debug('Temp: {:.2f}°C'.format(temperature))

        sleep(sleep_seconds)

if __name__ == "__main__":
    main()

#OFF: sudo i2cset -y 1 0x0d 0x08 0x00
#ON:  sudo i2cset -y 1 0x0d 0x08 0x01
