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
$ pip install .
```

Note: Script requires Python 3, the above assumes `virtualenvwrapper` has
been configured with Python 3 as default.

## Running

From the root directory, simply call:

```bash
$ workon venv
$ python -m undercontrol.sysmon [--config ...]
```

## Installing as a service
There is a custom command for the setup script, that will install the sysmon
package as a service to run at boot.

In the simplest case, the following will install the script as a user unit
in the user's systemd directory. If it doesn't exist already (which it didn't
on my device), the script will create it and its parents. This behaviour
can be disabled using the `--no-create-install-path` argument to the setup
script.

It's likely you'll want to provide the TOML config file, this is done using
the `--config` parameter. The script will convert relative paths to absolute.

```bash
$ python setup.py systemd_install --config config.toml
```

For full details on the possible arguments, run:

```bash
$ python setup.py --help systemd_install
```

### Creating as a system service
The above requires the user to log into the device, which is not always
preferable. If you'd prefer to run as a system daemon, the procedure is
similar to the above, except you'll need root permissions.

Also, provide the `--system` flag to configure the path defaults for
system services.

Since switching to root removes us from the venv environment, we need to
explicitly call the python binary from the venv (you can find this path
using `which`):

```bash
$ workon undercontrol-sysmon
$ which python
<sysmon_venv_path>/bin/python
$ sudo <sysmon_venv_path>/bin/python setup.py systemd_install --config-file config.toml --system
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

## CORS
If performing a front-end `fetch` on the server, you'll likely need to enable
CORS exceptions through the middleware. This is done by passing a list of
allowable domains to the `--cors-origins` flag. If no origins are provided,
the CORS middleware will not be enabled.