[Unit]
Description=UnderControl System Monitor

[Service]
WorkingDirectory={TPL_WORKING_DIRECTORY}
ExecStart={TPL_EXEC_START}

[Install]
WantedBy=default.target