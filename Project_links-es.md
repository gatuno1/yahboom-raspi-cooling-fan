# Vínculos para Hat *Yahboom RGB Cooling Fan*

## Repositorios

- Repositorio Community Opensource para Hat: https://github.com/dogweather/yahboom-raspi-cooling-fan

  Código migrado a Python3, que utiliza librería `smbus-python`.

  - [Referencia a comandos](https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load) para obtener estado del sistema en Debian en *stackexchange*. Utilizado en script [`oled.py`](oled.py).

- [Wiki del producto en Yahboom](http://www.yahboom.net/study/RGB_Cooling_HAT): Documentación del hat **RGB Cooling HAT** en inglés.

    Contiene código fuente en lenguaje C basado en librería `wiringPi`, que no compila en Raspberry Pi 64-bits full. También contiene código fuente en lenguaje Python2 basado en librería `smbus-python`, que no es muy estable en mi experiencia.
  - [Manual de instrucciones](http://www.yahboom.net/xiazai/Raspberry_Pi_RGB_Cooling_HAT/Instruction%20Manual.jpg): Manual del producto en inglés.
  - [Documentación de protocolo I2C](http://www.yahboom.net/xiazai/Raspberry_Pi_RGB_Cooling_HAT/I2C%20Communication%20Protocol.pdf): Documentación del protocolo I2C en inglés.

## Proyecto parecido para controlar ventilador: *Raspberry Pi Fan Control*

- [Blog de *Raspberry Pi Fan Control*](https://hobbylad.wordpress.com/2021/07/24/raspberry-pi-cooling-fan-control/)

    Proyecto para controlar un ventilador utilizando histéresis al alcanzar una temperatura límite, pero para hardaware diferente que utiliza un pin GPIO para prender/apagar el ventilador.

    Ventajas:
    - Utiliza librería `gpiozero`, tanto para controlar pin GPIO, como para leer la temperatura del procesador, **sin tener que crear cada vez un nuevo subproceso bash**.
    - Implementación como un servicio de `systemd`, para que se ejecute en segundo plano.
    - Maneja señales linux para detener el programa, como `SIGTERM` con *`Ctrl+C`* Y `SIGINT`.

## Librerías Python

- [`SMBus2`](https://pypi.org/project/smbus2/): Librería para comunicación I2C que reemplaza a `smbus-python`. Está implementada en Python 2.7-3.x, en torno a llamadas a `ioctl()` en Linux.
  - [Repositorio github](https://github.com/kplindegaard/smbus2): Ver archivo [README.md](https://github.com/kplindegaard/smbus2/blob/master/README.md) para instalación.
  - [Repositorio pip](https://pypi.org/project/smbus2/): Instalación con pip.
  - [Documentación](https://smbus2.readthedocs.io/en/latest/): Documentación en línea.

- [`gpiozero`](https://pypi.org/project/gpiozero/): Librería para manejo de GPIOs en Raspberry Pi.
  - [Repositorio github](https://github.com/gpiozero/gpiozero): Ver archivo [README.rst](https://github.com/gpiozero/gpiozero/blob/master/README.rst) para instalación.
  - [Repositorio pip](https://pypi.org/project/gpiozero/): Instalación con pip.

- [`Pillow`](https://pypi.org/project/Pillow/): Manejo de imágenes y fonts
  - [ImageFont Module](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html)
  - [Clase FreeTypeFont](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont): Maneja fonts ttf/freetype.

- [Adafruit SSD1306](https://pypi.org/project/Adafruit-SSD1306/): driver para pantalla OLED SSD1306.
  - [Repositorio github Adafruit en Python para SSD1306](https://github.com/adafruit/Adafruit_Python_SSD1306/): Versión en lenguaje Python, aunque está en estado archivado, funciona. La versión mantenida es para CircuitPython.
