import collections
import json
import os
import os.path
import psycopg2
import psycopg2.extras
import random
import re
import sys


from prettytable import PrettyTable
from tabulate import tabulate

from models.config import config
from models.person import Person, Staff, Fellow
from models.room import Room, LivingSpace, Office


class Amity(object):

    office = {}
    space = {}
    room = {}

    staff = {}
    fellow = {}
    person = {}

    allocation = {}

    allocation_id = 1

    conn = None
    try:
        conn = psycopg2.connect(database='cp1_amity')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # To avoid duplicate primary keys from being added
        sql_query = ("""SELECT MAX(room_id) FROM room""")
        cur.execute(sql_query)
        row = cur.fetchall()[0][0]

        if row is not None:
            room_id = row + 1
        else:
            room_id = 1

        sql_query = ("""SELECT MAX(person_id) FROM person""")
        cur.execute(sql_query)
        row = cur.fetchall()[0][0]

        if row is not None:
            person_id = row + 1
        else:
            person_id = 1

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        if conn:
            conn.rollback()

        raise Exception(error)

    finally:
        if conn is not None:
            conn.close()

    CP1_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # def create_room(self, room_name, room_type, room_gender=''):
    def create_room(self, *args):
        rooms_to_add = []  # [['accra', 'office'], ['home', 'space', 'm']]
        not_added = []
        for arg in args:
            if re.search('(:)', arg):
                rooms_to_add.append(arg.split(':'))
            else:
                not_added.append(arg)

        if len(not_added) != 0:
            return ('The following rooms will not added due to input format errors: {0}'.format(', '.join(not_added)))

        if len(rooms_to_add) != 0:
            for room_details in rooms_to_add:
                room_name = room_details[0].strip().title()
                room_type = room_details[1].strip().lower()
                room_gender = '' if len(room_details) < 3 else room_details[2].strip().lower()

                found_matches = Amity.search_room(self, Amity.room, room_name)

                if isinstance(found_matches, dict) and len(found_matches.keys()) > 0:
                    raise ValueError('Room already exists')
                else:
                    if room_type not in ['office', 'space', 'living space']:
                        return ('A room can either be an OFFICE or a LIVING SPACE')

                    elif room_type == 'office':
                        if room_gender != '':
                            return ('An office can be occupied by both male and female')
                        else:
                            new_office = Office(room_name)

                            # if len(new_office.rname) > 0:
                            #     Amity.room_id = Amity.room_id if Amity.office.__len__(
                            #     ) == 0 else max(Amity.room.keys()) + 1

                            Amity.office[Amity.room_id] = [new_office.rname.title(), new_office.rtype.lower(
                            ), new_office.max_no, new_office.rgender.upper(), new_office.occupancy]

                            print ('{0} added successfully with ID {1}'.format(
                                new_office.rname, Amity.room_id))

                    elif room_type == 'space' or room_type == 'living space':
                        if room_gender == '':
                            raise ValueError(
                                'Please specify if the living space is for male or female')
                        else:
                            new_space = LivingSpace(room_name, room_gender)

                            # if len(new_space.rname) > 0:
                            #     Amity.room_id = Amity.room_id if Amity.space.__len__(
                            #     ) == 0 else Amity.room_id +1 # max(Amity.room.keys()) + 1

                            Amity.space[Amity.room_id] = [new_space.rname.title(), new_space.rtype.lower(
                            ), new_space.max_no, new_space.rgender.upper(), new_space.occupancy]

                            print ('{0} added successfully with ID {1}'.format(
                                new_space.rname, Amity.room_id))

                Amity.room_id += 1

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
        headers = ['Room ID', 'Room Name', 'Room Type',
                   'Maximum', 'Room Gender', 'Occupancy']
        print(tabulate([(k,) + tuple(v) for k, v in found_matches.items()],
                       headers=headers, tablefmt='fancy_grid'))
        # print (tabulate([found_matches[k] for k in sorted(
        # found_matches, key=found_matches.get)], headers=headers,
        # tablefmt='fancy_grid'))

    def delete_room(self, room_to_delete):

        found_matches = Amity.search_room(
            self, Amity.room, room_to_delete)

        if isinstance(found_matches, dict) and len(found_matches.keys()) == 1:
            dict_key = [key for key in found_matches.keys()][0]

            found_allocations = [key for key in Amity.allocation.keys(
            ) if Amity.allocation[key][1] == dict_key]

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
                    Amity.person_id = Amity.person_id if Amity.person.__len__(
                    ) == 0 else max(Amity.person.keys()) + 1

                    Amity.staff[Amity.person_id] = [new_staff.pname, new_staff.pgender.upper(
                    ), new_staff.role.title(), wants_accommodation.upper()]

                    print ('{0} added successfully with ID {1}'.format(
                        new_staff.pname, Amity.person_id))

        if role == 'fellow':
            new_fellow = Fellow(person_name, person_gender,
                                wants_accommodation)

            if len(new_fellow.pname) > 0:
                Amity.person_id = Amity.person_id if Amity.person.__len__(
                ) == 0 else max(Amity.person.keys()) + 1

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
        if Amity.office.__len__() == 0:
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
        person_gender = Amity.person[person_id][1]
        wants_accommodation = Amity.person[person_id][3]

        if Amity.space.__len__() == 0:
            print ('No living spaces to allocate')
        else:
            # Check for available living spaces then randomly select an space
            # to allocate
            available_male_spaces = [key for key in Amity.space.keys(
            ) if Amity.space[key][2] > Amity.space[key][4] and Amity.space[key][3] == 'M']
            available_female_spaces = [key for key in Amity.space.keys(
            ) if Amity.space[key][2] > Amity.space[key][4] and Amity.space[key][3] == 'F']

            # Create an unique key for each allocation dictionary entry
            Amity.allocation_id = 1 if len(Amity.allocation.keys()) == 0 else max(
                Amity.allocation.keys()) + 1

            # Allocate living space
            if (len(available_male_spaces) != 0 or len(available_female_spaces) != 0) and wants_accommodation == 'Y':
                if person_gender == 'M':
                    if len(available_male_spaces) == 0:
                        print ('No available male living spaces to allocate')
                    else:
                        space_to_allocate = random.choice(
                            available_male_spaces)

                        # Add the new allocation to the allocation dictionary
                        Amity.allocation[Amity.allocation_id] = [
                            person_id, space_to_allocate]

                        # Update the number of the randomly selected living space
                        # occupants
                        old_occupancy = Amity.space[space_to_allocate][4]
                        new_occupancy = old_occupancy + 1
                        Amity.space[space_to_allocate][4] = new_occupancy

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
            person_to_reallocate = [
                key for key in search_person_existence.keys()][0]
        else:
            print (search_person_existence)

        search_room_existence = Amity.search_room(
            self, Amity.room, room_to_allocate)
        if isinstance(search_room_existence, dict) and len(search_room_existence.keys()) == 1:
            room_to_allocate = [key for key in search_room_existence.keys()][0]

            # Check if the room is avaiable
            available_room_list = [key for key in Amity.room.keys(
            ) if Amity.room[key][2] > Amity.room[key][4]]

            if room_to_allocate not in available_room_list:
                raise Exception('The room is not available')
            else:
                person_name = Amity.person[person_to_reallocate][0]
                person_gender = Amity.person[person_to_reallocate][1]
                role = Amity.person[person_to_reallocate][2].lower()
                room_gender = Amity.room[room_to_allocate][3]

                new_room_type = Amity.room[room_to_allocate][1]

                found_allocations = [key for key in Amity.allocation.keys(
                ) if Amity.allocation[key][0] == person_to_reallocate]

                if len(found_allocations) == 0:
                    raise Exception(
                        'No allocations available for {0}'.format(person_name))
                elif len(found_allocations) == 1:
                    found_allocations = found_allocations[0]
                    previous_allocated_room = Amity.allocation[found_allocations][1]

                    old_room_name = Amity.room[previous_allocated_room][0]
                    old_room_type = Amity.room[previous_allocated_room][1].lower(
                    )
                    old_room_occupancy = Amity.room[previous_allocated_room][4]
                    allocation_to_update = found_allocations

                    if new_room_type != old_room_type:
                        raise Exception('No {0} allocations available for {1}'.format(
                            new_room_type, person_name))
                else:

                    for i in found_allocations:
                        print (i)
                        previous_allocated_room = Amity.allocation[i][1]

                        old_room_name = Amity.room[previous_allocated_room][0]
                        old_room_type = Amity.room[previous_allocated_room][1].lower(
                        )
                        old_room_occupancy = Amity.room[previous_allocated_room][4]
                        allocation_to_update = i
                        if old_room_type == new_room_type:
                            break
                            previous_allocated_room = Amity.allocation[i][1]
                            old_room_name = Amity.room[previous_allocated_room][0]
                            old_room_type = Amity.room[previous_allocated_room][1].lower(
                            )
                            old_room_occupancy = Amity.room[previous_allocated_room][4]
                            allocation_to_update = i

                if previous_allocated_room == room_to_allocate:
                    print ('{0} is already allocated to {1}'.format(
                        person_name, old_room_name))
                else:
                    if new_room_type == 'space' and person_gender != room_gender:
                        raise Exception('A person of gender {0} is being allocated to a living space for {1}'.format(
                            person_gender, room_gender))

                    if new_room_type == 'space' and role == 'staff':
                        raise Exception(
                            'Staff cannot be allocated living spaces')

                    Amity.allocation[allocation_to_update] = [
                        person_to_reallocate, room_to_allocate]

                    print ('{0} has been reallocated from {1} to {2} '.format(
                        person_name, previous_allocated_room, room_to_allocate))

                    if new_room_type == 'space':
                        Amity.space[previous_allocated_room][4] -= 1
                        Amity.space[room_to_allocate][4] += 1
                    elif new_room_type == 'office':
                        Amity.office[previous_allocated_room][4] -= 1
                        Amity.office[room_to_allocate][4] += 1
        else:
            print (search_room_existence)

        Amity.room = {**Amity.office, **Amity.space}

    def load_people(self, file_name):

        if file_name == '':
            raise ValueError('Please enter a file to load data from')
        else:

            if re.search(r'[a-zA-Z0-9]+\.[a-z]+', file_name):
                text_file = os.path.join(Amity.CP1_DIR, file_name)
            else:
                text_file = os.path.join(Amity.CP1_DIR, file_name + '.txt')

            if os.path.isfile(text_file):
                with open(text_file, "r") as myfile:
                    people = myfile.readlines()

                if len(people) == 0:
                    print ('The file is empty')
                else:
                    for person in people:
                        data = person.lower().split()
                        # data[0] = data[0] + data[1]
                        name = ' '.join([data[0], data[1]])

                        person_name = name
                        person_gender = data[2]
                        role = data[3]

                        wants_accommodation = 'Y' if 'y' in data else 'N'

                        if wants_accommodation == 'Y':
                            Amity.add_person(self, person_name, person_gender,
                                             role, wants_accommodation)
                        else:
                            Amity.add_person(self, person_name, person_gender,
                                             role)
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

                found_matches = [key for key in people_dict.keys(
                ) if reg_str.search(people_dict[key][0])]
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

    def delete_person(self, person_to_delete):

        found_matches = Amity.search_person(
            self, Amity.person, person_to_delete)

        if isinstance(found_matches, dict) and len(found_matches.keys()) > 1:
            # Amity.tabulate_room_output(self, found_matches)
            return ('There is more than one person with the name {0}. \
            Please view the list of all people and use their ID instead'
                    .format(person_to_delete.title()))

        elif isinstance(found_matches, dict) and\
                len(found_matches.keys()) == 1:
            dict_key = [key for key in found_matches.keys()][0]

            found_allocations = [key for key in Amity.allocation.keys(
            ) if Amity.allocation[key][0] == dict_key]

            if len(found_allocations) > 0:
                for allocation_key in found_allocations:
                    # Amity.allocation.pop(k, None)
                    del Amity.allocation[allocation_key]

            del Amity.person[dict_key]
            # Amity.person.pop(dict_key, None)

            print ('Delete successful')

        else:
            print (found_matches)

    def print_room(self, room_to_print):
        # First check if the room exists
        search_room_existence = Amity.search_room(
            self, Amity.room, room_to_print)
        if isinstance(search_room_existence, dict) and len(search_room_existence.keys()) == 1:
            # Check if room has allocations
            room_to_print = [key for key in search_room_existence.keys()][0]
            room_name = Amity.room[room_to_print][0]

            found_allocations = [key for key in Amity.allocation.keys(
            ) if Amity.allocation[key][1] == room_to_print]

            if len(found_allocations) == 0:
                return ('There are no allocations for {0}'.format(room_name))
            else:
                persons_in_room = [Amity.allocation[key][0]
                                   for key in found_allocations]
                person_name = [Amity.person[key][0] for key in persons_in_room]

                headers = ['Person Name']
                print(tabulate([[Amity.person[key][0]] for key in sorted(
                    persons_in_room)], headers=headers, tablefmt='fancy_grid'))

                people_allocated_dict = {}
                for key in persons_in_room:
                    people_allocated_dict[key] = Amity.person[key]

                return (people_allocated_dict)

        else:
            print(search_room_existence)

    def print_unallocated(self, unallocated_persons_file=''):

        living_spaces_list = [key for key in Amity.space.keys()]

        fellows_need_accommodation = {
            key for key in Amity.person.keys() if Amity.person[key][3] == 'Y'}
        fellows_allocated_living_space = {Amity.allocation[key][0] for key in Amity.allocation.keys(
        ) if Amity.allocation[key][1] in living_spaces_list}

        fellows_ids_not_allocated_space = list(
            fellows_need_accommodation - fellows_allocated_living_space)

        fellows_not_allocated_space = {}
        for key in fellows_ids_not_allocated_space:
            fellows_not_allocated_space[key] = [
                Amity.person[key][0]] + ['Living Space']

        # Find people who have no office allocated
        office_list = [key for key in Amity.office.keys()]

        all_people = {key for key in Amity.person.keys()}
        people_allocated_office = {Amity.allocation[key][0] for key in Amity.allocation.keys()
                                   if Amity.allocation[key][1] in office_list}

        people_ids_not_allocated_office = list(
            all_people - people_allocated_office)

        unallocated_both_office_and_space = list(
            set(fellows_ids_not_allocated_space) & set(people_ids_not_allocated_office))

        people_unallocated_office = {}
        for key in people_ids_not_allocated_office:
            if key in unallocated_both_office_and_space:
                fellows_not_allocated_space[key][1] = 'Office, Living Space'
            else:
                people_unallocated_office[key] = [
                    Amity.person[key][0]] + ['Office']

        people_unallocated = {**fellows_not_allocated_space, **people_unallocated_office}

        unallocated_people_keys = [key for key in people_unallocated.keys()]

        if people_unallocated.__len__() == 0:
            return 'All people have been allocated rooms'

        else:
            sorted_people_unallocated = collections.OrderedDict(
                sorted(people_unallocated.items(), key=lambda t: t[1]))

            headers = ['ID', 'Person Name', 'Pending Allocation']
            print(tabulate([(k,) + tuple(v) for k, v in sorted_people_unallocated.items()],
                           headers=headers, tablefmt='fancy_grid'))

            if unallocated_persons_file != '':
                # Ensure that the file is created in the folder containing the
                # project
                if re.search(r'[a-zA-Z0-9]+\.[a-z]+', unallocated_persons_file):
                    file_path = os.path.join(
                        Amity.CP1_DIR, unallocated_persons_file)
                else:
                    file_path = os.path.join(
                        Amity.CP1_DIR, unallocated_persons_file + '.txt')

                with open(file_path, 'w') as output_file:
                    for person_id in sorted_people_unallocated.keys():
                        person_data = sorted_people_unallocated[person_id]
                        output_file.write(
                            person_data[0] + '\t' + person_data[1] + '\n')

    def print_allocations(self, allocation_output_file=''):
        if Amity.allocation.__len__() == 0:
            print ('No allocations available')
        else:
            allocated_rooms = list(
                {value[1] for key, value in Amity.allocation.items()})

            if allocation_output_file == '':
                file_path = os.path.join(Amity.CP1_DIR, 'allocation.txt')
            elif re.search(r'[a-zA-Z0-9]+\.[a-z]+', allocation_output_file):
                file_path = os.path.join(Amity.CP1_DIR, allocation_output_file)
            else:
                file_path = os.path.join(
                    Amity.CP1_DIR, allocation_output_file + '.txt')

            with open(file_path, 'w') as output_file:
                for room_id in (allocated_rooms):
                    people_in_room = [Amity.allocation[key][0] for key in Amity.allocation.keys()
                                      if Amity.allocation[key][1] == room_id]
                    name_of_people_in_room = [
                        Amity.person[person_id][0] for person_id in people_in_room]
                    room_name = Amity.room[room_id][0]

                    return (room_name + '\n' + '------------------------------' +
                            '\n' + ', '.join(sorted(name_of_people_in_room)) + '\n\n')

                    output_file.writelines(room_name + '\n' + '------------------------------' +
                                           '\n' + ', '.join(sorted(name_of_people_in_room)) + '\n\n')

    def save_state(self, db_name=''):

        all_people = []
        for key in Amity.person.keys():
            person_details = tuple([key] + Amity.person[key])
            all_people.append(person_details)

        all_rooms = []
        for key in Amity.room.keys():
            room_details = tuple([key] + Amity.room[key])
            all_rooms.append(room_details)

        all_allocations = []
        for key in Amity.allocation.keys():
            allocations_details = tuple(Amity.allocation[key])
            all_allocations.append(allocations_details)

        if db_name == '':
            db_name = 'cp1_amity'
            user_name = 'amity'
            user_password = 'amity'

        insert_people = ("""INSERT INTO person VALUES (%s, %s, %s, %s, %s)""")
        insert_rooms = ("""INSERT INTO room VALUES (%s, %s, %s, %s, %s, %s)""")
        insert_allocations = ("""INSERT INTO allocations VALUES (%s, %s)""")

        insert_commands = [insert_people, insert_rooms, insert_allocations]
        values_to_insert = [all_people, all_rooms, all_allocations]

        conn = None

        try:
            # params = config()
            # conn = psycopg2.connect(**params)
            conn = psycopg2.connect(database=db_name)
            # ,user = user_name, password = user_password)

            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            for i in range(3):
                cur.executemany(insert_commands[i], values_to_insert[i])

            cur.close()
            conn.commit()

            print (
                'PERSON, ROOM, and ALLOCATIONS data successfully saved to the DB {0}'.format(db_name))

        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()

            # print ('Error %s' % error)
            raise Exception(error)
            sys.exit(1)

        # Release the resources
        finally:
            if conn is not None:
                conn.close()

    def load_state(self, db_name=''):
        # Use DB Name specified
        # Check if DB exists
        if db_name == '':
            db_name = 'cp1_amity'
            user_name = 'amity'
            user_password = 'amity'

        query_staff = ("""SELECT * FROM person WHERE role = 'Staff'""")
        query_fellow = ("""SELECT * FROM person WHERE role = 'Fellow'""")
        query_space = ("""SELECT * FROM room WHERE room_type = 'space'""")
        query_office = ("""SELECT * FROM room WHERE room_type = 'office'""")
        query_allocations = ("""SELECT * FROM allocations""")

        # sql_queries = [query_people, query_rooms, query_allocations]

        conn = None
        try:
            # params = config()
            # conn = psycopg2.connect(**params)
            conn = psycopg2.connect(database=db_name)
            # ,user = user_name, password = user_password)

            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            cur.execute(query_staff)
            rows = cur.fetchall()
            for row in rows:
                staff_id = row[0]
                details = row[1:]
                Amity.staff[staff_id] = details

            cur.execute(query_fellow)
            rows = cur.fetchall()
            for row in rows:
                fellow_id = row[0]
                details = row[1:]
                Amity.fellow[fellow_id] = details

            Amity.person = {**Amity.fellow, **Amity.staff}

            cur.execute(query_space)
            rows = cur.fetchall()
            for row in rows:
                space_id = row[0]
                details = row[1:]
                Amity.space[space_id] = details

            cur.execute(query_office)
            rows = cur.fetchall()
            for row in rows:
                office_id = row[0]
                details = row[1:]
                Amity.office[office_id] = details

            Amity.room = {**Amity.office, **Amity.space}

            cur.execute(query_allocations)
            rows = cur.fetchall()
            alloc_id = 1
            for row in rows:
                Amity.allocation[alloc_id] = row
                alloc_id += 1

        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()

            # print ('Error %s' % error)
            raise Exception(error)
            sys.exit(1)

        # Release the resources
        finally:
            if conn is not None:
                conn.close()

a = Amity()

# a.create_room('accra:office', 'home:space:m', 'room', 'more rooms')
# a.create_room('Malindi:office')


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


# print ('\n\n**********ROOMS*************')
# print (a.room)
# print ('\n\n**********OFFICE*************')
# print (a.office)
# print ('\n\n**********SPACE*************')
# print (a.space)

# print ('\n\n----------------------')
# a.reallocate_room(101, 'Asmara')
# a.reallocate_room('jose', 3)
# a.delete_person('Jose')
# a.delete_person(101)

# print ('\n***********************')
# print (a.allocation)

# print ('\n\n***********************')
# print (a.room)
# # a.print_room('Asmara')
# a.print_unallocated('Unallocated.json')
# a.print_allocations('allocations')

# a.save_state()
# a.save_state('cp1_amity')


print ('\n\n***********************')
a.load_state()
