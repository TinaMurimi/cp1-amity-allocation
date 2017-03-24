from person import *
from room import *

class amity:

    def create_room(self):
        if self.rType == 'office' and self.max_no > 6:
            raise RuntimeError(
                "An office can only accommodate a maximum of 6 people")
            self.max_no = 6

        elif self.rType == 'lspace' and self.max_no > 4:
            raise RuntimeError(
                "A living space can only accommodate a maximum of 4 people")
            self.max_no = 4

        if self.occupancy > self.max_no:
            raise RuntimeError(
                "{0} has a maximum occupancy of {1}".format(self.rname, self.max_no))
            self.occupancy = 0

        if self.rType not in ['office', 'lspace']:
            raise RuntimeError(
                "A room can only be an office or living space (lspace)")

    def change_room_type(self, new_rType):
        """Before changing the room type from office to living space, 
            we need to ensure that the maximum possible number of occupants is not more than 4"""

        if new_rType == 'lspace' and self.max_no > 4:
            # try:
            max_no_input = input(
                "Enter the maximum number of occupants (max = 4): ")

            if max_no_input.isdigit():
                max_no_input = int(max_no_input)

                if max_no_input > 4:
                    raise RuntimeError(
                        "A living space can only accommodate a maximum of 4 people")

                print (max_no_input)
                self.max_no = Room.change_max_no(self, max_no_input)

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



#####################
# Person Functions go here


        if self.pType not in ['staff', 'fellow']:
             raise RuntimeError ("A person can only be a fellow or staff")

    def change_pType(self, new_pType):
        """Returns the new employee type a person is"""

        old_rType = self.pType
        self.pType = new_pType
        return (self.pType)