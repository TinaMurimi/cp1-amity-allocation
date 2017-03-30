import os
import os.path
import random
import re

from tabulate import tabulate

from person import Person, Staff, Fellow
from room import Room, LivingSpace, Office


class Amity(object):

    office = {}
    space = {}
    room = {}

    staff = {}
    fellow = {}
    person = {}

    allocation = {}

    person_id = 100
    room_id = 1
    allocation_id = 1

    def create_room(self, room_name, room_type, max_no, room_gender=''):
        room_name = room_name.strip().title()
        room_type = room_type.strip().lower()
        room_gender = room_gender.strip().lower()
        occupancy = 0

        found_matches = Amity.search_room(self, Amity.room, room_name)

        if isinstance(found_matches, dict) and len(found_matches.keys()) > 0:
            raise Exception ('Room already exists')
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
        headers = ['Room ID','Room Name', 'Room Type',
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

            found_allocations = [key for key in Amity.allocation.keys() if Amity.allocation[key][1] == dict_key]
            
            for k in found_allocations:
                Amity.allocation.pop(k, None)

            Amity.room.pop(dict_key, None)
            print ('Delete successful')

        else:
            print (found_matches)

    def add_person(self, person_name, person_gender, role, wants_accommodation='N'):

        person_name = person_name.strip().title()
        person_gender = person_gender.strip().lower()
        role = role.strip().lower()
        wants_accommodation = wants_accommodation.strip().lower()

        if role not in ['staff', 'fellow']:
            return ('A person can either have the role STAFF or FELLOW')

        if role == 'staff':
            if wants_accommodation != 'n':
                return ('Staff cannot be allocated living spaces')
            else:
                new_staff = Staff(person_name, person_gender)

                if len(new_staff.pname) > 0:
                    if len(Amity.person.keys()) == 0:
                        Amity.person_id = 100
                    else:
                        Amity.person_id = max(Amity.person.keys()) + 1

                    Amity.staff[Amity.person_id] = [new_staff.pname, new_staff.pgender.upper(
                    ), new_staff.role.title(), new_staff.wants_accommodation.upper()]

                    print ('{0} added successfully with ID {1}'.format(
                        new_staff.pname, Amity.person_id))

        if role == 'fellow':
            new_fellow = Fellow(person_name, person_gender,
                                wants_accommodation)

            if len(new_fellow.pname) > 0:
                if len(Amity.person.keys()) == 0:
                    Amity.person_id = 100
                else:
                    Amity.person_id = max(Amity.person.keys()) + 1

                Amity.fellow[Amity.person_id] = [new_fellow.pname, new_fellow.pgender.upper(
                ), new_fellow.role.title(), new_fellow.wants_accommodation.upper()]

                print ('{0} added successfully with ID {1}'.format(
                    new_fellow.pname, Amity.person_id))

        Amity.person = {**Amity.fellow, **Amity.staff}

        # Allocate Office and Living Space
        Amity.allocate_room(self, Amity.person_id)

        # print (Amity.person)
        # print (Amity.allocation)

    def allocate_room(self, person_id):

        # Allocate office
        if len(Amity.office.keys()) == 0:
            print ('No offices to allocate')
        else:
            # Check for available office then randomly select an office to
            # allocate
            available_office_list = [key for key in Amity.office.keys(
            ) if Amity.office[key][2] > Amity.office[key][4]]
            if len(available_office_list) == 0:
                print ('No offices to allocate')
            else:
                office_to_allocate = random.choice(available_office_list)

                # Create an unique key for each dictionary entry
                if len(Amity.allocation.keys()) == 0:
                    Amity.allocation_id = 1
                else:
                    Amity.allocation_id = max(Amity.allocation.keys()) + 1

                # Add the new allocation to  the allocations dictionary
                Amity.allocation[Amity.allocation_id] = [
                    person_id, office_to_allocate]

                # Update the number of the randomly selected office occupants
                old_occupancy = Amity.office[office_to_allocate][4]
                new_occupancy = old_occupancy + 1
                Amity.office[office_to_allocate][4] = new_occupancy

        # Allocate living space
        wants_accommodation = Amity.person[person_id][3]
        person_gender = Amity.person[person_id][1]

        if len(Amity.space.keys()) == 0:
            print ('No living spaces to allocate')
        else:
            # Check for available living spaces then randomly select an space
            # to allocate
            available_male_spaces = [key for key in Amity.space.keys(
            ) if Amity.space[key][2] > Amity.space[key][4] and Amity.space[key][3] == 'M']
            available_female_spaces = [key for key in Amity.space.keys(
            ) if Amity.space[key][2] > Amity.space[key][4] and Amity.space[key][3] == 'F']

            # Create an unique key for each allocation dictionary entry
            if len(Amity.allocation.keys()) == 0:
                Amity.allocation_id = 1
            else:
                Amity.allocation_id = max(Amity.allocation.keys()) + 1

            # Allocate living space
            if (len(available_male_spaces) != 0 or len(available_female_spaces) != 0) and wants_accommodation == 'Y':
                if person_gender == 'M':
                    if len(available_male_spaces) == 0:
                        print ('No available male living spaces to allocate')
                    else:
                        space_to_allocate = random.choice(
                            available_male_spaces)
                elif person_gender == 'F':
                    if len(available_female_spaces) == 0:
                        print ('No available female living spaces to allocate')
                    else:
                        space_to_allocate = random.choice(
                            available_female_spaces)

                # Add the new allocation to the allocation dictionary
                Amity.allocation[Amity.allocation_id] = [
                    person_id, space_to_allocate]

                # Update the number of the randomly selected living space
                # occupants
                old_occupancy = Amity.space[space_to_allocate][4]
                new_occupancy = old_occupancy + 1
                Amity.space[space_to_allocate][4] = new_occupancy

        Amity.room = {**Amity.office, **Amity.space}

    def reallocate_room(self, person_to_reallocate, room_to_allocate):

        search_person_existence = Amity.search_person(
            self, Amity.person, person_to_reallocate)
        
        if isinstance(search_person_existence, dict) and len(search_person_existence.keys()) > 1:
            return ('There is more than one person with the name {0}. Please view the list of all people and use their ID instead'.format(person_to_reallocate.title()))
        elif isinstance(search_person_existence, dict) and len(search_person_existence.keys()) == 1:
            person_to_reallocate = [key for key in search_person_existence.keys()][0]
        else:
            print (search_person_existence)

        search_room_existence = Amity.search_room( self, Amity.room, room_to_allocate)
        if isinstance(search_room_existence, dict) and len(search_room_existence.keys()) == 1:
            room_to_allocate = [key for key in search_room_existence.keys()][0]

            # Check if the room is avaiable
            available_room_list = [key for key in Amity.room.keys() if Amity.room[key][2] > Amity.room[key][4]]

            if room_to_allocate not in available_room_list:
                raise Exception('The room is not available')
            else:
                person_name = Amity.person[person_to_reallocate][0]
                person_gender = Amity.person[person_to_reallocate][1]
                role = Amity.person[person_to_reallocate][2].lower()
                room_gender = Amity.room[room_to_allocate][3]

                new_room_type = Amity.room[room_to_allocate][1]

                found_allocations = [key for key in Amity.allocation.keys() if Amity.allocation[key][0] == person_to_reallocate]

                if len(found_allocations) == 0:
                    raise Exception ('No allocations available for {0}'.format(person_name))
                elif len(found_allocations) == 1:
                    found_allocations = found_allocations[0]
                    previous_allocated_room = Amity.allocation[found_allocations][1]
                    
                    old_room_name = Amity.room[previous_allocated_room][0]
                    old_room_type = Amity.room[previous_allocated_room][1].lower()
                    old_room_occupancy = Amity.room[previous_allocated_room][4]
                    allocation_to_update = found_allocations

                    if new_room_type != old_room_type:
                        raise Exception ('No {0} allocations available for {1}'.format(new_room_type, person_name))
                else:
                    

                    for i in found_allocations:
                        print (i)
                        previous_allocated_room = Amity.allocation[i][1]

                        old_room_name = Amity.room[previous_allocated_room][0]
                        old_room_type = Amity.room[previous_allocated_room][1].lower()
                        old_room_occupancy = Amity.room[previous_allocated_room][4]
                        allocation_to_update = i
                        if old_room_type == new_room_type:
                            break
                            previous_allocated_room = Amity.allocation[i][1]
                            old_room_name = Amity.room[previous_allocated_room][0]
                            old_room_type = Amity.room[previous_allocated_room][1].lower()
                            old_room_occupancy = Amity.room[previous_allocated_room][4]
                            allocation_to_update = i

                if previous_allocated_room == room_to_allocate:
                    print ('{0} is already allocated to {1}'.format(person_name,old_room_name))
                else:

                    if new_room_type == 'space' and person_gender != room_gender:
                        raise Exception('A person of gender {0} is being allocated to a living space for {1}'.format(
                            person_gender, room_gender))

                    if new_room_type == 'space' and role == 'staff':
                        raise Exception('Staff cannot be allocated living spaces')

                    Amity.allocation[allocation_to_update] = [
                        person_to_reallocate, room_to_allocate]

                    if new_room_type == 'space':
                        Amity.space[previous_allocated_room][4] -= 1
                        Amity.space[room_to_allocate][4] += 1
                    elif new_room_type == 'office':
                        Amity.office[previous_allocated_room][4] -= 1
                        Amity.office[room_to_allocate][4] += 1

        Amity.room = {**Amity.office, **Amity.space}

    def load_people(self, text_file):
        # TO DO: Check input is a file
        if os.path.isfile(text_file):
            with open(text_file, "r") as myfile:
                person_data = myfile.readlines()

            if len(person_data) == 0:
               print ('The file is empty')
            else:
                for d in person_data:
                    data = d.split()
                    # data[0] = data[0] + data[1]
                    data[0] = ' '.join([data[0], data[1]])
                    data.pop(1)

                    person_name = data[0]
                    person_gender = data[1]
                    role = data[2]

                    if len(data) < 4:
                        wants_accommodation = 'N'
                    else:
                        wants_accommodation = data[3]

                    Amity.add_person(self, person_name, person_gender,
                                    role, wants_accommodation)
        else:
            raise FileNotFoundError('File does not exist')

    def search_person(self, people_dict, person_to_search):

        if isinstance(person_to_search, int) or isinstance(person_to_search, str):
            person_to_search = str(person_to_search)

            if person_to_search.isdigit():
                person_to_search = int(person_to_search)

                if person_to_search not in Amity.person:
                    return ("No entry found for person with ID or name {0}".format(person_to_search))
                else:
                    list_of_found_matches = {}
                    list_of_found_matches[person_to_search] = Amity.person[person_to_search]

                    Amity.tabulate_person_output(self, list_of_found_matches)
                    return list_of_found_matches

            else:
                person_to_search = person_to_search.strip().title()

                reg_str = re.compile(
                    r'\b' + re.escape(person_to_search) + r'\b')

                found_matches = [key for key in people_dict.keys() if reg_str.search(people_dict[key][0])]
                if len(found_matches) == 0:
                    return ("No entry found for person with ID or name {0}".format(
                        person_to_search.title()))

                list_of_found_matches = {}

                for key in found_matches:
                    list_of_found_matches[key] = Amity.person[key]

                Amity.tabulate_person_output(self, list_of_found_matches)
                return list_of_found_matches

        else:
            raise TypeError('Ínvalid input')  # to correct

    def tabulate_person_output(self, found_matches):
        headers = ['ID', 'Name', 'Gender', 'Role', 'Needs Accommodation']

        print(tabulate([(k,) + tuple(v) for k, v in found_matches.items()],
                       headers=headers, tablefmt='fancy_grid'))

        # print (tabulate([found_matches[k] for k in sorted(
        # found_matches, key=found_matches.get)], headers=headers,
        # tablefmt='fancy_grid'))

    def change_person_role(self, person_to_change, new_role):

        # To implement:
        # If you change role to staff, unallocate living space where applicable

        new_role = new_role.strip().lower()
        found_matches = Amity.search_person(
            self, Amity.person, person_to_change)

        if new_role not in ['staff', 'fellow']:
            return ('A person can either have the role STAFF or FELLOW')

        if isinstance(found_matches, dict) and len(found_matches.keys()) > 1:
            return ('There is more than one person with the name {0}. Please view the list of all people and use their ID instead'.format(person_to_change.title()))

        elif isinstance(found_matches, dict) and len(found_matches.keys()) == 1:
            dict_key = [key for key in found_matches.keys()][0]

            old_role = Amity.person[dict_key][3]
            pname = Amity.person[dict_key][1]
            old_accommodation = Amity.person[dict_key][4]

            if old_role == new_role.title():
                print ("{0} with ID {1} is aleady a {2}".format(
                    pname, dict_key, old_role))
            else:
                if old_role == 'Fellow' and old_accommodation == 'Y':
                    Amity.person[dict_key][4] = 'N'

                Amity.person[dict_key][3] = new_role.title()
                print ("Role for {0} with ID {1} has been update from {2} to {3} and accommodation requirement updated accordingly".format(
                    pname, dict_key, old_role, Amity.person[dict_key][3]))

        else:
            print (found_matches)

    def delete_person(self, person_to_delete):

        found_matches = Amity.search_person(
            self, Amity.person, person_to_delete)

        if isinstance(found_matches, dict) and len(found_matches.keys()) > 1:
            # Amity.tabulate_room_output(self, found_matches)
            return ('There is more than one person with the name {0}. Please view the list of all people and use their ID instead'.format(
                person_to_delete.title()))

        elif isinstance(found_matches, dict) and len(found_matches.keys()) == 1:
            dict_key = [key for key in found_matches.keys()][0]
            
            found_allocations = [key for key in Amity.allocation.keys() if Amity.allocation[key][0] == dict_key]
            
            for k in found_allocations:
                Amity.allocation.pop(k, None)
            
            Amity.person.pop(dict_key, None)

            print ('Delete successful')

        else:
            print (found_matches)


# a = Amity()

# asmara = a.create_room('Asmara', 'office', 6, '')
# tsavo = a.create_room('Tsavo', 'office', 6, '')
# platform = a.create_room('Platform', 'office', 6, '')


# accra = a.create_room('Accra', 'space', 4, 'F')
# hog = a.create_room('Hog', 'space', 4, 'M')
# malindi = a.create_room('Malindi', 'space', 4, 'M')
# coast = a.create_room('Coast', 'space', 4, 'F')

# jane = a.add_person('Jane', 'F', 'staFF')
# maria = a.add_person('Maria', 'F', 'fellow', 'Y')
# mark = a.add_person('Mark', 'M', 'staFF')
# jose = a.add_person('Jose', 'M', 'fellow')
# joe = a.add_person('Joe', 'M', 'fellow', 'Y')
# janat = a.add_person('Janet', 'F', 'fellow', 'Y')
# luke = a.add_person('Luke', 'M', 'fellow')

# a.load_people('person.txt')

# a.search_person(a.person, 'Jose')

# print ('\n\n***********************')
# print (a.person)
# print (a.room)


# print ('\n***********************')
# print (a.allocation)


# print ('\n\n***********************')
# print (a.room)

# print ('\n\n----------------------')
# # a.reallocate_room(101, 2)
# a.reallocate_room('jose', 3)
# a.delete_person('Jose')
# a.delete_person(101)

# print ('\n***********************')
# print (a.allocation)

# print ('\n\n***********************')
# print (a.room)

