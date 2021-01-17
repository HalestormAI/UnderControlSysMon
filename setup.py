import sys
from distutils.core import setup
from distutils.cmd import Command
from pathlib import Path


SYSTEM_INSTALL_PATH = "/etc/systemd/system"
USER_INSTALL_PATH = ".config/systemd/user"


class SystemdInstallerCommand(Command):
    description = "Create the systemd config file and install."
    user_options = [
        # The format is (long option, short option, description).
        ('config-file=', None, 'Path to the server TOML config file.'),
        ('install-path=', None,
         'Path to systemd user unit directory [defaults to ~/.config/systemd/user, '
         'or /etc/systemd/system if --system is provided ].'),
        ('no-create-install-path', None,
         "If supplied, the script will error if the install path doesn't exist, "
         "instead of creating it."),
        ('service-name=', None,
         "Name of the service unit file [default: 'undercontrol.sysmon.service']?"),
        ('system', None,
         "If supplied, the script will install to the systemwide systemd path. "
         "Requires root.")]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.config_file = None
        self.install_path = None
        self.no_create_install_path = False
        self.system = False
        self.service_name = "undercontrol.sysmon.service"

    def finalize_options(self):
        """Post-process options."""

        if self.config_file is not None:
            config_path = Path(self.config_file)
            assert config_path.exists(), \
                f"TOML Config file {self.config_file} does not exist."
            self.config_file = config_path.absolute().resolve()

        self.create_install_path = not bool(self.no_create_install_path)
        self.system = bool(self.system)

        if self.install_path is None and self.system:
            self.install_path = Path(SYSTEM_INSTALL_PATH)
        elif self.install_path is None:
            self.install_path = Path.home() / USER_INSTALL_PATH

        if not self.create_install_path:
            assert self.install_path.exists(), \
                f"Install path {self.install_path} does not exist."

        if self.install_path.exists():
            assert self.install_path.is_dir(), \
                f"Install path {self.install_path} exists but is not a directory."

    def run(self):
        """Run command."""
        try:
            import undercontrol.sysmon
        except ImportError:
            raise ImportError(
                "UnderControl SysMon package not installed. Run `pip install .` before creating service.")

        # Read in template
        tpl = open("systemd.undercontrol.sysmon.tpl").read()

        # Replace the template fields
        tpl = tpl.replace("{TPL_WORKING_DIRECTORY}", str(Path.cwd()))

        target = "multi-user.target" if self.system else "default.target"
        tpl = tpl.replace("{TPL_TARGET}", target)

        # Get the current python executable, then add the commands
        exec_str = f"{sys.executable} -m undercontrol.sysmon"

        if self.config_file is not None:
            exec_str += f" --config {self.config_file}"

        tpl = tpl.replace("{TPL_EXEC_START}", exec_str)

        # Write into install path
        install_path = Path(self.install_path)

        if self.create_install_path and not install_path.exists():
            print(f"Creating install directory {str(install_path)}")
            install_path.mkdir(parents=True, exist_ok=False)

        output_path = install_path / self.service_name
        print(f"Installing to {str(output_path)}")
        try:
            with open(output_path, "w") as fh:
                fh.write(tpl)
        except PermissionError:
            raise PermissionError(
                f"Could not write to {self.install_path}. Try running as sudo?")

        sudo_str = 'sudo ' if self.system else ''
        user_flag = '' if self.system else '--user '
        print("Installed unit file. Before running, please enable the service by running:")
        print(
            f"    $ {sudo_str}systemctl {user_flag}enable {self.service_name}")
        print()
        print("You can then manually start the server using:")
        print(f"    $ {sudo_str}systemctl {user_flag}start {self.service_name}")


setup(name='undercontrol-sysmon',
      version='0.0.2',
      author='Ian Hales',
      url='https://github.com/HalestormAI/UnderControlSysMon',
      packages=['undercontrol.sysmon'],
      data_files=["config.example.toml"],
      long_description=open('README.md', 'rt').read(),
      install_requires=[
          "fastapi",
          "uvicorn[standard]",
          "psutil",
          "toml"
      ],
      cmdclass={'systemd_install': SystemdInstallerCommand})
