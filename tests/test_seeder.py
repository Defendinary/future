from future.database import Database
from future.databases.SQLiteDatabase import SQLiteDatabase
from future.interfaces.IModel import IModel
from future.migrations import Blueprint
from future.seeder import SeedRunner


class Widget(IModel):
    __connection__ = "default"
    __table__ = "widgets"
    id: str
    name: str


async def test_seed_runner_runs_named_and_all(tmp_path):
    Database._connections = {}
    Database._default = None
    Database().set_connection_details({"default": "sqlite", "sqlite": SQLiteDatabase(database=":memory:")})
    connection = Database().get_connection("default")
    blueprint = Blueprint("widgets", "default", action="create")
    blueprint.id()
    blueprint.string("name")
    await connection.schema_create(blueprint)
    (tmp_path / "AlphaSeeder.py").write_text(
        "from future.interfaces.IModel import IModel\n"
        "from future.seeder import Seeder\n"
        "\n"
        "\n"
        "class Widget(IModel):\n"
        '    __connection__ = "default"\n'
        '    __table__ = "widgets"\n'
        "\n"
        "\n"
        "class AlphaSeeder(Seeder):\n"
        "    async def run(self):\n"
        '        await Widget(id="a", name="alpha").save()\n'
    )
    (tmp_path / "BetaSeeder.py").write_text(
        "from future.interfaces.IModel import IModel\n"
        "from future.seeder import Seeder\n"
        "\n"
        "\n"
        "class Widget(IModel):\n"
        '    __connection__ = "default"\n'
        '    __table__ = "widgets"\n'
        "\n"
        "\n"
        "class BetaSeeder(Seeder):\n"
        "    async def run(self):\n"
        '        await Widget(id="b", name="beta").save()\n'
    )
    runner = SeedRunner(path=str(tmp_path))
    assert await runner.run(name="AlphaSeeder") == ["AlphaSeeder"]
    assert (await Widget.find("a")).name == "alpha"
    assert await Widget.find("b") is None
    assert await runner.run() == ["AlphaSeeder", "BetaSeeder"]
    assert (await Widget.find("b")).name == "beta"
    await connection.disconnect()
