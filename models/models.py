from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Employees(Base):
    """
    Attributes:
        - person_id
        - person_name
        - person_gender
        - role
    """

    __tablename__ = 'Employees'

    person_id = Column(Integer, primary_key=True)
    person_name = Column(String(20), nullable=False)
    person_gender = Column(String(1), nullable=False)
    role = Column(String(6), nullable=False)
    wants_accommodation = Column(String(1), nullable=False)


class Rooms(Base):
    """"
    Table: Rooms
    Attributes:
        - room_id
        - room_name
        - room_type
        - capacity
        - room_gender
        - occupancy
    """

    __tablename__ = 'Rooms'

    room_id = Column(Integer, primary_key=True)
    room_name = Column(String(15), nullable=False)
    room_type = Column(String(6), nullable=False)
    capacity = Column(Integer, nullable=False)
    room_gender = Column(String(1), nullable=False)
    occupancy = Column(Integer, nullable=False)


class Allocations(Base):
    """
    Table: Allocations

    Attributes:
        - person_id: Foreign key, Employees.person_id
        - room_id: Foreign key, Rooms.room_id
    """

    __tablename__ = 'Allocations'

    person_id = Column('person_id', Integer, ForeignKey(
        'Employees.person_id'), primary_key=True)
    room_id = Column('room_id', Integer, ForeignKey(
        'Rooms.room_id'), primary_key=True)
