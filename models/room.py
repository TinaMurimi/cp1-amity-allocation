from abc import ABC, ABCMeta, abstractmethod


class Room(ABC):
    """ Abstract Base Class
    An Amity facility within Andela. A room can either be a(n):
        1. office
        2. living space. We use 'lspace'

    Attributes:
        - room_name: A string representing the room's name
        - room_type: A string representing if a room is an office or lspace
        - capacity: An integer representing the maximum number of people a room can accommodate
        - room_gender: A string M or F representing the gender that can occupy a room. Defaults to '' for offices
        - occupancy: An integer representing the number of people currently occupying the room
    """

    def __init__(self, room_name):
        self.room_name = room_name
        self.occupancy = 0

    @abstractmethod
    def room_type(self):
        """"Return a string representing the type of room"""
        raise NotImplementedError()


class Office(Room):
    """Office: An Amity facility within Andela

    Constraints:
        - An office can accommodate a maximum of 6 people

    Attributes:
        - room_name: A string representing the office's name
        - capacity: An integer representing the maximum number of people an office can accommodate
        - occupancy: An integer representing the number of people currently occupying the office
    """

    def __init__(self, room_name):
        super(Office, self).__init__(room_name)
        self.room_type = 'office'
        self.capacity = 6
        self.room_gender = 'N'

    def room_type(self):
        """"Return a string representing the type of room"""
        return 'office'


class LivingSpace(Room):
    """LivingSpace: An Amity facility within Andela

    Constraints:
        - A living space can accommodate a maximum of 4 people
        - Staff cannot be allocated living spaces
        - Fellows have a choice to choose a living space or not

    Attributes:
        - room_name: A string representing the living space's name
        - capacity: An integer representing the maximum number of people a living space can accommodate
        - room_gender: A string M or F representing the gender that can occupy a space
        - occupancy: An integer representing the number of people currently occupying the living space
    """

    def __init__(self, room_name, room_gender):
        super(LivingSpace, self).__init__(room_name)
        self.room_gender = room_gender
        self.room_type = 'space'
        self.capacity = 4

    def room_type(self):
        """"Return a string representing the type of room"""
        return 'space'