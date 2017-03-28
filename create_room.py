import re

from tabulate import tabulate

from person import Person, Staff, Fellow
from room import Room, LivingSpace, Office


class Amity(object):

    office = {}
    space = {}
    room = {}

    room_id = 1

    # accra = Office('Accra', 6)
    # accra = LivingSpace('Accra', 4, 'M')
    def create_room(self, room_name, room_type, max_no, room_gender=''):
        room_name = room_name.strip().title()
        room_type = room_type.strip().lower()
        room_gender = room_gender.strip().lower()
        occupancy = 0

        found_matches = Amity.search_room(self, Amity.room, room_name)

        if isinstance(found_matches, dict) and len(found_matches.keys()) > 0:
            print ('\n')
            print ('Room already exists')
        else:
            if room_type not in ['office', 'space', 'living space']:
                return ('A room can either be an OFFICE or a LIVING SPACE')

            if room_type == 'office':
                if room_gender != '':
                    return ('An office can be occupied by both male and female')
                else:
                    if max_no > 6:
                        return ("An office can only accommodate a maximum of 6 people")
                    else:
                        new_office = Office(room_name, max_no)

                        if len(new_office.rname) > 0:
                            if len(Amity.room.keys()) == 0:
                                Amity.room_id = 1
                            else:
                                Amity.room_id = max(Amity.room.keys()) + 1

                            Amity.office[Amity.room_id] = [new_office.rname.title(), new_office.rtype.lower(
                            ), new_office.max_no, new_office.rgender.upper(), new_office.occupancy]

                            print ('{0} added successfully with ID {1}'.format(
                                new_office.rname, Amity.room_id))

            if room_type == 'space' or room_type == 'living space':
                if room_gender == '':
                    return ('Please specify if the living space is for male or female')
                else:
                    if max_no > 4:
                        return ("A living space can only accommodate a maximum of 4 people")
                    else:
                        new_space = LivingSpace(room_name, max_no, room_gender)

                        if len(new_space.rname) > 0:
                            if len(Amity.room.keys()) == 0:
                                Amity.room_id = 1
                            else:
                                Amity.room_id = max(Amity.room.keys()) + 1

                            Amity.space[Amity.room_id] = [new_space.rname.title(), new_space.rtype.lower(
                            ), new_space.max_no, new_space.rgender.upper(), new_space.occupancy]

                            print ('{0} added successfully with ID {1}'.format(
                                new_space.rname, Amity.room_id))

        Amity.room = {**Amity.office, **Amity.space}

    def search_room(self, room_dict, room_to_search):

        if isinstance(room_to_search, int) or isinstance(room_to_search, str):
            room_to_search = str(room_to_search)

            if room_to_search.isdigit():
                room_to_search = int(room_to_search)

                if room_to_search not in Amity.room:
                    return ("No entry found for room with ID or name {0}".format(room_to_search))
                else:
                    list_of_found_matches = {}
                    list_of_found_matches[room_to_search] = Amity.room[room_to_search]

                    Amity.tabulate_room_output(self, list_of_found_matches)
                    return list_of_found_matches

            else:
                room_to_search = room_to_search.strip().title()

                reg_str = re.compile(
                    r'\b' + re.escape(room_to_search) + r'\b')

                found_matches = [key for key in room_dict.keys(
                ) if reg_str.search(room_dict[key][0])]
                if len(found_matches) == 0:
                    return ("No entry found for room with ID or name {0}".format(
                        room_to_search.title()))
                else:
                    list_of_found_matches = {}
                    for key in found_matches:
                        list_of_found_matches[key] = Amity.room[key]

                    Amity.tabulate_room_output(self, list_of_found_matches)
                    return list_of_found_matches

        else:
            raise TypeError('Ínvalid input')  # to correct

    def tabulate_room_output(self, found_matches):
        headers = ['Room Name', 'Room Type',
                   'Maximum', 'Room Gender', 'Occupancy']
        print(tabulate([(k,) + tuple(v) for k, v in found_matches.items()],
                       headers=headers, tablefmt='fancy_grid'))
        # print (tabulate([found_matches[k] for k in sorted(
        # found_matches, key=found_matches.get)], headers=headers,
        # tablefmt='fancy_grid'))

    def change_room_type(self, room_to_change, new_type):

        new_type = new_type.strip().lower()
        if new_type not in ['office', 'space', 'living space']:
            return ('A room can either be an OFFICE or a LIVING SPACE')

        found_matches = Amity.search_room(self, Amity.room, room_to_change)

        if isinstance(found_matches, dict) and len(found_matches.keys()) == 1:
            dict_key = [key for key in found_matches.keys()][0]

            old_type = Amity.room[dict_key][1]
            room_name = Amity.room[dict_key][0]
            max_no = Amity.room[dict_key][2]

            if old_type == new_type.lower():
                print ("{0} with ID {1} is aleady a {2}".format(
                    room_name, dict_key, old_type))
            else:
                if old_type == 'office' and max_no > 4:
                    Amity.room[dict_key][2] = 4

                Amity.room[dict_key][1] = new_type.lower()
                print ("Type for {0} with ID {1} has been update from {2} to {3} and maximum occupancy updated accordingly".format(
                    room_name, dict_key, old_type, Amity.room[dict_key][1]))

        else:
            print (found_matches)

    def delete_room(self, room_to_delete):
    
        found_matches = Amity.search_room(
            self, Amity.room, room_to_delete)
        
        if isinstance(found_matches, dict) and len(found_matches.keys()) == 1:
            dict_key = [key for key in found_matches.keys()][0]
            Amity.room.pop(dict_key, None)
            print ('Delete successful')

        else:
            print (found_matches)



a = Amity()

# asmara = a.create_room('Asmara', 'office', 6, '')
accra = a.create_room('Asmara', 'space', 4, 'M')

print(accra)
print(a.space)


# print ('-------------------------')
# print ("List of all rooms created")
# print (a.room)
# print ('-------------------------', '\n\n')

#a.search_room(a.room, 1)
#a.search_room(a.room, 'asmara')
# print ('-------------------------', '\n\n')

# a.change_room_type('asmara', 'living space')
# a.delete_room('asmara')
# print ('-------------------------', '\n\n')
