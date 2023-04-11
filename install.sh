#!/bin/sh

# Correction from https://www.shellcheck.net/wiki/SC2024
echo 'hdmi_force_hotplug=1' | sudo tee -a /boot/config.txt > /dev/null

# Correction from https://www.shellcheck.net/wiki/SC2164
cd /home/pi/.config/ || exit
mkdir /home/pi/.config/autostart
cd /home/pi/.config/autostart || exit
cp /home/pi/RGB_Cooling_HAT/start.desktop /home/pi/.config/autostart/
echo 'install ok!'
