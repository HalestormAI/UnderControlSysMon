# UnderControl: System Monitor Service

A small microservice that will sit on a server and report stats over REST as requested.

Currently only has a single endpoint, which will return all stats.

Can be configured using a TOML config file, which should be provided using the `--config` command line argument. Values supplied in
the config file will override the argument defaults. These arguments can also be provided on the command line.

For clarity, argument precedence from highest to lowest is [`>` indicates "will override"]:

    command_line_args > config_file_args > app_defaults