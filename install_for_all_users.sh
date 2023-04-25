#!/bin/sh
# Install for all users in `/opt`

# check if terminal supports output colors
if which tput >/dev/null 2>&1 && [ "$(tput -T"$TERM" colors)" -ge 8 ]; then
   fmtBold="\e[1m"
   fmtReset="\e[0m"
fi

# check if running as root
if [ "$(id -u)" != "0" ]; then
    echo "${fmtBold}Error: this script must be run with sudo or as root.${fmtReset}"
    exit 1
fi

# variables
install_dir='/opt/yahboom-raspi-cooling-fan'

# get user for UID 1000, normally 'pi'
user=$(getent passwd 1000 | cut -d: -f1)
user=${user:-pi}
echo "${fmtBold}Installing for user: '$user'.${fmtReset}"

# add user to groups 'i2c' & 'gpio'
usermod -a -G i2c,gpio "$user"
echo "${fmtBold}Added user '$user' to groups 'i2c' & 'gpio'.${fmtReset}"

#install prerequisites
echo "${fmtBold}Installing prerequisites...${fmtReset}"
apt-get update
apt-get install -y m4 libsystemd-dev python3-pip python3-gpiozero
echo "${fmtBold}Prerequisites installed.${fmtReset}"

# create directory in /opt with correct permissions
mkdir -p ${install_dir}
chmod 0775 ${install_dir}
chown "$user": ${install_dir}
echo "${fmtBold}Created directory: '${install_dir}'.${fmtReset}"

# copy files to /opt
cp -t ${install_dir} fan_temp_hysteresis.py yahboom-fan-ctrl.conf
chmod 0775 "${install_dir}/fan_temp_hysteresis.py"
chmod 0664 "${install_dir}/yahboom-fan-ctrl.conf"
chown "$user": "${install_dir}/fan_temp_hysteresis.py" yahboom-fan-ctrl.conf
echo "${fmtBold}Copied files to '${install_dir}'.${fmtReset}"

# create log file
touch "${install_dir}/yahboom-fan-ctrl.log"
chmod 0664 "${install_dir}/yahboom-fan-ctrl.log"
chown "$user": "${install_dir}/yahboom-fan-ctrl.log"
echo "${fmtBold}Created log file: '${install_dir}/yahboom-fan-ctrl.log'.${fmtReset}"

# check if service is active
if systemctl is-active --quiet yahboom-fan-ctrl.service; then
    echo "${fmtBold}Stopping service...${fmtReset}"
    SYSTEMD_LOG_LEVEL=debug systemctl stop yahboom-fan-ctrl.service 2>&1 | grep -E 'Got result|Failed'
fi

# create systemd service from m4 template
m4 -D __INSTALL_DIR__="${install_dir}" -D __USER__="${user}" \
    yahboom-fan-ctrl.service.m4 > /etc/systemd/system/yahboom-fan-ctrl.service
chmod 0644 /etc/systemd/system/yahboom-fan-ctrl.service
chown root:root /etc/systemd/system/yahboom-fan-ctrl.service
echo "${fmtBold}Created systemd service.${fmtReset}"
# reload systemd after creating service
systemctl daemon-reload

# check if service is enabled
if ! systemctl is-enabled --quiet yahboom-fan-ctrl.service; then
    echo "${fmtBold}Enabling service...${fmtReset}"
    SYSTEMD_LOG_LEVEL=debug systemctl enable yahboom-fan-ctrl.service 2>&1 | grep -E 'Got result|Failed'
fi

# start service
echo "${fmtBold}Starting service...${fmtReset}"
SYSTEMD_LOG_LEVEL=debug systemctl start yahboom-fan-ctrl.service 2>&1 | grep -E 'Got result|Failed'

# final message
echo "${fmtBold}Installation complete on '$install_dir'.${fmtReset}"
