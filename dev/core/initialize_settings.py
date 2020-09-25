"""
Initializes configuration settings for running application from environment variables or
configuration files.
"""
import os
import yaml
from dataclasses import dataclass


CONFIGURATION_FILE = "../config/server_config.yml"


def _get_secret_from_file(file_path):
    """Fetches value of secret from a file."""
    with open(file_path, "r") as file:
        return file.read().strip()


def _get_secret(identifier):
    """Returns secret from a file."""
    try:
        return _get_secret_from_file(identifier)
    except (FileNotFoundError, OSError):
        return identifier


@dataclass(frozen=True)
class Config:
    """Configuration setting for the application."""

    DEBUG_VALUE: str
    SECRET_KEY_VALUE: str
    ALLOWED_HOSTS_VALUE: str
    MAX_LOGIN_ATTEMPTS_VALUE: str
    CORS_CHECK_VALUE: str
    DATABASE_NAME_VALUE: str
    DATABASE_USER_VALUE: str
    DATABASE_PASSWORD_VALUE: str
    DATABASE_HOSTNAME_VALUE: str
    DATABASE_PORT_VALUE: str
    CORS_ORIGIN_WHITELIST_VALUE: str
    CELERY_BROKER_HOSTNAME_VALUE: str
    CELERY_BROKER_PORT_VALUE: str
    CELERY_BROKER_USERNAME_VALUE: str
    CELERY_BROKER_PASSWORD_VALUE: str


# Get configuration source
if "CORE_CONFIG" in os.environ:
    config_source = os.environ
elif os.path.isfile(CONFIGURATION_FILE):
    with open(CONFIGURATION_FILE, "r") as config_file:
        config_source = yaml.safe_load(config_file)
else:
    raise Exception("No configuration source available.")

config = Config(
    DEBUG_VALUE=config_source["DEBUG"]
    if config_source["APP_ENVIRONMENT"] != "production"
    else "False",
    SECRET_KEY_VALUE=_get_secret(config_source["SECRET_KEY"]),
    ALLOWED_HOSTS_VALUE=config_source["ALLOWED_HOSTS"],
    MAX_LOGIN_ATTEMPTS_VALUE=config_source["MAX_LOGIN_ATTEMPTS"],
    CORS_CHECK_VALUE=config_source["CORS_CHECK"],
    DATABASE_NAME_VALUE=config_source["DATABASE_NAME"],
    DATABASE_USER_VALUE=_get_secret(config_source["DATABASE_USER"]),
    DATABASE_PASSWORD_VALUE=_get_secret(config_source["DATABASE_PASSWORD"]),
    DATABASE_HOSTNAME_VALUE=config_source["DATABASE_HOSTNAME"],
    DATABASE_PORT_VALUE=config_source["DATABASE_PORT"],
    CORS_ORIGIN_WHITELIST_VALUE=config_source["CORS_ORIGIN_WHITELIST"],
    CELERY_BROKER_HOSTNAME_VALUE=config_source["CELERY_BROKER_HOSTNAME"],
    CELERY_BROKER_PORT_VALUE=config_source["CELERY_BROKER_PORT"],
    CELERY_BROKER_USERNAME_VALUE=_get_secret(config_source["CELERY_BROKER_USERNAME"]),
    CELERY_BROKER_PASSWORD_VALUE=_get_secret(config_source["CELERY_BROKER_PASSWORD"]),
)
