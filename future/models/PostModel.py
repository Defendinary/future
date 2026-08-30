from future.interfaces.IModel import IModel
from future.models.UserModel import UserModel


class PostModel(IModel):
    __connection__ = "default"
    __table__ = "posts"

    id: str
    title: str
    content: str
    author_id: str
    author: UserModel | None = None
