from future.interfaces.IModel import IModel


class UserModel(IModel):
    __connection__ = "default"
    __table__ = "users"

    id: str
    name: str
    email: str
