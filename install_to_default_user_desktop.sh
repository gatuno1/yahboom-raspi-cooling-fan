#!/bin/sh
# Install to default user desktop

# get home of default user: UID 1000
user_home=$(getent passwd 1000 | cut -d: -f6)

if ! cd "$user_home/.config/"; then
    echo "Error: cannot cd to '$user_home/.config/' directory"
    exit 1
fi
mkdir "$user_home/.config/autostart"
if ! cd "$user_home/.config/autostart"; then
    echo "Error: cannot cd to newly created '${user_home}/.config/autostart' directory"
    exit 1
fi
contents=$(m4 -D __USER_HOME__="$user_home" start.desktop.m4)
echo "$contents" > "$user_home/.config/autostart/start.desktop"
echo "Install ok to '$user_home'"
