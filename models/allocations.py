from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Allocations(Base):
    """
    Attributes:
        - person_id: ID of person
        - room_id: ID of room a person to be allocated
    """

    __tablename__ = 'Allocations'

    person_id = Column('person_id', Integer, ForeignKey('Person.person_id'), primary_key=True)
    room_id = Column('room_id', Integer, ForeignKey('Room.room_id'), primary_key=True)

    def __init__(self, person_id, room_id):
        "Creates an object with the attributes"
        self.person_id = person_id
        self.room_id = room_id