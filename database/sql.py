from sqlalchemy import create_engine, Integer, Column, String, ForeignKey, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

association_table = Table(
    "rooms_members",
    Base.metadata,
    Column("room_id", ForeignKey("rooms.id")),
    Column("user_id", ForeignKey("users.id"))
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer(), primary_key=True)
    name = Column(String(25), nullable=False, unique=True)
    password = Column(String(25), nullable=False)
    rooms = relationship("Room", secondary=association_table, back_populates='users')

    ownedRooms = relationship("Room", back_populates="owner")
    userVotes = relationship("RoomVotes", back_populates="users")


class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer(), primary_key=True)
    name = Column(String(25), nullable=False, unique=True)
    password = Column(String(25), nullable=False)
    ownerId = Column(Integer, ForeignKey("users.id"))
    users = relationship("User", secondary=association_table, back_populates='rooms')

    owner = relationship("User", back_populates="ownedRooms")
    topic = relationship("RoomTopic", back_populates="room")


class RoomTopic(Base):
    __tablename__ = "room_topics"
    id = Column(Integer(), primary_key=True)
    topic = Column(String(25), nullable=False)
    roomId = Column(Integer, ForeignKey("rooms.id"))
    status = Column(Boolean)

    room = relationship("Room", back_populates="topic")

    votes = relationship("RoomVotes", back_populates="room_topic")

    def __repr__(self):
        return self.topic


class RoomVotes(Base):
    __tablename__ = "rooms_votes"
    id = Column(Integer(), primary_key=True)
    value = Column(String(25), nullable=False)
    topicId = Column(Integer, ForeignKey("room_topics.id"))
    userId = Column(Integer, ForeignKey("users.id"))

    room_topic = relationship("RoomTopic", back_populates="votes")
    users = relationship("User", back_populates="userVotes")
