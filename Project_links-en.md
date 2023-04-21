# Links for Hat *Yahboom RGB Cooling Fan*

## Repositories

- Community Opensource repository for Hat: https://github.com/dogweather/yahboom-raspi-cooling-fan

  Code migrated to Python3, which uses `smbus-python` library.

  - [Command reference](https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load) to get system status on Debian at *stackexchange*. Used in script [`oled.py`](oled.py).

- [Yahboom Product Wiki](http://www.yahboom.net/study/RGB_Cooling_HAT): **RGB Cooling HAT** documentation in English.

    Contains C language source code based on `wiringPi` library, which does not compile on full 64-bit Raspberry Pi. It also contains source code in Python2 language based on `smbus-python` library, which is not very stable in my experience.
  - [Instruction Manual](http://www.yahboom.net/xiazai/Raspberry_Pi_RGB_Cooling_HAT/Instruction%20Manual.jpg): Product manual in English.
  - [I2C Protocol Documentation](http://www.yahboom.net/xiazai/Raspberry_Pi_RGB_Cooling_HAT/I2C%20Communication%20Protocol.pdf): I2C protocol documentation in English.

## Similar project to control fan: *Raspberry Pi Fan Control*

- [*Raspberry Pi Fan Control* Blog](https://hobbylad.wordpress.com/2021/07/24/raspberry-pi-cooling-fan-control/)

    Project to control a fan using hysteresis when reaching a limit temperature, but for different hardware that uses a GPIO pin to turn the fan on/off.

    Advantages:
    - Uses `gpiozero` library, both to control GPIO pin, and to read processor temperature, **without having to create each time a new bash thread**.
    - Implementation as a service of `systemd`, so that it runs in the background.
    - Handle linux signals to stop the program, such as `SIGTERM` with *`Ctrl+C`* AND `SIGINT`.

## Python libraries

- [`SMBus2`](https://pypi.org/project/smbus2/): Library for I2C communication that replaces `smbus-python`. It is implemented in Python 2.7-3.x, around calls to `ioctl()` on Linux.
  - [github repository](https://github.com/kplindegaard/smbus2): See file [README.md](https://github.com/kplindegaard/smbus2/blob/master/README.md) for installation.
  - [Pip repository](https://pypi.org/project/smbus2/): Installation with pip.
  - [Documentation](https://smbus2.readthedocs.io/en/latest/): Online documentation.

- [`gpiozero`](https://pypi.org/project/gpiozero/): Library for managing GPIOs on Raspberry Pi.
  - [github repository](https://github.com/gpiozero/gpiozero): See file [README.rst](https://github.com/gpiozero/gpiozero/blob/master/README.rst) for installation.
  - [Pip repository](https://pypi.org/project/gpiozero/): Installation with pip.

- [`Pillow`](https://pypi.org/project/Pillow/): Handling images and fonts
  - [ImageFont Module](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html)
  - [FreeTypeFont class](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont): Handles ttf/freetype fonts.

- [Adafruit SSD1306](https://pypi.org/project/Adafruit-SSD1306/): driver for OLED SSD1306 display.
  - [Adafruit Python github repository for SSD1306](https://github.com/adafruit/Adafruit_Python_SSD1306/): Python language version, although in archived state, works. The maintained version is for CircuitPython.
