# UnderControl: System Monitor Service

A small microservice that will sit on a server and report stats over REST as
requested.

Currently only has a single endpoint, which will return all stats.

Tested with Python 3.7 on a Raspberry Pi 4, Model B.

## Basic Setup

Nothing unusual here, create your virtual environment and install the
requirements. Assuming you're using `virtualenvwrapper`:

```bash
$ mkvirtualenv venv
$ pip install -r requirements.txt
```

Note: Script requires Python 3, the above assumes `virtualenvwrapper` has
been configured with Python 3 as default.

## Running

From the root directory, simply call:

```bash
$ workon venv
$ python -m sysmon [--config ...]
```

## Configuration
Can be configured using a TOML config file, which should be provided using the
`--config` command line argument. Values supplied in the config file will
override the argument defaults. These arguments can also be provided on the
command line.

For clarity, argument precedence from highest to lowest is [`>` indicates"will
override"]:

```
command_line_args > config_file_args > app_defaults
```

An example toml file is provided.

Arguments should be specified using their underscore delimited versions, for
example, if you would like to supply the `--per-cpu` argument in the config,
add the following to your `config.toml`:

```toml
per_cpu = true
```