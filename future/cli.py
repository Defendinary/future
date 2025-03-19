from json import dumps
from typing import Optional
import questionary
from blacksheepcli.common import click
from blacksheepcli.templates.domain import (Template, TemplateNotFoundError, TemplatesManager)


from blacksheepcli.common import click
from blacksheepcli.create.cli import create_project
from blacksheepcli.templates.cli import templates


import re
from typing import Optional



from typing import Optional

import questionary
from pathvalidate import is_valid_filename

from blacksheepcli.common import click
from blacksheepcli.create.domain import ProjectManager
from blacksheepcli.templates.cli import get_template_by_name, prompt_template

'''




---


# BlackSheep-CLI
🛠️ CLI to start BlackSheep projects.

- Interactive project scaffolding
- Support for configuring more `cookiecutter` project templates

```bash
pip install blacksheep-cli
```

## Official project templates

- `api`, to scaffold Web API projects
- `mvc`, to scaffold Web Apps projects with Model, View, Controller
   architecture, including Server Side Rendering of HTML views (SSR)

## Creating a new project

```bash
blacksheep create
```

## Listing the project templates

```bash
blacksheep templates list
```

With details:

```bash
blacksheep templates details
```

## How to contribute

- clone this repository
- create a Python virtual environment
- install in development mode `pip install -e .`
- add new commands, test
'''



from rich import print
from rich.progress import track
from rich.prompt import Prompt
from rich.console import Console
import time

print("Hello World!")
print("[blue]This is blue text[/blue]")
print("[bold red]This is bold red text[/bold red]")
print("✨ Here's a sparkle emoji")

print("[green]This is green text[/green]")
print("[bold green]This is bold green text[/bold green]")
print("✨ Here's a sparkle emoji")

def show_loading():
    for step in track(range(100), description="Loading..."):
        time.sleep(0.01)



def get_user_input():
    name = Prompt.ask("What's your name")
    color = Prompt.ask("Choose a color", choices=["red", "blue", "green"])
    console = Console()
    console.print(f"Hello [bold {color}]{name}[/bold {color}]!")
    
    
    
    

def print_instructions(destination: str):
    from rich.console import Console

    console = Console()

    console.rule()
    console.print(f"[bold green]🏗️  Project created in {destination}")
    console.rule()
    console.print("-- What's next:")
    console.print(f"\tcd {destination}")

    console.print("\tpip install -r requirements.txt\n\tpython dev.py")


@click.command(name="create")
@click.argument("name", required=False)
@click.option(
    "--destination",
    "-d",
    help=(
        "Destination file path, if not provided, the project "
        "is created in a new folder in CWD."
    ),
    default=None,
    required=False,
)
@click.option(
    "--template",
    "-t",
    help="Project template name.",
    required=False,
)
def create_project(
    name: Optional[str] = None,
    destination: Optional[str] = None,
    template: Optional[str] = None,
):
    """
    Create a new project, with the given NAME, from a template.

    Examples:

        blacksheep create my-proj

        blacksheep create my-proj --template basic
    """
    while not name:
        # unsafe_ask because we let Click handle user cancellation
        name = questionary.text("Project name:", qmark="✨").unsafe_ask()

    if not is_valid_filename(name):
        raise click.ClickException(
            "Invalid name. The provided name must be a valid folder name."
        )

    if destination is None:
        destination = name

    if template:
        template_obj = get_template_by_name(template)
    else:
        template_obj = prompt_template()

    assert destination is not None
    ProjectManager().bootstrap(
        template_obj.source,
        template_obj.tag or None,
        template_obj.folder,
        {"project_name": name},
    )

    print_instructions(destination)


# ---


"""
Imports click or rich_click depending on env settings.
Rich click increases import times and it might be desirable to disable it (e.g. when
running automated jobs).
"""
import os

_disable_rich = os.environ.get("NORICH_CLI", "").lower() in {
    "1",
    "true",
} or os.environ.get("POOR_CLI", "").lower() in {"1", "true"}

if _disable_rich:  # pragma: no cover
    import click
else:
    import rich_click as click

__all__ = ["click"]




# ---




value_pattern = re.compile("^[a-zA-Z_]{1}[0-9a-zA-Z_]+$")


def validate_name(value: Optional[str]):
    if not value:
        raise ValueError("Missing value")
    if not value_pattern.match(value):
        raise ValueError("Invalid value")


class ProjectManager:
    def bootstrap(self, source: str, checkout: Optional[str] = None, folder: Optional[str] = None, data=None):
        from blacksheepcli.common.cookiemod import cookiecutter
        # https://cookiecutter.readthedocs.io/en/stable/advanced/calling_from_python.html
        cookiecutter(source, checkout=checkout, directory=folder, extra_context=data)



from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from click import ClickException


@dataclass
class Template:
    id: str
    source: str
    description: str = ""
    tag: str = ""
    folder: Optional[str] = None

    def __post_init__(self):
        if "$" in self.source:
            tag = self.source.split("$")[-1]
            self.tag = tag
            self.source = self.source[: -(len(tag) + 1)]


class TemplateError(ClickException):
    """Base class for templates errors."""


class TemplateNotFoundError(TemplateError):
    """Exception raised when a template is not found."""

    def __init__(self, name: str) -> None:
        super().__init__(f"The template with name '{name}' could not be found.")


class TemplateConflictError(TemplateError):
    """Exception raised when a template is already configured."""

    def __init__(self, name: str) -> None:
        super().__init__(f"A template with name '{name}' is already configured.")


class TemplatesDataProvider(ABC):
    @abstractmethod
    def add_template(self, template: Template):
        ...

    @abstractmethod
    def update_template(self, template: Template):
        ...

    @abstractmethod
    def remove_template(self, template: str):
        ...

    @abstractmethod
    def get_templates(self) -> List[Template]:
        ...


def _get_default_data_provider() -> TemplatesDataProvider:
    from blacksheepcli.templates.data.default import JSONTemplatesDataProvider

    return JSONTemplatesDataProvider()


class TemplatesManager:
    def __init__(self, provider: Optional[TemplatesDataProvider] = None) -> None:
        self._provider = provider or _get_default_data_provider()

    def add_template(self, name: str, source: str, folder: Optional[str], description: str, force: bool):
        try:
            self.get_template_by_name(name)
        except TemplateNotFoundError:
            self._provider.add_template(Template(name, source, description, folder=folder))
        else:
            if force:
                self._provider.update_template(Template(name, source, description, folder=folder))
            else:
                raise TemplateConflictError(name)

    def remove_template(self, name: str):
        self._provider.remove_template(name)

    def get_template_by_name(self, name: str) -> Template:
        template = next((item for item in self.get_templates() if item.id == name), None)

        if template is None:
            raise TemplateNotFoundError(name)

        return template

    def get_templates(self) -> Iterable[Template]:
        yield from self._provider.get_templates()

    def get_templates_dict(self) -> Dict[str, Template]:
        return {template.id: template for template in self.get_templates()}






"""
Main entry point for the `cookiecutter` command, modified to support prompting the user
with Python https://github.com/tmbo/questionary, to offer a better user experience.
"""
import logging
import os
import sys
from copy import copy

from cookiecutter.config import get_user_config
from cookiecutter.exceptions import InvalidModeException
from cookiecutter.generate import generate_context, generate_files
from cookiecutter.prompt import prompt_for_config
from cookiecutter.replay import dump, load
from cookiecutter.repository import determine_repo_dir
from cookiecutter.utils import rmtree

from blacksheepcli.common.prompts import get_questions

logger = logging.getLogger(__name__)


def cookiecutter(
    template,
    checkout=None,
    no_input=True,
    extra_context=None,
    replay=None,
    overwrite_if_exists=False,
    output_dir=".",
    config_file=None,
    default_config=False,
    password=None,
    directory=None,
    skip_if_file_exists=False,
    accept_hooks=True,
):
    """
    Run Cookiecutter just as if using it from the command line.

    :param template: A directory containing a project template directory,
        or a URL to a git repository.
    :param checkout: The branch, tag or commit ID to checkout after clone.
    :param no_input: Prompt the user at command line for manual configuration?
    :param extra_context: A dictionary of context that overrides default
        and user configuration.
    :param replay: Do not prompt for input, instead read from saved json. If
        ``True`` read from the ``replay_dir``.
        if it exists
    :param output_dir: Where to output the generated project dir into.
    :param config_file: User configuration file path.
    :param default_config: Use default values rather than a config file.
    :param password: The password to use when extracting the repository.
    :param directory: Relative path to a cookiecutter template in a repository.
    :param accept_hooks: Accept pre and post hooks if set to `True`.
    """
    if replay and ((no_input is not False) or (extra_context is not None)):
        err_msg = (
            "You can not use both replay and no_input or extra_context "
            "at the same time."
        )
        raise InvalidModeException(err_msg)

    if extra_context is None:
        extra_context = {}

    config_dict = get_user_config(
        config_file=config_file,
        default_config=default_config,
    )

    repo_dir, cleanup = determine_repo_dir(
        template=template,
        abbreviations=config_dict["abbreviations"],
        clone_to_dir=config_dict["cookiecutters_dir"],
        checkout=checkout,
        no_input=no_input,
        password=password,
        directory=directory,
    )
    import_patch = _patch_import_path_for_repo(repo_dir)

    template_name = os.path.basename(os.path.abspath(repo_dir))

    if replay:
        with import_patch:
            if isinstance(replay, bool):
                context = load(config_dict["replay_dir"], template_name)
            else:
                path, template_name = os.path.split(os.path.splitext(replay)[0])
                context = load(path, template_name)
    else:
        context_file = os.path.join(repo_dir, "cookiecutter.json")
        logger.debug("context_file is %s", context_file)

        questions = get_questions(extra_context, repo_dir)
        if questions:
            from questionary import unsafe_prompt as questionary_prompt

            answers = questionary_prompt(questions)
            extra_context.update(answers)

        context = generate_context(
            context_file=context_file,
            default_context=config_dict["default_context"],
            extra_context=extra_context,
        )

        # prompt the user to manually configure at the command line.
        # except when 'no-input' flag is set
        with import_patch:
            context["cookiecutter"] = prompt_for_config(context, no_input)

        # include template dir or url in the context dict
        context["cookiecutter"]["_template"] = template

        # include output+dir in the context dict
        context["cookiecutter"]["_output_dir"] = os.path.abspath(output_dir)

        dump(config_dict["replay_dir"], template_name, context)

    # Create project from local context and project template.
    with import_patch:
        result = generate_files(
            repo_dir=repo_dir,
            context=context,
            overwrite_if_exists=overwrite_if_exists,
            skip_if_file_exists=skip_if_file_exists,
            output_dir=output_dir,
            accept_hooks=accept_hooks,
        )

    # Cleanup (if required)
    if cleanup:
        rmtree(repo_dir)

    return result


class _patch_import_path_for_repo:
    def __init__(self, repo_dir):
        self._repo_dir = repo_dir
        self._path = None

    def __enter__(self):
        self._path = copy(sys.path)
        sys.path.append(self._repo_dir)

    def __exit__(self, type, value, traceback):
        sys.path = self._path






"""
This module provides support for an alternative way to query the user for input, using
questionary (as it gives better control and a better user experience than cookiecutter's
built-in prompt support).
"""
import json
from pathlib import Path


def _normalize_required(item):
    required = item.get("required")

    if required:
        item["validate"] = lambda x: len(x) > 0
        del item["required"]


def _normalize_when_value(value):
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value


def _normalize_when(item):
    when = item.get("when")

    if when:
        if "==" in when:
            prop, equals_value = when.split("==")
            item["when"] = lambda x: x[prop.strip()] == _normalize_when_value(
                equals_value.strip(" '\"")
            )
        else:
            raise ValueError(f"Unsupported `when` setting: {when}")
    return item


def normalize_questions(extra_context, data):
    for item in data:
        _normalize_required(item)
        _normalize_when(item)

        # if the context already contains the information, skip it
        has_data = item["name"] in extra_context and extra_context[item["name"]]

        if has_data:
            continue

        yield item


def get_questions(context, repo_dir: str):
    questions_file_path = Path(repo_dir) / "questions.json"

    if questions_file_path.exists():
        data = json.loads(questions_file_path.read_text("utf8"))
        return list(normalize_questions(context, data))

    return []









@click.group()
def main():
    """
    🛠️  CLI to start BlackSheep projects.
    """


main.add_command(create_project)
main.add_command(templates)




def pretty(data):
    return dumps(data, ensure_ascii=False, indent=4)


@click.group()
def templates():
    """
    Commands to handle templates.
    """


def _display_source_details(template: Template):
    from rich.text import Text

    text = Text(template.source)

    if template.tag:
        text.append(f"\ntag: {template.tag}", style="yellow")
    if template.folder:
        text.append(f"\nfolder: {template.folder}", style="yellow")
    return text


@click.command(name="details")
def describe_templates():
    """
    Display details about the configured templates.
    """
    from rich.console import Console
    from rich.table import Table

    manager = TemplatesManager()
    templates = manager.get_templates()

    table = Table()
    table.add_column("Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Source", style="magenta")
    table.add_column("Description", justify="left", style="green")

    for template in templates:
        table.add_row(template.id, _display_source_details(template), template.description)

    console = Console()
    console.print(table)


@click.command(name="list")
@click.option("--source", "-s", is_flag=True, help="Include the source in the output.")
def list_templates(source: bool):
    """
    Lists all available templates.
    """
    manager = TemplatesManager()
    templates = manager.get_templates()

    for template in templates:
        if source:
            click.echo(f"{template.id}\t{template.source}")
        else:
            click.echo(f"{template.id}")


@click.command(name="add")
@click.argument("name")
@click.argument("source")
@click.argument("folder", required=False)
@click.option("-d", "--description", default="", show_default=True, help="Template description.")
@click.option("-f", "--force", is_flag=True, help="Force update if the template exists")
def add_template(name: str, source: str, folder: Optional[str], description: str, force: bool):
    """
    Add a template, by name and source, with optional description. If a specific tag
    should be used for a Git repository, it can be specified at the end of the source,
    using an "@" sign. Example: https://github.com/Neoteroi/BlackSheep-Foo$v2

    This command fails if a template exists with the same name. To overwrite an existing
    template, use the -f, or --force flag. Templates can later be used to scaffold new
    projects.

    Examples:

    blacksheep templates add foo https://github.com/Neoteroi/BlackSheep-Foo
        -d 'Some nice template! 🐃'

    blacksheep templates add foo2 'https://github.com/Neoteroi/BlackSheepFoo$v2'
    """
    manager = TemplatesManager()
    manager.add_template(name, source, folder, description, force)


@click.command(name="remove")
@click.argument("name")
def remove_template(name: str):
    """
    Remove a template.
    """
    manager = TemplatesManager()
    manager.remove_template(name)


def prompt_template() -> Template:
    """
    Prompts the user to select one of the available templates.
    """
    manager = TemplatesManager()
    templates = manager.get_templates_dict()

    chosen_name = questionary.select("Project template:", choices=[template.id for template in templates.values()], qmark="🚀").unsafe_ask()

    return templates[chosen_name]


def get_template_by_name(name) -> Template:
    manager = TemplatesManager()
    for template in manager.get_templates():
        if template.id == name:
            return template

    raise TemplateNotFoundError(name)


templates.add_command(list_templates)
templates.add_command(describe_templates)
templates.add_command(add_template)
templates.add_command(remove_template)












#!/usr/bin/env python3
# import os
# import re
# import sys

# from dotenv import load_dotenv
# from prettytable import PrettyTable
# from run import app

# from app.config.middleware import MIDDLEWARE as MIDDLEWARE_ENUM


## Future ideas
# * Look at stuff from [Masonite](https://docs.masoniteproject.com/official-packages/masonite-debugbar)

# https://github.com/python-poetry/cleo


import sys
import os
import shutil
from importlib.resources import files

def initialize_project(destination_folder: str):
    """Initialize a new project by copying boilerplate files."""
    boilerplate_path = files("future").joinpath("boilerplate")
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for item in os.listdir(boilerplate_path):
        src = os.path.join(boilerplate_path, item)
        dst = os.path.join(destination_folder, item)
        
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    print(f"Initialized project in {destination_folder}")

def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: future init <destination-folder>")
        return

    command = sys.argv[1]

    if command == "init":
        if len(sys.argv) != 3:
            print("Usage: future init <destination-folder>")
            return
        destination_folder = sys.argv[2]
        initialize_project(destination_folder)
    else:
        print(f"Unknown command: {command}")



import os
import shutil
from importlib.resources import files

def initialize_project(destination_folder: str):
    boilerplate_path = files("future").joinpath("boilerplate")
    
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for item in os.listdir(boilerplate_path):
        src = os.path.join(boilerplate_path, item)
        dst = os.path.join(destination_folder, item)
        
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    print(f"Initialized project in {destination_folder}")

# Example CLI command
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: future init <destination-folder>")
    else:
        initialize_project(sys.argv[1])



"""
# random shit to fix linting errors temporarily lol
meta = []
MIDDLEWARE_ENUM = {}

# /openapi.json schema
# schema = schema.get_schema(routes=ROUTES)
# print(yaml.dump(schema, default_flow_style=False))


# Pre-check
if len(sys.argv) < 2:
    sys.exit(f"Usage: { sys.argv[1] } <migrate|routes>")


class Star2:
    def __init__(self):
        pass

    # Get inspiration from https://github.com/klen/muffin/ CLI
    # - https://github.com/klen/muffin/blob/6d5aab7e713b0553deae370f518a3f358dc8ddd9/muffin/manage.py#L89

    # Get inspiration from https://github.com/Neoteroi/BlackSheep

    def hello(self):
        print("Hi..!")


class Star:
    def __init__(self):
        load_dotenv(dotenv_path=".env")

    # def middleware(self):

    def migrate(self):
        comment = input("Enter migration comment: ")
        print("--- MIGRATION STATUS ---")
        ret = os.system(f"alembic revision --autogenerate -m { comment }")
        print(ret)
        ret = os.system("alembic upgrade head")
        print(ret)
        print("------------------------")

    def routes(self):
        def middleware_mapper(mw):
            for entry in MIDDLEWARE_ENUM:
                if mw == MIDDLEWARE_ENUM[entry]:
                    return entry

            meta = []
            for name, route_group in app.blueprints.items():
                # print(dir(blueprint))
                # print(dir(route_group.middlewares))

                # DEBUG:
                # pprint(ROUTES[3].app.routes[0].app.__dict__)

                for route in route_group.routes:
                    tmp = {}
                    tmp["domain"] = route_group.host
                    tmp["middleware"] = (
                        f"{middleware_mapper(route_group.middlewares[0])}"
                        if route_group.middlewares
                        else ""
                    )  # route_group.middlewares[0].__qualname__
                    tmp["group"] = name
                    tmp["path"] = "/" + route.path
                    meta.append(tmp)

        def getMeta(route_path):
            # print("GOT", type(route_path), route_path)
            for route in meta:
                if route["path"] == route_path:
                    return route

            t = PrettyTable(
                [
                    "Method",
                    "Path",
                    "Function",
                    "Name",
                    "Domain",
                    "Middleware",
                    "Route Group",
                ]
            )
            t.align = "l"
            # table_data = []

            for route in app.router.routes:
                method = list(route.methods)
                path = "/" + route.path
                func = re.search("\.(\w+)$", route.name).group(
                    1
                )  # FIXME: name gets name of class method. Not the name() set.
                name = ""  # TODO: Fix this

                fml = getMeta(path)
                domain = fml["domain"]
                middleware = fml["middleware"]
                group = fml["group"]

                t.add_row([method, path, func, name, domain, middleware, group])

            print(t)


# Main
if __name__ == "__main__":
    a = Agnostic()

    command = sys.argv[1]
    if command == "routes":
        a.routes()
    elif command == "migrate":
        a.migrate()
"""


# Craft Command

import os
import shutil
from subprocess import call

import zipfile
import tempfile
import requests
from io import BytesIO
from cryptography.fernet import Fernet

from cleo import Application, Command as BaseCommand

from ...future.exceptions import (
    ProjectLimitReached,
    ProjectProviderTimeout,
    ProjectProviderHttpError,
    ProjectTargetNotEmpty,
)


class HasColoredOutput:
    """Add level-colored output print functions to a class."""

    def success(self, message):
        print(f"\033[92m {message} \033[0m")

    def warning(self, message):
        print(f"\033[93m {message} \033[0m")

    def danger(self, message):
        print(f"\033[91m {message} \033[0m")

    def info(self, message):
        return self.success(message)


class AddCommandColors:
    """The default style set used by Cleo is defined here:
    https://github.com/sdispater/clikit/blob/master/src/clikit/formatter/default_style_set.py
    This mixin add method helper to output errors and warnings.
    """

    def error(self, text):
        """
        Write a string as information output.

        :param text: The line to write
        :type text: str
        """
        self.line(text, "error")

    def warning(self, text):
        """
        Write a string as information output.

        :param text: The line to write
        :type text: str
        """
        self.line(text, "c2")


class Command(BaseCommand, AddCommandColors):
    pass


class ProjectCommand(Command):
    """
    Creates a new Masonite project

    start
        {target? : Path of you Masonite project}
        {--b|--branch=False : Specify which branch from the Masonite repo you would like to install}
        {--r|--release=False : Specify which version of Masonite you would like to install}
        {--repo=MasoniteFramework/cookie-cutter : Specify from which repository you want to craft your project}
        {--p|--provider=github : Specify from which repository you want to craft your project github, gitlab }
    """

    providers = ["github", "gitlab"]
    # timeout in seconds for requests made to providers
    TIMEOUT = 20
    BRANCH = 4.0

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.api_base_url = None

    def handle(self):
        target = self.argument("target")

        if not target:
            target = "."

        branch = self.option("branch")
        version = self.option("release")
        repo = self.option("repo")
        provider = self.option("provider")

        if target == ".":
            to_dir = os.path.abspath(os.path.expanduser(target))
        else:
            to_dir = os.path.join(os.getcwd(), target)
        self.check_target_does_not_exist(to_dir)

        try:
            if repo and provider not in self.providers:
                return self.error(
                    "'provider' option must be in {}".format(",".join(self.providers))
                )

            self.set_api_provider_url_for_repo(provider, repo)

            # find cookie-cutter version to use when doing 'craft new' only
            if (
                repo == "MasoniteFramework/cookie-cutter"
                and provider == "github"
                and branch == "False"
                and version == "False"
            ):
                branch = self.BRANCH

            if branch != "False":
                branch_data = self.get_branch_provider_data(provider, branch)
                if "name" not in branch_data:
                    return self.error(f"Branch {branch} does not exist.")

                zipball = self.get_branch_archive_url(provider, repo, branch)
            elif version != "False":
                releases_data = self.get_releases_provider_data(provider)
                zipball = False
                for release in releases_data:
                    if "tag_name" in release and release["tag_name"].startswith(
                        f"v{version}"
                    ):
                        #self.info("Installing version {0}".format(release["tag_name"]))
                        self.line("")
                        zipball = self.get_release_archive_url_from_release_data(
                            provider, release
                        )
                        break
                if zipball is False:
                    return self.error(f"Version {version} could not be found")
            else:
                tags_data = self.get_releases_provider_data(provider)

                # try to find all releases which are not prereleases
                tags = []
                for release in tags_data:
                    if release["prerelease"] is False:
                        tag_key = "tag_name" if provider == "github" else "name"
                        tags.append(release[tag_key].replace("v", ""))

                tags = sorted(
                    tags, key=lambda v: [int(i) for i in v.split(".")], reverse=True
                )
                # get url from latest tagged version
                if not tags:
                    self.comment(
                        "No tags has been found, using latest commit on master."
                    )
                    zipball = self.get_branch_archive_url(provider, repo, "master")
                else:
                    zipball = self.get_tag_archive_url(provider, repo, tags[0])
        except ProjectLimitReached:
            raise ProjectLimitReached(
                f"You have reached your hourly limit of creating new projects with {provider}. Try again in 1 hour."
            )
        except requests.Timeout:
            raise ProjectProviderTimeout(
                f"{provider} provider is not reachable, request timed out after {self.TIMEOUT} seconds"
            )
        except Exception as e:
            self.error(
                "The following error happened when crafting your project. Verify options are correct else open an issue at https://github.com/MasoniteFramework/masonite."
            )
            raise e

        success = False

        zipurl = zipball

        self.info("Crafting Application ...")

        # create a tmp directory to extract project template
        tmp_dir = tempfile.TemporaryDirectory()
        try:
            request = requests.get(zipurl)
            with zipfile.ZipFile(BytesIO(request.content)) as zfile:
                zfile.extractall(tmp_dir.name)
                extracted_path = os.path.join(
                    tmp_dir.name, zfile.infolist()[0].filename
                )
            success = True
        except Exception as e:
            self.error(f"An error occured when downloading {zipurl}")
            raise e

        if success:
            if target == ".":
                shutil.move(extracted_path, os.getcwd())
            else:
                shutil.move(extracted_path, to_dir)

            # remove tmp directory
            tmp_dir.cleanup()

            if target == ".":
                from_dir = os.path.join(os.getcwd(), zfile.infolist()[0].filename)

                for file in os.listdir(zfile.infolist()[0].filename):
                    shutil.move(os.path.join(from_dir, file), os.getcwd())
                os.rmdir(from_dir)

            self.info("Application Created Successfully!")
            if target == ".":
                self.info("Installing Dependencies...")
                self.call("install")
                self.info(
                    "Installed Successfully. Just Run `python craft serve` To Start Your Application."
                )
            else:
                self.info(
                    f"You now will have to go into your new {target} directory and run `project install` to complete the installation"
                )

            return

        else:
            self.comment("Could Not Create Application :(")

    def check_target_does_not_exist(self, target):
        """To avoid overwriting target directory and to avoid raw errors
        check that target directory does not exist."""
        if target == os.getcwd():
            return False

        if os.path.isdir(target):
            raise ProjectTargetNotEmpty(
                f"{target} already exists. You must craft a project in a new directory."
            )

    def set_api_provider_url_for_repo(self, provider, repo):
        if provider == "github":
            self.api_base_url = f"https://api.github.com/repos/{repo}"
        elif provider == "gitlab":
            import urllib.parse

            repo_encoded_url = urllib.parse.quote(repo, safe="")
            self.api_base_url = f"https://gitlab.com/api/v4/projects/{repo_encoded_url}"

    def get_branch_provider_data(self, provider, branch):
        if provider == "github":
            branch_data = self._get(f"{self.api_base_url}/branches/{branch}")
        elif provider == "gitlab":
            branch_data = self._get(f"{self.api_base_url}/repository/branches/{branch}")
        return branch_data.json()

    def get_branch_archive_url(self, provider, repo, branch):
        if provider == "github":
            return f"https://github.com/{repo}/archive/{branch}.zip"
        elif provider == "gitlab":
            # here we can provide commit, branch name or tag
            return f"{self.api_base_url}/repository/archive.zip?sha={branch}"

    def get_tag_archive_url(self, provider, repo, version):
        if provider == "github":
            tag_data = self._get(f"{self.api_base_url}/releases/tags/v{version}")
            return tag_data.json()["zipball_url"]
        elif provider == "gitlab":
            return self.get_branch_archive_url("gitlab", repo, "v" + version)

    def get_releases_provider_data(self, provider):
        if provider == "github":
            releases_data = self._get(f"{self.api_base_url}/releases")
        elif provider == "gitlab":
            releases_data = self._get(f"{self.api_base_url}/releases")
        return releases_data.json()

    def get_release_archive_url_from_release_data(self, provider, release):
        if provider == "github":
            return release["zipball_url"]
        elif provider == "gitlab":
            return [x for x in release["assets"]["sources"] if x["format"] == "zip"][0][
                "url"
            ]
            # could also do
            # return "{0}/repository/archive.zip?sha={1}.zip".format(self.api_base_url, branch)

    def get_tags_provider_data(self, provider):
        if provider == "github":
            releases_data = self._get(f"{self.api_base_url}/releases")
        elif provider == "gitlab":
            releases_data = self._get(f"{self.api_base_url}/repository/tags")
        return releases_data.json()

    def _get(self, request):
        data = requests.get(request, timeout=self.TIMEOUT)
        if data.status_code != 200:
            if data.reason == "rate limit exceeded":
                raise ProjectLimitReached()
            else:
                raise ProjectProviderHttpError(
                    f"{data.reason}({data.status_code}) at {data.url}"
                )
        return data


class KeyCommand(Command):
    """
    Generate a new key.

    key
        {--s|--store : Stores the key in the .env file}
        {--d|--dont-store : Does not store the key in the .env file}
    """

    def handle(self):
        key = bytes(Fernet.generate_key()).decode("utf-8")

        if self.option("dont-store"):
            return self.info(f"Key: {key}")

        with open(".env") as file:
            data = file.readlines()

        for line_number, line in enumerate(data):
            if line.startswith("APP_KEY="):
                data[line_number] = f"APP_KEY={key}\n"
                break

        with open(".env", "w") as file:
            file.writelines(data)

        self.info(f"Key added to your .env file: {key}")


class InstallCommand(Command):
    """
    Installs all of Masonite's dependencies

    install
        {--no-key : If set, craft install command will not generate and store a new key}
        {--no-dev : If set, Masonite will install without dev dependencies}
        {--f|--force : Overwrite .env if exists}
    """

    def handle(self):
        if not os.path.isfile(".env") or self.option("force"):
            shutil.copy(".env-example", ".env")

        if os.path.isfile("Pipfile"):
            try:
                if not self.option("no-dev"):
                    call(["pipenv", "install", "--dev"])
                else:
                    call(["pipenv", "install"])

                if not self.option("no-key"):
                    call(["pipenv", "shell", "new", "key", "--store"])

                return
            except Exception:
                self.comment(
                    """Pipenv could not install from your Pipfile .. reverting to pip installing requirements.txt"""
                )
                call(["python", "-m", "pip", "install", "-r", "requirements.txt"])
        elif os.path.isfile("requirements.txt"):
            call(["python", "-m", "pip", "install", "-r", "requirements.txt"])
        else:
            raise OSError("Could not find a Pipfile or a requirements.txt file")
        if not self.option("no-key"):
            try:
                self.call("key", "--store")
            except Exception:
                self.error(
                    "Could not successfully install Masonite. This could happen for several reasons but likely because of how Masonite is installed on your system and you could be hitting permission issues when Masonite is fetching required modules."
                    " If you have correctly followed the installation instructions then you should try everything again but start inside an virtual environment first to avoid any permission issues. If that does not work then seek help in"
                    " the Masonite Slack channel. Links can be found on GitHub in the main Masonite repo."
                )


__version__ = "0.2.0"
application = Application("Star-CLI", __version__)
application.add(ProjectCommand())
application.add(KeyCommand())
application.add(InstallCommand())

if __name__ == "__main__":
    application.run()
