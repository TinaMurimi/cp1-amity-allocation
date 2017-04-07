import collections
import json
import os
import os.path
import psycopg2
import psycopg2.extras
import random
import re
import sys

from operator import itemgetter
from prettytable import PrettyTable
from tabulate import tabulate

from models.config import config
from models.person import Person, Staff, Fellow
from models.room import Room, LivingSpace, Office


class Amity(object):

    office = []
    space = []
    room = []

    staff = []
    fellow = []
    person = []

    allocation = []

    CP1_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # def create_room(self, room_name, room_type, room_gender=''):
    def create_room(self, *args):
        Amity.room = Amity.office + Amity.space

        rooms_to_add = []  # {2:['accra', 'office'], 1:['home', 'space', 'm']}
        not_added = []
        for arg in args:
            if re.search('(:)', arg):
                rooms_to_add.append(arg.split(':'))
            else:
                not_added.append(arg)

        if not_added:
            print ('\nThe following rooms will not added due to input format errors: {0}'.format(
                ', '.join(not_added)))

        if rooms_to_add:
            # Get the max(room_id) from the database table
            conn = None
            try:
                conn = psycopg2.connect(database='cp1_amity')
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                # To avoid duplicate primary keys from being added
                sql_query = ("""SELECT MAX(room_id) FROM room""")
                cur.execute(sql_query)
                row = cur.fetchall()[0][0]

                max_room_id = row + 1 if row is not None else 1

                cur.close()

            except (Exception, psycopg2.DatabaseError) as error:
                if conn:
                    conn.rollback()

                raise Exception(error)

            finally:
                if conn is not None:
                    conn.close()

            # The room_id to be used for a new room created
            room_ids_assgined = [room_details['room_id'] for room_details in Amity.room]
            room_id = max_room_id if not room_ids_assgined else max(
                room_ids_assgined) + 1

            for room_details in rooms_to_add:
                room_name = room_details[0].strip().title()
                room_type = room_details[1].strip().lower()
                room_gender = '' if len(
                    room_details) < 3 else room_details[2].strip().lower()

                found_matches = Amity.search_room(self, room_name)
                if isinstance(found_matches, dict) and found_matches:
                    raise ValueError('Room already exists')
                else:
                    if room_type not in ['office', 'space', 'living space']:
                        return ('A room can either be an OFFICE or a LIVING SPACE')

                    elif room_type == 'office':
                        if room_gender != '':
                            return ('An office can be occupied by both male and female')
                        else:
                            new_office = Office(room_name)

                            Amity.office.append({'room_id': room_id, 'room_name': new_office.rname.title(), 'room_type': new_office.rtype.lower(
                            ), 'max_no': new_office.max_no, 'room_gender': new_office.rgender.upper(), 'occupancy': new_office.occupancy})

                            print ('{0} added successfully with ID {1}'.format(
                                new_office.rname, room_id))

                    elif room_type == 'space' or room_type == 'living space':
                        if room_gender == '':
                            raise ValueError(
                                'Please specify if the living space is for male or female')
                        else:
                            new_space = LivingSpace(room_name, room_gender)

                            Amity.space.append({'room_id': room_id, 'room_name': new_space.rname.title(), 'room_type': new_space.rtype.lower(
                            ), 'max_no': new_space.max_no, 'room_gender': new_space.rgender.upper(), 'occupancy': new_space.occupancy})

                            print ('{0} added successfully with ID {1}'.format(
                                new_space.rname, room_id))

                room_id += 1

            Amity.room = Amity.office + Amity.space

    def search_room(self, room_to_search):
        dict_to_search = Amity.room

        if isinstance(room_to_search, int) or isinstance(room_to_search, str):
            room_to_search = str(room_to_search)
            room_to_search = room_to_search.strip().title()

            reg_str = re.compile(
                r'\b' + re.escape(room_to_search) + r'\b')

            found_matches = [{'index': index, 'details': dict_to_search[index]} for index in range(len(dict_to_search)) if reg_str.search(
                str(dict_to_search[index]['room_id'])) or reg_str.search(dict_to_search[index]['room_name'])]

            if not found_matches:
                return ("No entry found for room with ID or name {0}".format(
                    room_to_search.title()))
            else:
                # Amity.tabulate_room_output(self, list_of_found_matches)
                return found_matches[0]

        else:
            raise TypeError('Ínvalid input')  # to correct

    def tabulate_room_output(self, found_matches):
        headers = ['Room ID', 'Room Name', 'Room Type',
                   'Maximum', 'Room Gender', 'Occupancy']

        print(tabulate([(k,) + tuple(v) for k, v in found_matches.items()],
                       headers=headers, tablefmt='fancy_grid'))

    def delete_room(self, room_to_delete):

        found_matches = Amity.search_room(self, room_to_delete)
        if isinstance(found_matches, dict) and found_matches:
            room_index_to_delete = found_matches['index']
            room_id_to_delete = found_matches['details']['room_id']
            room_type_to_delete = found_matches['details']['room_type']

            found_allocations = [index for index in range(
                len(Amity.allocation)) if Amity.allocation[index]['room_id'] == room_id_to_delete]
            Amity.allocation = [Amity.allocation[index] for index in range(
                len(Amity.allocation)) if index not in found_allocations]

            if room_type_to_delete == 'office':
                index_in_office_dict = [index for index in range(
                    len(Amity.office)) if Amity.office[index]['room_id'] == room_id_to_delete][0]
                del Amity.office[index_in_office_dict]

            elif room_type_to_delete == 'space':
                index_in_space_dict = [index for index in range(
                    len(Amity.space)) if Amity.space[index]['room_id'] == room_id_to_delete][0]
                del Amity.space[index_in_space_dict]

            Amity.room = Amity.space + Amity.office

            # Check if delete is successful
            found_matches = Amity.search_room(self, room_to_delete)
            if isinstance(found_matches, str):
                print ('\nDelete successful')
            else:
                print ('\nDelete unsuccessful')

        else:
            print (found_matches)

    def add_person(self, person_name, person_gender, role, wants_accommodation='N'):

        conn = None
        try:
            conn = psycopg2.connect(database='cp1_amity')
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # To avoid duplicate primary keys from being added
            sql_query = ("""SELECT MAX(person_id) FROM person""")
            cur.execute(sql_query)
            row = cur.fetchall()[0][0]

            max_person_id = row + 1 if row is not None else 1

            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()

            raise Exception(error)

        finally:
            if conn is not None:
                conn.close()

        Amity.person = Amity.fellow + Amity.staff

        # The person_id to be used for a new room created
        person_ids_assgined = [person_details['person_id'] for person_details in Amity.person]
        person_id = max_person_id if not person_ids_assgined else max(
            person_ids_assgined) + 1

        person_name = person_name.strip().title()
        person_gender = person_gender.strip().upper()
        role = role.strip().title()
        wants_accommodation = wants_accommodation.strip().upper()

        if role not in ['Staff', 'Fellow']:
            return ('A person can either have the role STAFF or FELLOW')

        elif role == 'Staff':
            if wants_accommodation != 'N':
                return ('Staff cannot be allocated living spaces')
            else:
                new_staff = Staff(person_name, person_gender)

                Amity.staff.append({'person_id': person_id, 'person_name': new_staff.pname, 'person_gender': new_staff.pgender,
                                    'role': new_staff.role.title(), 'wants_accommodation': wants_accommodation})

                print ('{0} added successfully with ID {1}'.format(
                    new_staff.pname, person_id))

                # Allocate Office and Living Space
                print ('Allocate Office and Living Space for staff\n')
                Amity.allocate_room(self, person_id)

                person_id += 1

        elif role == 'Fellow':
            new_fellow = Fellow(person_name, person_gender,
                                wants_accommodation)

            Amity.fellow.append({'person_id': person_id, 'person_name': new_fellow.pname, 'person_gender': new_fellow.pgender,
                                 'role': new_fellow.role.title(), 'wants_accommodation': wants_accommodation})

            print ('{0} added successfully with ID {1}'.format(
                new_fellow.pname, person_id))

            # Allocate Office and Living Space
            print ('Allocate Office and Living Space for fellow\n')
            Amity.allocate_room(self, person_id)

            person_id += 1

        Amity.person = Amity.fellow + Amity.staff

    def allocate_room(self, person_id_to_allocate):

        Amity.person = Amity.fellow + Amity.staff

        person_details = [person_details for person_details in Amity.person if person_details['person_id'] == person_id_to_allocate][0]
        person_gender = person_details['person_gender']
        wants_accommodation = person_details['wants_accommodation']

        # Allocate office
        # Check for available office then randomly select an office to allocate

        available_office_list = [{'index': index, 'room_id': Amity.office[index]['room_id']} for index in range(
            len(Amity.office)) if Amity.office[index]['max_no'] > Amity.office[index]['occupancy']]

        if not available_office_list:
            print ('No offices to allocate')
        else:
            office_to_allocate = random.choice(available_office_list)
            Amity.allocation.append(
                {'person_id': person_id_to_allocate, 'room_id': office_to_allocate['room_id']})

            # Update the number of the randomly selected office occupants
            prev_occupancy = Amity.office[office_to_allocate['index']]['occupancy']
            new_occupancy = prev_occupancy + 1
            Amity.office[office_to_allocate['index']
                         ]['occupancy'] = new_occupancy

        # Allocate living space
        if not Amity.space:
            print ('No living spaces to allocate')
        else:
            # Check for available living spaces then randomly select an space
            # to allocate
            available_male_spaces = [{'index': index, 'room_id': Amity.space[index]['room_id']} for index in range(len(
                Amity.space)) if Amity.space[index]['room_gender'] == 'M' and Amity.space[index]['max_no'] > Amity.space[index]['occupancy']]

            available_female_spaces = [{'index': index, 'room_id': Amity.space[index]['room_id']} for index in range(len(
                Amity.space)) if Amity.space[index]['room_gender'] == 'F' and Amity.space[index]['max_no'] > Amity.space[index]['occupancy']]

            # Allocate living space
            if (available_male_spaces or available_female_spaces) and wants_accommodation == 'Y':
                if person_gender == 'M':
                    if len(available_male_spaces) == 0:
                        print ('No available male living spaces to allocate')
                    else:
                        space_to_allocate = random.choice(
                            available_male_spaces)

                        # Add the new allocation to the allocation dictionary
                        Amity.allocation.append(
                            {'person_id': person_id_to_allocate, 'room_id': space_to_allocate['room_id']})

                        # Update the number of the randomly selected living
                        # space occupants
                        prev_occupancy = Amity.space[space_to_allocate['index']]['occupancy']
                        new_occupancy = prev_occupancy + 1
                        Amity.space[space_to_allocate['index']
                                    ]['occupancy'] = new_occupancy

                elif person_gender == 'F':
                    if len(available_female_spaces) == 0:
                        print ('No available female living spaces to allocate')
                    else:
                        space_to_allocate = random.choice(
                            available_female_spaces)

                        # Add the new allocation to the allocation dictionary
                        Amity.allocation.append(
                            {'person_id': person_id_to_allocate, 'room_id': space_to_allocate['room_id']})

                        # Update the number of the randomly selected living space
                        # occupants
                        prev_occupancy = Amity.space[space_to_allocate['index']]['occupancy']
                        new_occupancy = prev_occupancy + 1
                        Amity.space[space_to_allocate['index']
                                    ]['occupancy'] = new_occupancy

        Amity.room = Amity.office + Amity.space

    def reallocate_room(self, person_to_reallocate, room_to_allocate):

        # Check if the person exists
        found_people = Amity.search_person(self, person_to_reallocate)

        if isinstance(found_people, list) and len(found_people) > 1:
            raise Exception('There is more than one person with the name {0}. Please view the list of all people and use their ID instead'.format(
                person_to_reallocate.title()))

        elif isinstance(found_people, list) and len(found_people) == 1:

            found_people = found_people[0]
            person_id_to_reallocate = found_people['details']['person_id']

            # Check if the room exists
            found_rooms = Amity.search_room(self, room_to_allocate)

            if isinstance(found_rooms, dict) and found_rooms:
                room_id_to_reallocate = found_rooms['details']['room_id']
                new_room_name = found_rooms['details']['room_name']
                new_room_type = found_rooms['details']['room_type']
                new_room_gender = found_rooms['details']['room_gender']
                new_room_index = found_rooms['index']

                # Check if the room is avaiable
                available_room_list = [{'index': index, 'room_id': Amity.room[index]['room_id']} for index in range(
                    len(Amity.room)) if Amity.room[index]['max_no'] > Amity.room[index]['occupancy']]

                available_rooms_ids = [available_room_list[index]['room_id']
                                       for index in range(len(available_room_list))]

                if room_id_to_reallocate not in available_rooms_ids:
                    raise Exception('The room is not available')

                else:
                    person_id_to_reallocate = found_people['details']['person_id']
                    person_name = found_people['details']['person_name']
                    person_gender = found_people['details']['person_gender']
                    role = found_people['details']['role']

                    print('\nAmity.allocation.__len__',
                          person_id_to_reallocate, Amity.allocation[1]['person_id'])
                    print('\n')

                    found_allocations = [allocation_details for allocation_details in Amity.allocation if allocation_details['person_id'] ==                                    person_id_to_reallocate]
                    found_allocations_rooms = [allocation_details['room_id'] for allocation_details in Amity.allocation if allocation_details['person_id'] == person_id_to_reallocate]

                    if not found_allocations:
                        raise Exception(
                            'No allocations available for {0}'.format(person_name))

                    else:
                        if new_room_type == 'office':
                            office_ids = [Amity.office[index]['room_id']
                                          for index in range(len(Amity.office))]
                            prev_office_id = [found_allocations_rooms[index] for index in range(
                                len(found_allocations_rooms)) if found_allocations_rooms[index] in office_ids][0]
                            prev_office = [{'index': index, 'details': Amity.office[index]} for index in range(
                                len(Amity.office)) if Amity.office[index]['room_id'] == prev_office_id][0]

                            if not prev_office_id:
                                raise Exception('No {0} allocations available for {1}'.format(
                                    new_room_type, person_name))
                            else:
                                # Reallocate office
                                prev_room_id = prev_office['details']['room_id']
                                prev_room_name = prev_office['details']['room_name']
                                prev_room_index = prev_office['index']

                                if prev_room_id == room_id_to_reallocate:
                                    print ('{0} is already allocated to {1}'.format(
                                        person_name, prev_room_name))
                                else:
                                    Amity.allocation[prev_room_index] = {
                                        'person_id': person_id_to_reallocate, 'room_id': room_id_to_reallocate}

                                    # Update the occupancy
                                    Amity.office[prev_room_index]['occupancy'] -= 1
                                    Amity.office[new_room_index]['occupancy'] += 1

                                    print ('{0} has been reallocated office from {1} to {2} '.format(
                                        person_name, prev_room_name, room_to_allocate))

                        elif new_room_type == 'space':
                            if role == 'Staff':
                                raise ValueError(
                                    'Staff cannot be allocated living spaces')

                            else:
                                if new_room_gender != person_gender:
                                    raise ValueError('A person of gender {0} is being allocated to a living space for {1}'.format(
                                        person_gender, new_room_gender))

                                else:
                                    space_ids = [Amity.space[index]['room_id']
                                                 for index in range(len(Amity.space))]

                                    prev_space_id = [found_allocations_rooms[index] for index in range(
                                        len(found_allocations_rooms)) if found_allocations_rooms[index] in space_ids][0]
                                    prev_space = [{'index': index, 'details': Amity.space[index]} for index in range(
                                        len(Amity.space)) if Amity.space[index]['room_id'] == prev_space_id][0]

                                    if not prev_space:
                                        raise Exception('No {0} allocations available for {1}'.format(
                                            new_room_type, person_name))
                                    else:
                                        # Reallocate space
                                        prev_room_id = prev_space['details']['room_id']
                                        prev_room_name = prev_space['details']['room_name']
                                        prev_room_index = prev_space['index']

                                        if prev_room_id == room_id_to_reallocate:
                                            print ('{0} is already allocated to {1}'.format(
                                                person_name, prev_room_name))
                                        else:
                                            prev_space_index = prev_space['index']
                                            Amity.allocation[prev_space_index] = {
                                                'person_id': person_id_to_reallocate, 'room_id': room_id_to_reallocate}

                                            # Update the occupancy
                                            Amity.space[prev_room_index]['occupancy'] -= 1
                                            Amity.space[new_room_index]['occupancy'] += 1

                                            print ('{0} has been reallocated living space from {1} to {2} '.format(
                                                person_name, prev_room_name, room_to_allocate))

                        Amity.room = Amity.office + Amity.space

            else:
                print (found_rooms)

        else:
            print (found_people)

    def load_people(self, file_name='person.txt'):

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

    def search_person(self, person_to_search):

        if isinstance(person_to_search, int) or isinstance(person_to_search, str):
            person_to_search = str(person_to_search)
            person_to_search = person_to_search.strip().title()

            reg_str = re.compile(
                r'\b' + re.escape(person_to_search) + r'\b')

            found_matches = [{'index': index, 'details': Amity.person[index]} for index in range(len(Amity.person)) if reg_str.search(
                str(Amity.person[index]['person_id'])) or reg_str.search(Amity.person[index]['person_name'])]

            if not found_matches:
                return ("No entry found for person with ID or name {0}".format(
                    person_to_search.title()))
            else:
                # Amity.tabulate_person_output(self, list_of_found_matches)
                return found_matches

        else:
            raise TypeError('Ínvalid input')  # to correct

    def tabulate_person_output(self, found_matches):

        headers = ['ID', 'Name', 'Gender', 'Role', 'Needs Accommodation']

        print(tabulate([(k,) + tuple(v) for k, v in found_matches.items()],
                       headers=headers, tablefmt='fancy_grid'))

    def delete_person(self, person_to_delete):

        found_matches = Amity.search_person(self, person_to_delete)

        if isinstance(found_matches, list) and len(found_matches) > 1:
            raise Exception('There is more than one person with the name {0}. Please view the list of all people and use their ID instead'.format(
                person_to_reallocate.title()))

        elif isinstance(found_matches, list) and len(found_matches) == 1:

            found_matches = found_matches[0]

            person_index_to_delete = found_matches['index']
            person_id_to_delete = found_matches['details']['person_id']
            person_role_to_delete = found_matches['details']['role']

            found_allocations = [index for index in range(len(Amity.allocation)) if Amity.allocation[index]['person_id'] == person_id_to_delete]
            Amity.allocation = [Amity.allocation[index] for index in range(
                len(Amity.allocation)) if index not in found_allocations]

            if person_role_to_delete == 'Staff':
                index_in_staff_dict = [index for index in range(
                    len(Amity.staff)) if Amity.staff[index]['person_id'] == person_id_to_delete][0]
                del Amity.staff[index_in_staff_dict]

            elif person_role_to_delete == 'Fellow':
                index_in_fellow_dict = [index for index in range(
                    len(Amity.fellow)) if Amity.fellow[index]['person_id'] == person_id_to_delete][0]
                del Amity.fellow[index_in_fellow_dict]

            else:
                print ('\nIS  NEITHER STAFF NOR FELLOW\n')

            Amity.person = Amity.fellow + Amity.staff

            # Check if delete is successful
            found_matches = Amity.search_room(self, person_to_delete)
            if isinstance(found_matches, str):
                print ('\nDelete successful')
            else:
                print ('\nDelete unsuccessful')

        else:
            print (found_matches)

    def print_room(self, room_to_print):
        # First check if the room exists
        found_rooms = Amity.search_room(self, room_to_print)

        if isinstance(found_rooms, dict) and found_rooms:
            room_id = found_rooms['details']['room_id']
            room_name = found_rooms['details']['room_name']
            room_index = found_rooms['index']

            found_allocations = [Amity.allocation[index]['room_id'] for index in range(
                len(Amity.allocation)) if Amity.allocation[index]['room_id'] == room_id]

            if not found_allocations:
                return ('There are no allocations for {0}'.format(room_name))
            else:
                persons_in_room = [Amity.allocation[index]['person_id'] for index in range(
                    len(Amity.allocation)) if Amity.allocation[index]['room_id'] == room_id]
                person_name = [Amity.person[index]['person_name'] for index in range(
                    len(Amity.person)) if Amity.person[index]['person_id'] in persons_in_room]

                headers = ['Person Name']
                print(tabulate([[name] for name in person_name],
                               headers=headers, tablefmt='fancy_grid'))

                return (person_name)

        else:
            print(found_rooms)

    def print_unallocated(self, unallocated_persons_file=''):

        living_spaces_list = [Amity.space[index]['room_id']
                              for index in range(len(Amity.space))]

        fellows_need_accommodation = [Amity.person[index]['person_id'] for index in range(
            len(Amity.person)) if Amity.person[index]['wants_accommodation'] == 'Y']
        fellows_allocated_living_space = [Amity.allocation[index]['person_id'] for index in range(
            len(Amity.allocation)) if Amity.allocation[index]['room_id'] in living_spaces_list]

        fellows_ids_not_allocated_space = list(
            set(fellows_need_accommodation) - set(fellows_allocated_living_space))
        fellows_not_allocated_space = [{'person_id': Amity.person[index]['person_id'], 'person_name':Amity.person[index]['person_name'],
                                        'Unallocated':'Living Space'} for index in range(len(Amity.person)) if Amity.person[index]['person_id'] in fellows_ids_not_allocated_space]

        # Find people who have no office allocated
        office_list = [Amity.office[index]['room_id']
                       for index in range(len(Amity.office))]

        all_people = [Amity.person[index]['person_id']
                      for index in range(len(Amity.person))]
        people_allocated_office = [Amity.allocation[index]['person_id'] for index in range(
            len(Amity.allocation)) if Amity.allocation[index]['room_id'] in office_list]

        people_ids_not_allocated_office = list(
            set(all_people) - set(people_allocated_office))

        unallocated_both_office_and_space = list(
            set(fellows_ids_not_allocated_space) & set(people_ids_not_allocated_office))

        people_ids_unallocated = list(
            set(fellows_ids_not_allocated_space + people_ids_not_allocated_office))

        for index in range(len(people_ids_unallocated)):
            if people_ids_unallocated[index] in unallocated_both_office_and_space:
                position = [position for position in range(len(
                    fellows_not_allocated_space)) if people_ids_unallocated[index] == fellows_ids_not_allocated_space[position]][0]
                fellows_not_allocated_space[position]['Unallocated'] = 'Office, Living Space'

        not_allocated_office_id = list(
            set(people_ids_not_allocated_office) - set(unallocated_both_office_and_space))
        people_unallocated_office = [{'person_id': Amity.person[index]['person_id'], 'person_name':Amity.person[index]['person_name'],
                                      'Unallocated':'Living Space'} for index in range(len(Amity.person)) if Amity.person[index]['person_id'] in not_allocated_office_id]

        people_unallocated = fellows_not_allocated_space + people_unallocated_office
        people_unallocated = sorted(
            people_unallocated, key=itemgetter('person_name'))

        if not people_unallocated:
            return 'All people have been allocated rooms'

        else:
            headers = ['ID', 'Person Name', 'Pending Allocation']
            print(tabulate([item.values() for item in people_unallocated],
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
                    for details in people_unallocated:
                        output_file.write(
                            str(details['person_id']) + '\t' + details['person_name'] + '\t' + details['Unallocated'] + '\n')

    def print_allocations(self, allocation_output_file=''):
        if Amity.allocation.__len__() == 0:
            print ('No allocations available')
        else:
            allocated_rooms = list(
                set([item['room_id'] for item in Amity.allocation]))

            if allocation_output_file == '':
                file_path = os.path.join(Amity.CP1_DIR, 'allocation.txt')
            elif re.search(r'[a-zA-Z0-9]+\.[a-z]+', allocation_output_file):
                file_path = os.path.join(Amity.CP1_DIR, allocation_output_file)
            else:
                file_path = os.path.join(
                    Amity.CP1_DIR, allocation_output_file + '.txt')

            room_details = [{'room_id': room_details['room_id'], 'room_name':room_details['room_name']}
                            for room_details in Amity.room if room_details['room_id'] in allocated_rooms]
            room_details = sorted(room_details, key=itemgetter('room_name'))

            with open(file_path, 'w') as output_file:
                for room_info in room_details:
                    people_in_room = [
                        item['person_id'] for item in Amity.allocation if item['room_id'] == room_info['room_id']]
                    name_of_people_in_room = sorted(
                        [person_details['person_name'] for person_details in Amity.person if person_details['person_id'] in people_in_room])

                    output_file.writelines(room_info['room_name'] + '\n' + '------------------------------' +
                                           '\n' + ', '.join(sorted(name_of_people_in_room)) + '\n\n')

                    print (room_info['room_name'] + '\n' + '------------------------------' +
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
            conn = psycopg2.connect(database=db_name)
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

        conn = None
        try:
            conn = psycopg2.connect(database=db_name)
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

            Amity.person = Amity.fellow + Amity.staff

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

            raise Exception(error)
            sys.exit(1)

        # Release the resources
        finally:
            if conn is not None:
                conn.close()


# a = Amity()

# a.create_room('accra:office', 'room', 'more rooms',
              'tsavo:office', 'malindi:office')
# a.create_room('male Room:space:m', 'Female Room:space:f')
# a.create_room('platform:office')
# a.create_room('ACCRA:office')

# print ('\n\n********* OFFICES CREATED **************')
# print (a.office)

# print ('\n\n********* SPACES CREATED **************')
# print (a.space)

# print ('\n\n********* ROOMS CREATED **************')
# print (a.room)


# asmara = a.create_room('Asmara', 'office', 6, '')
# tsavo = a.create_room('Tsavo', 'office', 6, '')
# platform = a.create_room('Platform', 'office', 6, '')


# accra = a.create_room('Accra', 'space', 4, 'F')
# hog = a.create_room('Hog', 'space', 4, 'M')
# malindi = a.create_room('Malindi', 'space', 4, 'M')
# coast = a.create_room('Coast', 'space', 4, 'F')

# print ('\n')
# jane = a.add_person('Jane', 'F', 'Staff')
# maria = a.add_person('Maria', 'F', 'Fellow', 'Y')
# mark = a.add_person('Mark', 'M', 'Staff')
# jose = a.add_person('Jose', 'M', 'Fellow')
# joe = a.add_person('Joe', 'M', 'Fellow', 'Y')
# joem = a.add_person('Joe Maina', 'M', 'Fellow', 'Y')
# janet = a.add_person('Janet', 'F', 'Fellow', 'Y')
# luke = a.add_person('Luke', 'M', 'Fellow')

# a.load_people('person.txt')

# a.search_person(a.person, 'Jose')

# print ('\n\n********* ROOMS CREATED **************')
# print (a.room)

# print ('\n\n********* PEOPLE ADDED **************')
# print (a.person)


# print ('\n********* SEARCH PERSON **************')
# print (a.search_person('LUkE'))
# print (a.search_person('Jane'))
# print ('\n')

# print ('\n********** ALLOCATIONS *************')
# print (a.allocation)
# print ('\n')

# print ('\n\n********** DELETE ROOM *************')
# a.delete_room('FEMALE Room')
# a.delete_room('JUST A Room')
# print (a.allocation)


# print ('\n********* SEARCH ROOM **************')
# print (a.search_room(101))
# print (a.search_room('Asmara'))

# print ('\n********** REALLOCATE ROOM *************')
# a.reallocate_room('Jose', 'Asmara')

# print ('\n********** REALLOCATE ROOM2 *************')
# a.reallocate_room('Jose', 'platform')

# print ('\n********** REALLOCATE ROOM3 *************')
# a.reallocate_room('Jose', 'MALINDI')

# print ('\n********** REALLOCATE ROOM4 *************')
# a.reallocate_room('Jose', 'tsavo')

# print ('\n********** REALLOCATE ROOM5 *************')
# a.reallocate_room('Jose', 'Female Room')

# print ('\n********** REALLOCATE ROOM6 *************')
# a.reallocate_room('Jose', 'male Room')
# print ('\n')


# print ('\n********** DELETE PERSON *************')
# a.delete_person('Jose')
# a.delete_person(101)

# print (a.person)
# print ('\n')

# print ('\n***********************')
# print (a.allocation)

# print ('\n\n*********** PRINT ROOM ************')
# print (a.room)
# a.print_room('accra')

# print ('\n\n*********** PRINT UNALLOCATED ************')
# a.print_unallocated('Unallocated.txt')

print ('\n\n*********** PRINT ALLOCATIONS ************')
a.print_allocations('allocations')

# a.save_state()
# a.save_state('cp1_amity')


# print ('\n\n***********************')
# a.load_state()
