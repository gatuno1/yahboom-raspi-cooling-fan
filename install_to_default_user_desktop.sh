#!/bin/sh
# Install to default user desktop

# variables
as_user=''
script_path=$(dirname "$(readlink -f "$0")")

# check if terminal supports output colors
if which tput >/dev/null 2>&1 && [ "$(tput -T"$TERM" colors)" -ge 8 ]; then
   fmtBold="\e[1m"
   fmtReset="\e[0m"
   fmtErr="\e[31m"
fi

# get user for UID 1000, normally 'pi'
user=$(getent passwd 1000 | cut -d: -f1)
user=${user:-pi}
echo "${fmtBold}Installing for user: '$user'.${fmtReset}"

# check if running as root or current user is not the default user
if [ "$(id -u)" = "0" ] || [ "$USER" != "$user" ]; then
    as_user="$user"
fi

#install prerequisites
echo "${fmtBold}Installing prerequisites...${fmtReset}"
apt-get update
apt-get install -y m4
echo "${fmtBold}Prerequisites installed.${fmtReset}"

# get home of default user: UID 1000
user_home=$(getent passwd 1000 | cut -d: -f6)

# check if current user is able to create files in default user home
if ! touch "$user_home/test.tmp"; then
    echo "${fmtErr}Error: this script must be run with sudo or as root.${fmtReset}"
    exit 1
else
    rm "$user_home/test.tmp"
fi

# check if home directory exists
if [ ! -d "$user_home" ]; then
    echo "${fmtErr}Error: cannot find home directory '$user_home' for default user '$user'.${fmtReset}"
    exit 1
fi

# check if script path is different from default user home
if [ "$script_path" != "$user_home/RGB_Cooling_HAT" ]; then
    mkdir -p "$user_home/RGB_Cooling_HAT"
    # copy python script to user home
    cp "$script_path/RGB_Cooling_HAT.py" "$user_home/RGB_Cooling_HAT/RGB_Cooling_HAT.py"
    # correct ownership of copied files
    if [ -n "$as_user" ]; then
        chown "$user": \
            "$user_home/RGB_Cooling_HAT" \
            "$user_home/RGB_Cooling_HAT/RGB_Cooling_HAT.py"
    fi
    # make script executable
    chmod +x "$user_home/RGB_Cooling_HAT/RGB_Cooling_HAT.py"
    echo "${fmtBold}Updated '$user_home/RGB_Cooling_HAT'.${fmtReset}"
fi

# create autostart directory
if ! mkdir -p "$user_home/.config/autostart"; then
    echo "${fmtErr}Error: cannot create '${user_home}/.config/autostart' directory.${fmtReset}"
    exit 1
fi
echo "${fmtBold}Created '$user_home/.config/autostart'.${fmtReset}"

# generate desktop file from template
m4 -D __USER_HOME__="$user_home" "$script_path/start.desktop.m4" > "$user_home/.config/autostart/start.desktop"
echo "${fmtBold}Generated '$user_home/.config/autostart/start.desktop'.${fmtReset}"

# generate python script to user home
m4 -D __USER_HOME__="$user_home" "$script_path/start.sh.m4" > "$user_home/RGB_Cooling_HAT/start.sh"
# make script executable
chmod +x "$user_home/RGB_Cooling_HAT/start.sh"
echo "${fmtBold}Generated '$user_home/RGB_Cooling_HAT/start.sh'.${fmtReset}"

# correct ownership of generated files
if [ -n "$as_user" ]; then
    chown "$user": \
        "$user_home/.config/autostart" \
        "$user_home/.config/autostart/start.desktop" \
        "$user_home/RGB_Cooling_HAT/start.sh"
fi

echo "${fmtBold}Installed ok to desktop of '$user_home'.${fmtReset}"
