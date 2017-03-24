import gc

from abc import ABC, ABCMeta, abstractmethod


class Room(ABC):
    """An Amity facility within Andela. A room can either be a(n):
        1. office
        2. living space. We use 'lspace'

    Attributes:
        - rname: A string representing the room's name
        - rtype: A string representing if a room is an office or lspace
        - max_no: An integer representing the maximum number of people a room can accommodate
        - rgender: A string M or F representing the gender that can occupy a room. Defaults to '' for offices
        - occupancy: An integer representing the number of people currently occupying the room
    """

    def __init__(self, rname, rtype, max_no, rgender='', occupancy=0):
        self.rname = rname
        self.rtype = rtype
        self.max_no = max_no
        self.rgender = rgender
        self.occupancy = occupancy

    @abstractmethod
    def room_type(self):
        """"Return a string representing the type of room"""
        raise NotImplementedError()


class Office(Room):
    """Office: An Amity facility within Andela

    Constraints:
        - An office can accommodate a maximum of 6 people

    Attributes:
        - rname: A string representing the office's name
        - max_no: An integer representing the maximum number of people an office can accommodate
        - occupancy: An integer representing the number of people currently occupying the office
    """

    def __init__(self, rname, max_no=6, occupancy=0):
        super(Office, self).__init__(rname, 'office', max_no, '', occupancy)

    def room_type(self):
        """"Return a string representing the type of room"""
        return ('office')

class LivingSpace(Room):
    """LivingSpace: An Amity facility within Andela

    Constraints:
        - A living space can accommodate a maximum of 4 people
        - Staff cannot be allocated living spaces
        - Fellows have a choice to choose a living space or not

    Attributes:
        - rname: A string representing the living space's name
        - max_no: An integer representing the maximum number of people a living space can accommodate
        - rgender: A string M or F representing the gender that can occupy a space
        - occupancy: An integer representing the number of people currently occupying the living space
    """

    def __init__(self, rname, max_no, rgender, occupancy=0):
        super(LivingSpace, self).__init__(rname, 'space', max_no, rgender, occupancy)

    def room_type(self):
        """Return a string representing the type of room"""
        return ('lspace')


# if __name__ == '__main__':
    # asmara = Room('Asmara', 'office', 6, '', 3)
    # print('\n')
    # print('Room Name:', asmara.rname)
    # print('Room Type:', asmara.rtype)
    # print('Room max_no:', asmara.max_no)
    # print('Room rgender:', asmara.rgender)
    # print('Room occupancy:', asmara.occupancy)

    # accra = Office('Accra', 6)
    # accra = LivingSpace('Accra', 4, 'M')
    # print('Room Name:', accra.rname)

    # tsavo = LivingSpace('Tsavo', 4, 'M')
    # print (tsavo.rname)

    # local()
    # print (accra.rname, accra.rtype, accra.max_no, accra.rgender, accra.occupancy)
    # print('Room Name:', accra.rname)
    # print('Room Type:', accra.rtype)
    # print('Room max_no:', accra.max_no)
    # print('Room rgender:', accra.rgender)
    # print('Room occupancy:', accra.occupancy)

    # accra.change_rtype('lspace')
    # print('\n\n\n')
    # print('Room Name:', accra.rname)
    # print('Room Type:', accra.rtype)
    # print('Room max_no:', accra.max_no)
    # print('Room rgender:', accra.rgender)
    # print('Room occupancy:', accra.occupancy)


# #Person, Fellow, Staff, Amity, Room, Office, LivingSpace
