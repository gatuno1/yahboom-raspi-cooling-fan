#!/bin/sh
# Install for all users in `/opt`

# check if running as root
if [ "$(id -u)" != "0" ]; then
    echo "Error: this script must be run with sudo or as root."
    exit 1
fi

# variables
install_dir='/opt/yahboom-raspi-cooling-fan'

# get user for UID 1000, normally 'pi'
user=$(getent passwd 1000 | cut -d: -f1)
user=${user:-pi}
echo "Installing for user: '$user'."

# add user to groups 'i2c' & 'gpio'
usermod -a -G i2c,gpio "$user"
echo "Added user '$user' to groups 'i2c' & 'gpio'."

#install prerequisites
echo "Installing prerequisites..."
apt-get update
apt-get install -y m4 libsystemd-dev python3-pip python3-gpiozero
echo "Prerequisites installed."

# create directory in /opt with correct permissions
mkdir -p ${install_dir}
chmod 0775 ${install_dir}
chown "$user": ${install_dir}
echo "Created directory: '${install_dir}'."

# copy files to /opt
cp -t ${install_dir} fan_temp_hysteresis.py yahboom-fan-ctrl.conf
chmod 0775 "${install_dir}/fan_temp_hysteresis.py"
chmod 0664 "${install_dir}/yahboom-fan-ctrl.conf"
chown "$user": "${install_dir}/fan_temp_hysteresis.py" yahboom-fan-ctrl.conf
echo "Copied files to '${install_dir}'."

# create log file
touch "${install_dir}/yahboom-fan-ctrl.log"
chmod 0664 "${install_dir}/yahboom-fan-ctrl.log"
chown "$user": "${install_dir}/yahboom-fan-ctrl.log"
echo "Created log file: '${install_dir}/yahboom-fan-ctrl.log'."

# check if service is active
if systemctl is-active --quiet yahboom-fan-ctrl.service; then
    echo "Stopping service..."
    SYSTEMD_LOG_LEVEL=debug systemctl stop yahboom-fan-ctrl.service 2>&1 | grep -E -i 'Got result|Failed'
fi

# create systemd service from m4 template
m4 -D __INSTALL_DIR__="${install_dir}" -D __USER__="${user}" \
    yahboom-fan-ctrl.service.m4 > /etc/systemd/system/yahboom-fan-ctrl.service
chmod 0644 /etc/systemd/system/yahboom-fan-ctrl.service
chown root:root /etc/systemd/system/yahboom-fan-ctrl.service

# reload systemd after creating service
systemctl daemon-reload

# check if service is enabled
if ! systemctl is-enabled --quiet yahboom-fan-ctrl.service; then
    echo "Enabling service..."
    SYSTEMD_LOG_LEVEL=debug systemctl enable yahboom-fan-ctrl.service 2>&1 | grep -E -i 'Got result|Failed'
fi

# start service
echo "Starting service..."
SYSTEMD_LOG_LEVEL=debug systemctl start yahboom-fan-ctrl.service 2>&1 | grep -E -i 'Got result|Failed'

# final message
echo "Installation complete."
