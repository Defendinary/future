# from sqlalchemy import INTEGER as Integer, Column, ForeignKey, String, Boolean, TIMESTAMP as Timestamp, select, Text
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from dataclasses import dataclass, asdict

# nock recommendation
from pydantic import BaseModel, Field, conint

from typing import Generic, TypeVar
T = TypeVar("T")
# class PaginatedSet(Generic[T])

import msgspec
from enum import Enum
#import enum


class Test(msgspec.struct):
    _id: int
    name: str
    


class Model(DeclarativeBase):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class User(Model):
    __tablename__ = "users"
    name = Column(String)
    email = Column(String)
    password = Column(String)



class Model2:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_dict(self):
        return self.__dict__

class Record(Model2):
    def __init__(self, name, id=None, uuid=None):
        super().__init__(name=name, id=id, uuid=uuid)


# Einar sin recommendation med dataclasses (usage uten decorators)
class A:
    a: str
    b: int

A = dataclass(A)
A = dataclass(A, slots=True)  # bruker mindre minne
A = dataclass(A, kw_only=True)

nico = A(a="aaaa", b="bbbb")
print(nico)
print(asdict(nico))
