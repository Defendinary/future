
APP_ROOT = "app"
APP_DIRS = [
    "config",
    "controllers",
    "middleware"
    "models",
    "plugins"
]

PROJECT_FILES = [
    ".env.example",
    ".gitignore",
    "LICENSE",
    "pyproject.toml",
    "README.md"
]

#PROJECT_STRUCTURE = 

PROJECT_NAME = {
    APP_ROOT: [
        APP_DIRS,
        "routes.py",
    ],
}




README_MD = '''\
# ✨ Future - Broilerplate ✨
Boilerplate example for Future
'''

ENV_EXAMPLE = '''\
# Application settings
APP_NAME=Example
APP_VERSION=1.0
APP_DESCRIPTION=Description
APP_DOMAIN=example.com
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=False
APP_ACCESS_LOG=True
APP_WORKERS=1
APP_KEY=REPLACE_WITH_GENERATED_SECRET_KEY
APP_SSO=False
APP_REGISTRATION=False

# Database settings
DB_DRIVER=sqlite
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=database.sqlite
DB_USERNAME=
DB_PASSWORD=
DB_LOGGING=False
DB_OPTIONS=

# Elasticsearch settings
ELASTIC_HOST=127.0.0.1
ELASTIC_PORT=9200
ELASTIC_USER=
ELASTIC_PASS=
'''

PYPROJECT_TOML = '''\
[tool.poetry]
name = "Future - Boilerplate"
version = "0.0.1"
description = "This is a boilerplate example for Future."
authors = ["nicolaipre"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.12"
python-dotenv = "^1.0.1"
future = {git = "ssh://git@github.com/Defendinary/future.git"}

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"    
'''

LICENSE = '''\
MIT License

Copyright (c) 2025 Defendinary

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

GITIGNORE = '''\
.idea/
.vscode/
.env
.venv
poetry.lock
__pycache__/
'''




APP_ROUTES = '''\
from app.config.environment import APP_DEBUG, APP_DOMAIN, APP_NAME, APP_VERSION, APP_DESCRIPTION, API_SPEC
from app.controllers.ApiController import ExampleController
from future.routing import RouteGroup, Get, Post


ROUTES = [
    RouteGroup(
        name="Example Group",
        #subdomain="",
        #prefix="/",
        middleware=["example"],
        routes=[
            Get("/", ExampleController.example, name="Example Route"),
        ]
    ),
]    
'''



EXAMPLE_PLUGIN = '''\
from future.plugins import Plugin


class ExamplePlugin(Plugin):
    pass    
'''


EXAMPLE_MODEL = '''\
from future.models import Model


class ExampleModel(Model):
    pass
'''


EXAMPLE_MIDDLEWARE = '''\
from future.middleware import Middleware
from future.request import Request
from future.response import Response


class ExampleMiddleware(Middleware):
    name = "example"
    attach_to = "request"
    priority = 0

    def intercept(request: Request):
        return Response(b"OK")
'''


EXAMPLE_CONTROLLER = '''\
from future.controllers import Controller
from future.requests import Request
from future.responses import Response


class ExampleController(Controller):
    async def example(request: Request):
        return Response(body=b"ExampleController", status=200)
'''


CONFIG_DATABASE = '''\
from app.config.environment import DB_DRIVER, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_OPTIONS, DB_DATABASE
from future.database import Database

mysql = Database(
    driver=DB_DRIVER,
    host=DB_HOST,
    port=DB_PORT,
    username=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_DATABASE,
    options=DB_OPTIONS,
)

database = mysql.session()
'''

CONFIG_ENVIRONMENT = '''\
from os import environ as env
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")

# Application settings sourced from .env
APP_NAME            =  str(env.get("APP_NAME", "Future"))
APP_VERSION         =  str(env.get("APP_VERSION", "1.0"))
APP_DESCRIPTION     =  str(env.get("APP_DESCRIPTION", "A short description"))
APP_DEBUG           = eval(env.get("APP_DEBUG", False))
APP_ACCESS_LOG      = eval(env.get("APP_ACCESS_LOG", False))
APP_WORKERS         =  int(env.get("APP_WORKERS", 4))
APP_DOMAIN          =  str(env.get("APP_DOMAIN", "example.com")).replace("http://", "").replace("https://", "")
APP_HOST            =  str(env.get("APP_HOST", "127.0.0.1"))
APP_PORT            =  int(env.get("APP_PORT", 8000))
APP_SSO             = eval(env.get("APP_SSO", False))
APP_KEY             =  str(env.get("APP_KEY", None))
APP_REGISTRATION    = eval(env.get("APP_REGISTRATION", False))
APP_SSL_CERT_FILE   =  str(env.get("APP_SSL_CERT_FILE", "./cert.pem"))
APP_SSL_KEY_FILE    =  str(env.get("APP_SSL_KEY_FILE", "./key.pem"))
APP_SSL_PASSPHRASE  =  str(env.get("APP_SSL_PASSPHRASE", "password"))

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

# API Spec generated based on settings
API_SPEC = {
    "openapi": "1.0.0",
    "info": {
        "title": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
    }
}
'''


CONFIG_MIDDLEWARE = '''\
from app.middleware.ExampleMiddleware import ExampleMiddleware


AVAILABLE_MIDDLEWARES = {
    "example": ExampleMiddleware,
}
'''


RUN_PY = '''\
"""
Runs the application for local development. This file should not be used to start the
application for production.

Refer to https://www.uvicorn.org/deployment/ for production deployments.
"""

"""
#!/usr/bin/env python3
from future.application import Future
from app.config.environment import (
    APP_NAME,
    APP_DEBUG,
    APP_HOST,
    APP_PORT,
    APP_DEBUG,
    APP_DOMAIN,
    APP_ACCESS_LOG,
    APP_WORKERS,
    APP_SSL_CERT_FILE,
    APP_SSL_KEY_FILE,
    APP_SSL_PASSPHRASE
)
from app.routes import ROUTES

app = Future(
    name=APP_NAME,
    domain=APP_DOMAIN,
    debug=APP_DEBUG,
)
app.add_routes(routes=ROUTES)
#print([x.prefix for x in ROUTES])

if __name__ == '__main__':
    app.run(
        host=APP_HOST,
        port=APP_PORT,
        workers=APP_WORKERS
    )

"""
'''






## Boilerplate template

"""
This module provides the default implementation of TemplatesDataProvider, which uses a
JSON file stored in a user's folder.
"""
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import List, Union

from blacksheepcli.templates.domain import Template, TemplatesDataProvider


def _default_templates():
    return {
        "templates": [
            {
                "id": "api",
                "source": "https://github.com/Neoteroi/BlackSheep-API",
                "description": (
                    "Template that can be used to start an API "
                    "with request handlers defined as functions."
                ),
            },
            {
                "id": "mvc",
                "source": "https://github.com/Neoteroi/BlackSheep-MVC",
                "description": (
                    "Template that can be used to start a web app with MVC "
                    "architecture and SSR enabled."
                ),
            },
        ]
    }


class JSONTemplatesDataProvider(TemplatesDataProvider):
    """
    Default data provider for Templates, using a JSON file stored in a user's folder.
    """

    def __init__(self, file_path: Union[str, Path, None] = None) -> None:
        self._file_path = (
            Path(file_path)
            if file_path is not None
            else Path.home()
            / ".neoteroi"
            / os.environ.get("BLACKSHEEPCLI_FOLDER", "blacksheep-cli")
            / "templates.json"
        )
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_default()

    def _ensure_default(self):
        if not self._file_path.exists():
            self._file_path.write_text(
                json.dumps(_default_templates(), indent=4, ensure_ascii=False),
                encoding="utf8",
            )

    def _get_settings(self):
        # NOTE: if a json.JSONDecodeError happens, maybe because the user edited the
        # settings file by hand, let the application crash, so the user can handle
        # the information and no information gets lost.
        try:
            with open(self._file_path, mode="rt", encoding="utf8") as source_file:
                return json.loads(source_file.read())
        except FileNotFoundError:
            return {}

    def _write_settings(self, data):
        with open(self._file_path, mode="wt", encoding="utf8") as source_file:
            return source_file.write(json.dumps(data, indent=4, ensure_ascii=False))

    def add_template(self, template: Template):
        data = self._get_settings()
        templates = data.get("templates", [])
        templates.append(asdict(template))
        data["templates"] = sorted(templates, key=lambda item: item["id"])
        self._write_settings(data)

    def update_template(self, template: Template):
        templates = self.get_templates()
        current = next((value for value in templates if value.id == template.id), None)
        if current:
            current.source = template.source
            current.tag = template.tag
            current.description = template.description
        else:
            current = template
        data = self._get_settings()
        values = [asdict(item) for item in templates]
        data["templates"] = sorted(values, key=lambda item: item["id"])
        self._write_settings(data)

    def remove_template(self, name: str):
        data = self._get_settings()
        templates = data.get("templates", [])
        data["templates"] = [item for item in templates if item["id"] != name]
        self._write_settings(data)

    def get_templates(self) -> List[Template]:
        data = self._get_settings()
        try:
            templates = data["templates"]
        except KeyError:
            return []
        return [
            Template(
                item["id"],
                item["source"],
                item.get("description", ""),
                item.get("tag", ""),
                folder=item.get("folder"),
            )
            for item in sorted(templates, key=lambda item: item["id"])
        ]
