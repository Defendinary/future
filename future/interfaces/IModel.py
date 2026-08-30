from future.database import Database
from future.interfacing import Interface
from future.logger import log
from future.models.Query import Query
from types import UnionType
from typing import get_args, get_origin, Union
import inflection
import json

# Active-record base (Masonite-style).
# await TradeModel.find("1"), await TradeModel.where(...).get(), await trade.save()


class _IModelType(type):
    def __getattr__(self, attribute, *args, **kwargs):
        instantiated = object.__new__(self)
        return getattr(instantiated, attribute)


class IModel(Interface, metaclass=_IModelType):
    __table__ = None
    __connection__ = "default"

    def __init__(self, **attributes):
        for key, value in attributes.items():
            setattr(self, key, value)

    # _IModelType.__getattr__ turns TradeModel.find into “make an empty instance, then get find from it.”
    # The instance __getattr__ then returns the callable. That lets class-level calls work without @classmethod.
    def __getattr__(self, attribute):
        if attribute == "find":
            async def find(id):
                return await (await self.connection()).find(self, id)
            return find
        if attribute == "all":
            async def all():
                return await (await self.connection()).all(self)
            return all
        if attribute == "where":
            def where(*args):
                return Query(self).where(*args)
            return where
        if attribute == "order_by":
            def order_by(*args):
                return Query(self).order_by(*args)
            return order_by
        if attribute == "transaction":
            async def transaction():
                return await (await self.connection()).transaction()
            return transaction
        if attribute == "eager_load":
            async def eager_load(models, name, related, foreign_key=None, kind="belongs_to"):
                if not models:
                    return models
                if kind == "belongs_to":
                    key = foreign_key or (inflection.underscore(related.__name__) + "_id")
                    ids = list({getattr(model, key, None) for model in models if getattr(model, key, None) is not None})
                    related_map = {}
                    if ids:
                        for row in await related.where("id", "in", ids).get():
                            related_map[getattr(row, "id")] = row
                    for model in models:
                        setattr(model, name, related_map.get(getattr(model, key, None)))
                    return models
                key = foreign_key or (inflection.underscore(models[0].__class__.__name__) + "_id")
                parent_ids = [getattr(model, "id") for model in models if getattr(model, "id", None) is not None]
                children = await related.where(key, "in", parent_ids).get() if parent_ids else []
                grouped = {}
                for child in children:
                    grouped.setdefault(getattr(child, key), []).append(child)
                for model in models:
                    setattr(model, name, grouped.get(getattr(model, "id"), []))
                return models
            return eager_load
        raise AttributeError(attribute)

    def tableize(self):
        return self.__table__ or inflection.tableize(self.__class__.__name__)

    async def connection(self):
        name = self.__connection__
        if name == "default":
            name = Database._default
        connection = Database().get_connection(self.__connection__)
        log.debug("%s using database connection %s (%s)", self.__class__.__name__, name, type(connection).__name__)
        table_exists = getattr(connection, "table_exists", None)
        if table_exists is not None:
            table = self.tableize()
            if not await table_exists(table):
                message = f'Table "{table}" does not exist on connection {name}. Run: future migrate'
                log.warning(message)
                raise RuntimeError(message)
        return connection

    def to_dict(self):
        data = dict(self.__dict__)
        annotations = {}
        for cls in reversed(type(self).__mro__):
            if cls is object:
                continue
            annotations.update(getattr(cls, "__annotations__", {}))
        for name, annotation in annotations.items():
            current = annotation
            origin = get_origin(current)
            args = get_args(current)
            if origin is Union or origin is UnionType or isinstance(current, UnionType):
                non_none = [item for item in args if item is not type(None)]
                current = non_none[0] if non_none else current
            if isinstance(current, type) and issubclass(current, IModel):
                data.pop(name, None)
        return data

    def to_json(self):
        return json.dumps(self.to_dict())

    def openapi_schema(self):
        from datetime import date, datetime
        from typing import get_args, get_origin, Union
        import types
        properties = {}
        required = []
        annotations = {}
        for cls in reversed(type(self).__mro__):
            if cls is object:
                continue
            annotations.update(getattr(cls, "__annotations__", {}))
        for name, annotation in annotations.items():
            if name.startswith("_"):
                continue
            optional = False
            current = annotation
            origin = get_origin(current)
            args = get_args(current)
            if origin is Union or isinstance(current, types.UnionType) or origin is types.UnionType:
                non_none = [item for item in args if item is not type(None)]
                if type(None) in args and len(non_none) == 1:
                    optional = True
                    current = non_none[0]
                    origin = get_origin(current)
                    args = get_args(current)
            if origin is list:
                item = args[0] if args else str
                if isinstance(item, type) and issubclass(item, IModel):
                    item_schema = {"$ref": f"#/components/schemas/{item.__name__}"}
                elif item is int:
                    item_schema = {"type": "integer"}
                elif item is float:
                    item_schema = {"type": "number"}
                elif item is bool:
                    item_schema = {"type": "boolean"}
                elif item in (datetime, date):
                    item_schema = {"type": "string", "format": "date-time" if item is datetime else "date"}
                else:
                    item_schema = {"type": "string"}
                properties[name] = {"type": "array", "items": item_schema}
            elif isinstance(current, type) and issubclass(current, IModel):
                properties[name] = {"$ref": f"#/components/schemas/{current.__name__}"}
            elif current is int:
                properties[name] = {"type": "integer"}
            elif current is float:
                properties[name] = {"type": "number"}
            elif current is bool:
                properties[name] = {"type": "boolean"}
            elif current is datetime:
                properties[name] = {"type": "string", "format": "date-time"}
            elif current is date:
                properties[name] = {"type": "string", "format": "date"}
            elif current is dict:
                properties[name] = {"type": "object"}
            else:
                properties[name] = {"type": "string"}
            if not optional:
                required.append(name)
        schema = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema

    def __repr__(self):
        return str(self.to_dict())

    async def save(self):
        return await (await self.connection()).save(self)

    async def delete(self):
        return await (await self.connection()).delete(self)

    async def update(self, **changes):
        for key, value in changes.items():
            setattr(self, key, value)
        await (await self.connection()).update(self, changes)
        return self

    async def belongs_to(self, related, foreign_key=None):
        key = foreign_key or (inflection.underscore(related.__name__) + "_id")
        related_id = getattr(self, key, None)
        if related_id is None:
            return None
        return await related.find(related_id)

    async def has_many(self, related, foreign_key=None):
        key = foreign_key or (inflection.underscore(self.__class__.__name__) + "_id")
        return await related.where(key, getattr(self, "id")).get()
