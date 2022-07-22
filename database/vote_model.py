from pydantic import BaseModel


class Vote(BaseModel):
    username: str
    value: int


class Votes(BaseModel):
    votes: list[Vote] = []
