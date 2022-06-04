from pydantic import BaseModel


class Vote(BaseModel):
    username: str
    value: str


class Votes(BaseModel):
    votes: list[Vote] = []
