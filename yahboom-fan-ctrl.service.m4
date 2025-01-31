# Located in /etc/systemd/system/yahboom-fan-ctrl.service

[Unit]
Description=Yahboom Fan control daemon
After=multi-user.target

[Service]
Environment=LANGUAGE="C.UTF-8"
ExecStart=/usr/bin/python3 __INSTALL_DIR__/fan_temp_hysteresis.py
WorkingDirectory=__INSTALL_DIR__
Type=simple
User=__USER__
RestartPreventExitStatus=1 127
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
