from abc import ABC, ABCMeta, abstractmethod

class Room(ABC):
    """An Amity facility within Andela. A room can either be a(n):
        1. office
        2. living space. We use 'lspace'

    Attributes:
        - rname: A string representing the room's name
        - rType: A string representing if a room is an office or lspace
        - max_no: An integer representing the maximum number of people a room can accommodate
        - rgender: A string M or F representing the gender that can occupy a room. Defaults to '' for offices
        - occupancy: An integer representing the number of people currently occupying the room
    """

    __metaclass__ = ABCMeta

    def __init__(self, rname, rType, max_no, rgender='', occupancy=0):
        self.rname = rname
        self.rType = rType
        self.max_no = max_no
        self.rgender = rgender
        self.occupancy = occupancy

        if self.rType == 'office' and self.max_no > 6:
            raise RuntimeError ("An office can only accommodate a maximum of 6 people")
            self.max_no = 6
        elif self.rType == 'lspace' and self.max_no > 4:
            raise RuntimeError ("A living space can only accommodate a maximum of 4 people")
            self.max_no = 4

        if self.occupancy > self.max_no:
            raise RuntimeError ("{0} has a maximum occupancy of {1}".format(self.rname, self.max_no))
            self.occupancy = 0
            
        if self.rType not in ['office', 'lspace']:
            raise RuntimeError ("A room can only be an office or living space (lspace)")
        
    def change_rType(self, new_rType):
        """Before changing the room type from office to living space, 
            we need to ensure that the maximum possible number of occupants is not more than 4"""

        if new_rType == 'lspace' and self.max_no > 4:
            # try:
            max_no_input = input("Enter the maximum number of occupants (max = 4): ")

            if max_no_input.isdigit():
                max_no_input = int (max_no_input)
                
                if max_no_input > 4:
                    raise RuntimeError ("A living space can only accommodate a maximum of 4 people")
                
                print (max_no_input)
                self.max_no = Room.change_max_no(self,max_no_input)
                
                old_rType = self.rType
                self.rType = new_rType
                return self.rType

            else:
                raise TypeError('Invalid input')

            # except KeyboardInterrupt as err:
            #     print ('Caught KeyboardInterrupt')

    
    def change_max_no(self, new_nax_no):
        """Updates the maximum possible number of occupants"""

        old_max_no = self.max_no
        self.max_no = new_nax_no
        return self.max_no   
    
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
        Room.__init__(self, rname, 'office', max_no, '', occupancy)
        

    def afunction(self):
        pass
    
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
        Room.__init__(self, rname, 'lspace', max_no, rgender, occupancy)
        

    def afunction(self):
        pass

    def room_type(self):
        """"Return a string representing the type of room"""
        return ('lspace')


if __name__ == '__main__':
    
    #asmara = Room('Asmara','office',6, '', 3)    
    # print('\n')
    # print('Room Name:', asmara.rname)
    # print('Room Type:', asmara.rType)
    # print('Room max_no:', asmara.max_no)
    # print('Room rgender:', asmara.rgender)
    # print('Room occupancy:', asmara.occupancy)


    accra = Office('Accra',6)
    #accra = LivingSpace('Accra', 4, 'M')
    #print (accra.rname, accra.rType, accra.max_no, accra.rgender, accra.occupancy)
    print('Room Name:', accra.rname)
    print('Room Type:', accra.rType)
    print('Room max_no:', accra.max_no)
    print('Room rgender:', accra.rgender)
    print('Room occupancy:', accra.occupancy)

    accra.change_rType('lspace')
    print('\n\n\n')
    print('Room Name:', accra.rname)
    print('Room Type:', accra.rType)
    print('Room max_no:', accra.max_no)
    print('Room rgender:', accra.rgender)
    print('Room occupancy:', accra.occupancy)


# #Person, Fellow, Staff, Amity, Room, Office, LivingSpace