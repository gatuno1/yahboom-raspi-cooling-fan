#!/usr/bin/env python3
# Control fan speed of yahboom RGB fan hat, based on CPU temperature.

import smbus2
import signal
import sys
import configparser
import os
from time import sleep
from enum import Enum
import logging
import logging.handlers
from systemd.journal import JournalHandler

# Constants
DEVICE_ADDR = 0x0d
"""i2c device address used by yahboom RBG fan hat."""
FAN_SPEED_REG = 0x08
"""i2c register address to regulate fan speed."""
PRODUCT_CODE = "yahboom-raspi-cooling-hat"
"""Product code of yahboom RGB fan hat."""
MODULE_NAME = "yahboom-fan-ctrl"
"""Module name used for configuration file and log file."""

# Error codes
OK_EXIT = 0
ERR_SYSTEM = 1
ERR_PYTHON_VERSION = 2
ERR_IC2_DEVICE = 3
ERR_TEMPERATURE_FILE = 4
ERR_LOG_FILE = 5

# Configuration global variables
bus_number: int = 1  # raspberry pi with 256MB uses bus_number = 0
"""i2c bus number."""
log_file: str = f"/var/log/{PRODUCT_CODE}/" + MODULE_NAME + ".log"
"""Log file path."""
verbose: int = 1
"""Verbosity level of messages."""
max_log_size: int = 100*1024
"""Maximum size of log file, in bytes."""
max_log_backups: int = 3
"""Maximum number of log file backups."""

hysteresis_temp: float = 10.0
"""Temperature hysteresis to turn off fan, in Celsius."""
trigger_temp: float = 55.0
"""Temperature at which fan is turned on in Celsius."""
max_attempts = 3
"""Maximum number of attempts to write to i2c device."""
sleep_seconds = 2.0
"""Time to sleep between temperature checks, in seconds."""


class FanActions(Enum):
    # Reference for enums: https://docs.python.org/3/howto/enum.html
    """Possible actions for fan."""
    NONE = 0x00
    """No action to be taken."""
    OFF = 0x01
    """Turn fan off."""
    ON = 0x02
    """Turn fan on."""


def signal_name(signum: int) -> str:
    """Get signal name from signal value.

    Args:
        signum (int): signal value

    Returns:
        str: Code name of signal
    """
    # Reference to get name: https://stackoverflow.com/a/35996948/17892898
    # Note: Method signal.Signals(signum) requires python 3.5 or higher.
    try:
        if sys.version_info >= (3, 8):
            return f"{signal.Signals(signum).name} - {signal.strsignal(signal.Signals(signum))}"
        else:
            sig = signal.Signals(signum).name
            return sig.name
    except KeyError:
        return 'SIG_UNKNOWN'
    except ValueError:
        return 'SIG_UNKNOWN'


def read_config():
    """Read configuration from file or command line arguments.
    """
    global bus_number, log_file, verbose, max_log_size, max_log_backups
    global hysteresis_temp, trigger_temp, max_attempts, sleep_seconds
    # Read configuration from file
    config = configparser.ConfigParser()

    # Search for config file in /etc/yahboom-fan-ctrl/ and ./ directories
    config_file_paths = [
        f"/etc/{MODULE_NAME}/{MODULE_NAME}.conf",
        f"./{MODULE_NAME}.conf"]
    for config_file_path in config_file_paths:
        if os.path.exists(config_file_path):
            config.read(config_file_path)
            break

    # Set configuration variables from file or default values
    bus_number = config.getint('DEFAULT', 'bus_number', fallback=bus_number)
    log_file = config.get('DEFAULT', 'log_file', fallback=log_file)
    verbose = config.getint('DEFAULT', 'verbose', fallback=verbose)
    max_log_size = config.getint(
        'DEFAULT', 'max_log_size', fallback=max_log_size)
    max_log_backups = config.getint(
        'DEFAULT', 'max_log_backups', fallback=max_log_backups)

    hysteresis_temp = config.getfloat(
        'FAN-CTRL', 'hysteresis_temp', fallback=hysteresis_temp)
    trigger_temp = config.getfloat(
        'FAN-CTRL', 'trigger_temp', fallback=trigger_temp)
    max_attempts = config.getint(
        'FAN-CTRL', 'max_attempts', fallback=max_attempts)
    sleep_seconds = config.getfloat(
        'FAN-CTRL', 'sleep_seconds', fallback=sleep_seconds)


def setup_logging(verbose_level: int, log_file: str) -> logging.Logger:
    """Setup of Log management, to file and journalctl.

    Args:
        verbose_level (int): verbosity level
        log_file (str): file path to log file

    Returns:
        logging.Logger: logger object
    """
    #
    # Reference: https://docs.python.org/3.9/howto/logging.html
    new_logger = logging.getLogger(MODULE_NAME)
    jh = JournalHandler(SYSLOG_IDENTIFIER=MODULE_NAME)
    jh.setLevel(logging.INFO if verbose_level < 2 else logging.DEBUG)
    new_logger.addHandler(JournalHandler(jh))
    new_logger.setLevel(logging.DEBUG)
    # Reference for multiple handlers: https://docs.python.org/3.9/howto/logging-cookbook.html?highlight=logger#multiple-handlers-and-formatters
    # Reference for log to file: https://stackoverflow.com/questions/6386698/how-to-write-to-a-file-using-the-logging-python-module
    if max_log_size > 256:
        fh = logging.handlers.RotatingFileHandler(
            log_file, encoding='utf-8', maxBytes=max_log_size, backupCount=max_log_backups)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        new_logger.addHandler(fh)
    return new_logger


def assure_log():
    """Check if log file and directory exists, if not create them.
    """
    global log_file, max_log_size, max_log_backups
    # check non empty file name
    if len(log_file) == 0:
        print("Error: log file cannot be empty. Aborting.", file=sys.stderr)
        exit(ERR_LOG_FILE)
    # get path to log file, if not create the directory and file
    try:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    except OSError:
        print(
            f"Error: Cannot create directory for log file '{log_file}'.", file=sys.stderr)
        exit(ERR_LOG_FILE)
    # create log file if not exists, with user permissions
    try:
        with open(log_file, 'a'):
            os.utime(log_file, None)
    except OSError:
        print(f"Error: Cannot create log file '{log_file}'.", file=sys.stderr)
        exit(ERR_LOG_FILE)


def main():
    """Main function of the program.
       If python version is not 3.5 or higher, exit with error code 127.
    """
    # Variables
    temperature: float
    """Current CPU temperature in Celsius."""
    fan_action: FanActions
    """Action to be taken by fan."""
    last_action: FanActions = FanActions.OFF
    """Last action taken by fan."""
    common_logger: logging.Logger
    """Logger object to write to journal and log file."""

    def signal_handler(signal_num: int, frame):
        """Exit the program, after writing to log and turning off fan.

        Args:
            signal_num (int): signal value
            frame (frame object): current stack frame
        """
        common_logger.info(
            f"Caught terminate signal '{signal_name(signal_num)}'. Turn fan off.\n")
        set_fan(FanActions.OFF)
        exit(OK_EXIT)

    def init_communication():
        """Initialize communication with i2c device, also writing to log.
        If communication fails, exit with error code 2.
        """
        common_logger.info(f"Starting {MODULE_NAME} log.")
        try:
            with smbus2.SMBus(bus_number) as i2c:
                i2c.enable_pec(True)  # Enable "Packet Error Checking"
                # Stop fan
                i2c.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, 0x00)
        except Exception as e:
            common_logger.critical(
                f"Cannot open i2c device at bus {bus_number}, address '{hex(DEVICE_ADDR)}'! Aborting.\n", exc_info=True)
            exit(ERR_IC2_DEVICE)
        else:
            common_logger.info(
                f"Connected successfully to i2c device at bus {bus_number}, address '{hex(DEVICE_ADDR)}'.")

        common_logger.info(
            f"Initial Temp: {get_cpu_temp():.2f}°C, trigger temp: >={trigger_temp:.2f}°C, hys. temp: {-hysteresis_temp:.2f}°C.")

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
            common_logger.critical(
                f"Error: Cannot find system temperature file '{CPU_TEMP_FILE}'.", exc_info=True)
            exit(ERR_TEMPERATURE_FILE)
        except PermissionError:
            common_logger.critical(
                f"Error: Permission denied to access temperature file '{CPU_TEMP_FILE}'.", exc_info=True)
            exit(ERR_TEMPERATURE_FILE)
        except:
            common_logger.critical(
                f"Error: Unknown error reading temperature file '{CPU_TEMP_FILE}'.", exc_info=True)
            exit(ERR_TEMPERATURE_FILE)
        return temp

    def set_fan(action: FanActions):
        """Activate/deactivate fan, calling i2c write function.

        Args:
            action (FanActions): Requested action
        """
        success = False
        attempt = 1
        # 0x1 = 100% fan speed, 0x0 = 0% fan speed
        value = 0x01 if action == FanActions.ON else 0x00
        while not success and attempt <= max_attempts:
            try:
                with smbus2.SMBus(bus_number) as bus:
                    bus.enable_pec(True)
                    bus.write_byte_data(DEVICE_ADDR, FAN_SPEED_REG, value)
            except:
                if attempt <= max_attempts:
                    attempt += 1
                    if verbose >= 2:
                        common_logger.exception(
                            f"Write i2c error, attempt {attempt}.", exc_info=True)
                else:
                    common_logger.critical(
                        f"Cannot write to i2c device after {attempt} attempts.", exc_info=True)
                    exit(ERR_IC2_DEVICE)
            else:
                success = True

    # Read configuration from file(s), affecting global configuration variables
    read_config()
    assure_log()

    # Log management
    common_logger = setup_logging(verbose, log_file)

    # Check python version on runtime
    if sys.version_info < (3, 5):
        logger.critical(
            "Python version must be 3.5 or higher to run this program.\n")
        exit(ERR_PYTHON_VERSION)

    # System signal management
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Init
    init_communication()

    # Main loop
    while True:
        fan_action = FanActions.NONE
        temperature = get_cpu_temp()

        if temperature >= trigger_temp:
            fan_action = FanActions.ON
        elif temperature <= trigger_temp - hysteresis_temp:
            fan_action = FanActions.OFF

        if fan_action != FanActions.NONE:
            set_fan(fan_action)
            if fan_action != last_action:
                common_logger.info(
                    f"Temp: {temperature:.2f}°C, Fan action: {fan_action.name}")
                last_action = fan_action
            else:
                common_logger.debug(
                    f"Temp: {temperature:.2f}°C, Fan action: {fan_action.name}")
        elif verbose >= 2:
            common_logger.debug(f"Temp: {temperature:.2f}°C")

        sleep(sleep_seconds)


if __name__ == "__main__":
    main()

# Manual OFF: sudo i2cset -y 1 0x0d 0x08 0x00
# Manual  ON:  sudo i2cset -y 1 0x0d 0x08 0x01
