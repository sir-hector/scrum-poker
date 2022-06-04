from typing import Optional
from pydantic import BaseModel
from database.users_model import User


class Room(BaseModel):
    name: str
    id: int
    owner: str
    users: list[User] = []
