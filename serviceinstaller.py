"""
A flexible service installer, currently compatible with Linux Systemd.
"""

# Standard library imports
import collections
import collections.abc
import copy
import configparser
import getpass
import logging
from pathlib import Path
import os
import subprocess
import sys


COMMAND_TIMEOUT = 60


# --- Utility functions ---
def log_setup(verbose=None):
    if verbose is None:
        logging_level = 99
    elif verbose:
        logging_level = "DEBUG"
    else:
        logging_level = "INFO"
    logging.basicConfig(stream=sys.stdout, level=logging_level)


def update_dict_recursive(base, update):
    for update_key, update_value in update.items():
        base_value = base.get(update_key, {})
        if not isinstance(base_value, collections.abc.Mapping):
            base[update_key] = update_value
        elif isinstance(update_value, collections.abc.Mapping):
            base[update_key] = update_dict_recursive(
                base_value, update_value)
        else:
            base[update_key] = update_value
    return base


def get_actual_username():
    try:
        username = os.environ["SUDO_USER"]
        if username:
            return username
    except KeyError:
        pass
    return getpass.getuser()


# --- Module level constants ---
VERSION_INFO = (0, 1, 3)
__version__ = '.'.join((str(version) for version in VERSION_INFO))

PlatformConfig = collections.namedtuple(
    "PlatformConfig",
    ("full_name", "install_path", "configparser_options", "default_contents"))

INSTALL_PATH_SYSTEMD = Path("/etc") / "systemd" / "system"

CONFIGPARSER_OPTIONS_SYSTEMD = {
    "delimiters": ("=", ),
    "comment_prefixes": ("#", ),
    "empty_lines_in_values": False,
    }

DEFAULT_CONTENTS_SYSTEMD = {
    "Unit": {
        "After": "multi-user.target",
        },
    "Service": {
        "Type": "simple",
        "Restart": "on-failure",
        "User": get_actual_username(),
        },
    "Install": {
        "WantedBy": "multi-user.target",
        },
    }

SUPPORTED_PLATFORMS = {
    "linux": PlatformConfig(
        "Linux (systemd)", INSTALL_PATH_SYSTEMD, CONFIGPARSER_OPTIONS_SYSTEMD,
        DEFAULT_CONTENTS_SYSTEMD),
    }


# --- Main functions ---
def get_platform_config(platform=None):
    if platform is None:
        platform = sys.platform
    platform_config = None
    for plat in SUPPORTED_PLATFORMS:
        if platform.startswith(plat):
            platform_config = SUPPORTED_PLATFORMS[plat]
            break
    if platform_config is None:
        raise ValueError(
            "Service installation only currently supported on "
            f"{list(SUPPORTED_PLATFORMS.keys())}, not on {platform}.")
    return platform_config


def generate_systemd_config(config_dict, platform=None):
    platform_config = get_platform_config(platform)
    service_config = configparser.ConfigParser(
        **platform_config.configparser_options)
    # Make configparser case sensitive
    service_config.optionxform = str
    config_dict = update_dict_recursive(
        copy.deepcopy(platform_config.default_contents), config_dict)
    service_config.read_dict(config_dict)
    return service_config


def write_systemd_config(service_config, filename,
                         platform=None, output_path=None):
    platform_config = get_platform_config(platform)
    if output_path is None:
        output_path = platform_config.install_path
    output_path = Path(output_path)
    os.makedirs(output_path.parent, mode=0o755, exist_ok=True)
    with open(output_path / filename, "w",
              encoding="utf-8", newline="\n") as service_file:
        service_config.write(service_file)
    os.chmod(output_path, 0o644)
    os.chown(output_path, 0, 0)  # pylint: disable=no-member
    return output_path


def install_service(service_settings, service_filename,
                    services_enable=None, services_disable=None,
                    platform=None, verbose=None):
    """
    Install a service with the given settings to the given filename.

    Currently only supports Linux Systemd.

    Parameters
    ----------
    service_settings : dict of str: any
        Dictionary, potentially ntested, of the settings for the service.
        Varies by service platform; for systemd, will contain the parameters
        listed in a standard service unit file. Applied on top of the defaults.
    service_filename : str, optional
        What to name the resulting service file (as needed),
        including any extension. The default is None.
    services_enable : list-like, optional
        Services to manually enable along with this one. The default is None.
    services_disable : TYPE, optional
        Services to manually disable along with this one. The default is None.
    platform : str, optional
        Platform to install the service on. Currently, only ``linux`` suported.
        By default, will be detected automatically.
    verbose : bool, optional
        Whether to print verbose log output. By default, prints nothing.

    Returns
    -------
    None.

    """
    log_setup(verbose)
    if services_enable is None:
        services_enable = []
    if services_disable is None:
        services_disable = []

    logging.debug("Installing %s service...", service_filename)
    platform_config = get_platform_config(platform)
    logging.debug("Using platform config settings: %s", platform_config)
    logging.debug("Generating service configuration file...")
    service_config = generate_systemd_config(service_settings, platform)
    logging.debug("Writing service configuration file to %s",
                  platform_config.install_path / service_filename)
    output_path = write_systemd_config(
        service_config, service_filename, platform)

    logging.debug("Reloading systemd daemon...")
    subprocess.run(
        ("systemctl", "daemon-reload"), timeout=COMMAND_TIMEOUT, check=True)

    for service in services_disable:
        logging.debug("Disabling %s (if enabled)...", service)
        subprocess.run(("systemctl", "disable", service),
                       timeout=COMMAND_TIMEOUT, check=False)

    for service in (*services_enable, service_filename):
        logging.debug("Enabling %s...", service)
        subprocess.run(("systemctl", "enable", service),
                       timeout=COMMAND_TIMEOUT, check=True)

    logging.info("Successfully installed %s service to %s",
                 service_filename, output_path)
