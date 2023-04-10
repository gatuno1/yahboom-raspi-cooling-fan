# Vínculos Hat "yahboom raspi cooling fan"

- [Repositorio Opensource para Hat](https://github.com/dogweather/yahboom-raspi-cooling-fan): Código migrado a Python3.
  - [Referencia a comandos](https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load) para obtener estado del sistema en Debian en *stackexchange*. Utilizado en script [`oled.py`](oled.py).

## Librerías Python

- [Pillow](https://pypi.org/project/Pillow/): Manejo de imágenes y fonts
  - [ImageFont Module](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html)
  - [Clase FreeTypeFont](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.FreeTypeFont): Maneja fonts ttf/freetype.

- [ Adafruit SSD1306](https://pypi.org/project/Adafruit-SSD1306/): driver para pantalla OLED SSD1306.
  - [Repositorio github Adafruit en Python para SSD1306](https://github.com/adafruit/Adafruit_Python_SSD1306/): Versión en lenguaje Python, aunque está en estado archivado, funciona. La versión mantenida es para CircuitPython.
