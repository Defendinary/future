"""
Application settings handled using essentials-configuration and Pydantic.

- essentials-configuration is used to read settings from various sources and build the
  configuration root
- Pydantic is used to validate application settings

https://github.com/Neoteroi/essentials-configuration




THE SAME AS CONFIG.py or ENVIRONMENT.py!!!



from os import environ as env
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")  # FIXME: dotenv not used correctly. Shouldn't need both os.environ and dotenv...

# Application settings sourced from .env
APP_NAME            = str(env.get("APP_NAME", "Future"))
APP_VERSION         = str(env.get("APP_VERSION", "1.0"))
APP_DESCRIPTION     =  str(env.get("APP_DESCRIPTION", "A short description"))
APP_DEBUG           = bool(env.get("APP_DEBUG", False))
APP_ACCESS_LOG      = bool(env.get("APP_ACCESS_LOG", False))
APP_WORKERS         =  int(env.get("APP_WORKERS", 4))
APP_HOST            =  str(env.get("APP_HOST", "127.0.0.1"))
APP_PORT            =  int(env.get("APP_PORT", 9000))
APP_SSO             = bool(env.get("APP_SSO", False))
APP_KEY             =  str(env.get("APP_KEY", "secret"))  # os.urandom(24)  # TODO: add to cli --generate
APP_REGISTRATION    = bool(env.get("APP_REGISTRATION", False))
APP_SSL_CERT_FILE   =  str(env.get("APP_SSL_CERT_FILE", "./cert.pem"))
APP_SSL_KEY_FILE    =  str(env.get("APP_SSL_KEY_FILE", "./key.pem"))
APP_SSL_PASSPHRASE  =  str(env.get("APP_SSL_PASSPHRASE", "changeme"))

# Database settings sourced from .env
DB_DRIVER           =  str(env.get("DB_DRIVER", "sqlite"))
DB_HOST             =  str(env.get("DB_HOST", "127.0.0.1"))
DB_PORT             =  int(env.get("DB_PORT", 3306))
DB_DATABASE         =  str(env.get("DB_DATABASE", None))
DB_USERNAME         =  str(env.get("DB_USERNAME", None))
DB_PASSWORD         =  str(env.get("DB_PASSWORD", None))
DB_LOGGING          =  str(env.get("DB_LOGGING", True))
DB_OPTIONS          =  str(env.get("DB_OPTIONS", None))

# Elasticsearch settings sourced from .env
ELASTIC_HOST        =  str(env.get("ELASTIC_HOST", "127.0.0.1"))
ELASTIC_PORT        =  int(env.get("ELASTIC_PORT", 9200))
ELASTIC_USER        =  str(env.get("ELASTIC_USER", None))
ELASTIC_PASS        =  str(env.get("ELASTIC_PASS", None))







https://docs.pydantic.dev/latest/usage/settings/
"""
from blacksheep.server.env import get_env, is_development
from config.common import Configuration, ConfigurationBuilder
from config.env import EnvVars
from config.user import UserSettings
from config.yaml import YAMLFile
from pydantic import BaseModel


class APIInfo(BaseModel):
    title: str
    version: str


class App(BaseModel):
    show_error_details: bool


class Settings(BaseModel):
    app: App
    info: APIInfo



def default_configuration_builder() -> ConfigurationBuilder:
    app_env = get_env()
    builder = ConfigurationBuilder(
        YAMLFile(f"settings.yaml"),
        YAMLFile(f"settings.{app_env.lower()}.yaml", optional=True),
        EnvVars("APP_"),
    )

    if is_development():
        # for development environment, settings stored in the user folder
        builder.add_source(UserSettings())

    return builder


def default_configuration() -> Configuration:
    builder = default_configuration_builder()
    return builder.build()


def load_settings() -> Settings:
    config_root = default_configuration()
    return config_root.bind(Settings)
