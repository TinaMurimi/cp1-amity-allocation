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

# from models.config import config
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

    def create_room(self, room_type, room_gender, *rooms_to_add):

        prev_no_of_rooms = len(Amity.room)

        room_type = room_type.strip().lower()
        room_gender = room_gender.strip().upper()

        if room_gender.title() not in ('Male', 'Female', 'M', 'F', ''):
            return(
                'Use Male or Female to specify gender that will occupy room')
        else:
            if rooms_to_add:
                # Get the max(room_id) from the database table
                conn = None
                try:
                    conn = psycopg2.connect(database='cp1_amity')
                    cur = conn.cursor(
                        cursor_factory=psycopg2.extras.DictCursor)

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
                room_ids_assgined = [room_details['room_id']
                                     for room_details in Amity.room]
                room_id = max_room_id if not room_ids_assgined else max(
                    room_ids_assgined) + 1

                for room_name in rooms_to_add[0]:
                    room_name = room_name.strip().title()
                    found_matches = Amity.search_room(self, room_name)

                    if isinstance(found_matches, dict) and found_matches:
                        return ('Room already exists')

                    else:
                        if room_type not in ['office', 'space', 'living space']:
                            return ('A room can either be an OFFICE or a LIVING SPACE')

                        elif room_type == 'office':
                            if room_gender != '':
                                return(
                                    'An office can be occupied by both male and female')
                            else:
                                new_office = Office(room_name)

                                Amity.office.append({'room_id': room_id, 'room_name': new_office.room_name.title(), 'room_type': new_office.room_type.lower(
                                ), 'max_no': new_office.max_no, 'room_gender': new_office.room_gender.upper(), 'occupancy': new_office.occupancy})

                                print ('{0} added successfully with ID {1}'.format(
                                    new_office.room_name, room_id))

                        elif room_type == 'space' or room_type == 'living space':
                            if room_gender == '':
                                return(
                                    'Please specify if the living space is for male or female')
                            else:
                                new_space = LivingSpace(room_name, room_gender)

                                Amity.space.append({'room_id': room_id, 'room_name': new_space.room_name.title(), 'room_type': new_space.room_type.lower(
                                ), 'max_no': new_space.max_no, 'room_gender': new_space.room_gender.upper(), 'occupancy': new_space.occupancy})

                                print ('{0} added successfully with ID {1}'.format(
                                    new_space.room_name, room_id))

                    room_id += 1

            else:
                print ('Room no rooms to add')

        Amity.room = Amity.office + Amity.space
        if len(Amity.room) - prev_no_of_rooms != len(rooms_to_add[0]):
            return ('Rooms not added')
        else:
            return ('{} rooms added successfully'.format(len(rooms_to_add[0])))

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
                return found_matches[0]

        else:
            return ('Ínvalid input')

    def list_rooms(self):

        headers = ['Room ID', 'Room Name', 'Room Type',
                   'Capacity', 'Room Gender', 'Current Occupancy']

        list_of_rooms = sorted(
            Amity.room, key=itemgetter('room_id'))

        print(tabulate([item.values() for item in list_of_rooms],
                       headers=headers, tablefmt='fancy_grid'))

    def delete_room(self, room_to_delete):
        found_matches = Amity.search_room(self, room_to_delete)

        if isinstance(found_matches, dict) and found_matches:
            room_index_to_delete = found_matches['index']
            room_id_to_delete = found_matches['details']['room_id']
            room_type_to_delete = found_matches['details']['room_type']
            room_name_to_delete = found_matches['details']['room_name']

            # Delete allocations for room
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
                return ('{} has been deleted successfully'.format(
                    room_name_to_delete))
            else:
                return ('{} has NOT deleted'.format(room_name_to_delete))

        else:
            return (found_matches)

    def add_person(self, person_name, person_gender, role, wants_accommodation='N'):

        prev_no_of_people = len(Amity.person)

        if role.title() not in ['Staff', 'Fellow']:
            return (
                'A person can either have the role STAFF or FELLOW')

        if person_gender[0].upper() not in ('M', 'F'):
            return ('Use Male, M, FEmale, F to specify gender')

        if not wants_accommodation:
            wants_accommodation = 'N'
        else:
            if wants_accommodation[0].upper() not in ('Y', 'N'):
                return (
                    'Use Yes, Y, No, N to specify if a person wants accommodation or not')

        person_name = person_name.strip().title()
        person_gender = person_gender.strip().upper()
        role = role.strip().title()
        wants_accommodation = wants_accommodation.strip().upper()

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
        person_ids_assgined = [person_details['person_id']
                               for person_details in Amity.person]
        person_id = max_person_id if not person_ids_assgined else max(
            person_ids_assgined) + 1

        if role == 'Staff':
            if wants_accommodation != 'N':
                return ('Staff cannot be allocated living spaces')
            else:
                new_staff = Staff(person_name, person_gender)

                Amity.staff.append({'person_id': person_id, 'person_name': new_staff.person_name, 'person_gender': new_staff.person_gender,
                                    'role': new_staff.role.title(), 'wants_accommodation': wants_accommodation})

                print ('{0} added successfully with ID {1}'.format(
                    new_staff.person_name, person_id))

                # Allocate Office and Living Space
                Amity.allocate_room(self, person_id)

                person_id += 1

        elif role == 'Fellow':
            new_fellow = Fellow(person_name, person_gender,
                                wants_accommodation)

            Amity.fellow.append({'person_id': person_id, 'person_name': new_fellow.person_name, 'person_gender': new_fellow.person_gender,
                                 'role': new_fellow.role.title(), 'wants_accommodation': wants_accommodation})

            print ('{0} added successfully with ID {1}'.format(
                new_fellow.person_name, person_id))

            # Allocate Office and Living Space
            Amity.allocate_room(self, person_id)

            person_id += 1

        Amity.person = Amity.fellow + Amity.staff
        if len(Amity.person) - prev_no_of_people != 1:
            return ('Person not added!')

        else:
            # Check a person has been allocated rooms
            found_allocations = [
                allocations for allocations in Amity.allocation if allocations['person_id'] == person_id - 1]
            if found_allocations:
                return ('Person added and allocated room')
            else:
                return ('Person added but not allocated (all) rooms')

    def allocate_room(self, person_id_to_allocate):
        Amity.person = Amity.fellow + Amity.staff

        person_details = [
            person_details for person_details in Amity.person if person_details['person_id'] == person_id_to_allocate][0]
        person_gender = person_details['person_gender'].upper()
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
                Amity.space)) if Amity.space[index]['room_gender'].upper() == 'M' and Amity.space[index]['max_no'] > Amity.space[index]['occupancy']]

            available_female_spaces = [{'index': index, 'room_id': Amity.space[index]['room_id']} for index in range(len(
                Amity.space)) if Amity.space[index]['room_gender'].upper() == 'F' and Amity.space[index]['max_no'] > Amity.space[index]['occupancy']]

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
                        prev_occupancy = Amity.space[space_to_allocate['index']
                                                     ]['occupancy']
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
                        prev_occupancy = Amity.space[space_to_allocate['index']
                                                     ]['occupancy']
                        new_occupancy = prev_occupancy + 1
                        Amity.space[space_to_allocate['index']
                                    ]['occupancy'] = new_occupancy

        Amity.room = Amity.office + Amity.space

    def reallocate_person(self, person_to_reallocate, room_to_allocate):

        # Check if the person exists
        found_people = Amity.search_person(self, person_to_reallocate)

        if isinstance(found_people, list) and len(found_people) > 1:
            return ('There is more than one person with the name {0}. Please view the list of all people and use their ID instead'.format(
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

                # Check if the room is avaiable
                available_room_list = [{'index': index, 'room_id': Amity.room[index]['room_id']} for index in range(
                    len(Amity.room)) if Amity.room[index]['max_no'] > Amity.room[index]['occupancy']]

                available_rooms_ids = [available_room_list[index]['room_id']
                                       for index in range(len(available_room_list))]

                if room_id_to_reallocate not in available_rooms_ids:
                    return ('{0} is not available'.format(new_room_name))

                else:
                    person_id_to_reallocate = found_people['details']['person_id']
                    person_name = found_people['details']['person_name']
                    person_gender = found_people['details']['person_gender']
                    role = found_people['details']['role']

                    found_allocations = [{'index': index, 'room_id': Amity.allocation[index]['room_id']} for index in range(
                        len(Amity.allocation)) if Amity.allocation[index]['person_id'] == person_id_to_reallocate]

                    if not found_allocations:
                        return (
                            'No allocations available for {0}'.format(person_name))

                    else:
                        if new_room_type == 'office':

                            new_office_index = [index for index in range(
                                len(Amity.office)) if Amity.office[index]['room_id'] == room_id_to_reallocate][0]

                            office_ids = [Amity.office[index]['room_id']
                                          for index in range(len(Amity.office))]

                            prev_allocated_office = [found_allocations[index] for index in range(
                                len(found_allocations)) if found_allocations[index]['room_id'] in office_ids]

                            if not prev_allocated_office:
                                return ('No {0} allocations available for {1}'.format(new_room_type, person_name))

                            else:
                                prev_allocated_office_index = prev_allocated_office[0]['index']
                                prev_allocated_office_id = prev_allocated_office[0]['room_id']

                                prev_office = [{'index': index, 'details': Amity.office[index]} for index in range(
                                    len(Amity.office)) if Amity.office[index]['room_id'] == prev_allocated_office_id][0]

                                prev_room_name = prev_office['details']['room_name']
                                prev_room_index = prev_office['index']

                                # Reallocate office
                                if prev_allocated_office_id == room_id_to_reallocate:
                                    return ('{0} is already allocated to {1}'.format(
                                        person_name, prev_room_name))

                                else:
                                    Amity.allocation[prev_allocated_office_index] = {
                                        'person_id': person_id_to_reallocate, 'room_id': room_id_to_reallocate}

                                    # Update the occupancy
                                    Amity.office[prev_room_index]['occupancy'] -= 1
                                    Amity.office[new_office_index]['occupancy'] += 1

                                    return ('{0} has been reallocated office from {1} to {2}'.format(
                                        person_name, prev_room_name, new_room_name))

                        elif new_room_type == 'space':
                            space_ids = [Amity.space[index]['room_id']
                                         for index in range(len(Amity.space))]

                            new_space_index = [index for index in range(
                                len(Amity.space)) if Amity.space[index]['room_id'] == room_id_to_reallocate][0]
                            prev_allocated_space = [found_allocations[index] for index in range(
                                len(found_allocations)) if found_allocations[index]['room_id'] in space_ids]

                            if role == 'Staff':
                                return(
                                    'Staff cannot be allocated living spaces')

                            else:
                                if new_room_gender != person_gender:
                                    return('A person of gender {0} is being allocated to a living space for {1}'.format(
                                        person_gender, new_room_gender))

                                else:
                                    if not prev_allocated_space:
                                        return ('No {0} allocations available for {1}'.format(new_room_type, person_name))

                                    else:
                                        prev_allocated_space_index = prev_allocated_space[0]['index']
                                        prev_allocated_space_id = prev_allocated_space[0]['room_id']

                                        prev_space = [{'index': index, 'details': Amity.space[index]} for index in range(
                                            len(Amity.space)) if Amity.space[index]['room_id'] == prev_allocated_space_id][0]

                                        prev_room_name = prev_space['details']['room_name']
                                        prev_room_index = prev_space['index']

                                        # Reallocate space
                                        if prev_allocated_space_id == room_id_to_reallocate:
                                            return ('{0} is already allocated to {1}'.format(
                                                person_name, prev_room_name))

                                        else:
                                            Amity.allocation[prev_allocated_space_index] = {
                                                'person_id': person_id_to_reallocate, 'room_id': room_id_to_reallocate}

                                            # Update the occupancy
                                            Amity.space[prev_room_index]['occupancy'] -= 1
                                            Amity.space[new_space_index]['occupancy'] += 1

                                            return ('{0} has been reallocated living space from {1} to {2}'.format(
                                                person_name, prev_room_name, new_room_name))

                        Amity.room = Amity.office + Amity.space

            else:
                return (found_rooms)

        else:
            return (found_people)

    def load_people(self):
        text_file = os.path.join(Amity.CP1_DIR, 'person.txt')

        prev_no_of_people = len(Amity.person)

        if os.path.isfile(text_file):
            with open(text_file, "r") as myfile:
                people = myfile.readlines()

            if not people:
                print ('The file is empty')
            else:
                for person in people:
                    data = person.lower().split()
                    name = ' '.join([data[0], data[1]])

                    person_name = name
                    person_gender = data[2]
                    role = data[3]

                    wants_accommodation = 'Y' if 'y' in data else 'N'

                    Amity.add_person(self, person_name, person_gender,
                                     role, wants_accommodation)

            if len(Amity.person) - prev_no_of_people != len(people):
                return ('People not loaded!')
            else:
                return ('{} people loaded!'.format(len(people)))

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
            return ('Ínvalid input')  # to correct

    def list_people(self):

        headers = ['ID', 'Name', 'Gender', 'Role', 'Needs Accommodation']

        list_of_people = sorted(
            Amity.person, key=itemgetter('person_id'))

        print(tabulate([item.values() for item in list_of_people],
                       headers=headers, tablefmt='fancy_grid'))

    def delete_person(self, person_to_delete):

        found_matches = Amity.search_person(self, person_to_delete)

        if isinstance(found_matches, list) and len(found_matches) > 1:
            return ('There is more than one person with the name {0}. Please view the list of all people and use their ID instead'.format(
                person_to_reallocate.title()))

        elif isinstance(found_matches, list) and len(found_matches) == 1:

            found_matches = found_matches[0]

            person_index_to_delete = found_matches['index']
            person_id_to_delete = found_matches['details']['person_id']
            person_role_to_delete = found_matches['details']['role']
            person_name_to_delete = found_matches['details']['person_name']

            found_allocations = [{'index': index, 'room_id': Amity.allocation[index]['room_id']} for index in range(len(
                Amity.allocation)) if Amity.allocation[index]['person_id'] == person_id_to_delete]

            # Update the current room occupancy by -1
            office_ids = [Amity.office[index]['room_id']
                          for index in range(len(Amity.office))]
            space_ids = [Amity.space[index]['room_id']
                         for index in range(len(Amity.space))]

            if found_allocations:
                # UPDATE the occupancy for OFFICE person was allocated
                prev_allocated_office = [found_allocations[index] for index in range(
                    len(found_allocations)) if found_allocations[index]['room_id'] in office_ids]

                if prev_allocated_office:
                    prev_allocated_office_index = prev_allocated_office[0]['index']
                    prev_allocated_office_id = prev_allocated_office[0]['room_id']

                    prev_office = [{'index': index, 'details': Amity.office[index]} for index in range(
                        len(Amity.office)) if Amity.office[index]['room_id'] == prev_allocated_office_id][0]

                    prev_office_index = prev_office['index']
                    Amity.office[prev_office_index]['occupancy'] -= 1

                # UPDATE the occupancy for LIVING SPACE person was allocated
                prev_allocated_space = [found_allocations[index] for index in range(
                    len(found_allocations)) if found_allocations[index]['room_id'] in space_ids]

                if prev_allocated_space:
                    prev_allocated_space_index = prev_allocated_space[0]['index']
                    prev_allocated_space_id = prev_allocated_space[0]['room_id']

                    prev_space = [{'index': index, 'details': Amity.space[index]} for index in range(
                        len(Amity.space)) if Amity.space[index]['room_id'] == prev_allocated_space_id][0]

                    prev_space_index = prev_space['index']
                    Amity.space[prev_space_index]['occupancy'] -= 1

                Amity.room = Amity.office + Amity.space

                # Delete the allocations for that person
                found_allocations_index = [item['index']
                                           for item in found_allocations]

                Amity.allocation = [Amity.allocation[index] for index in range(
                    len(Amity.allocation)) if index not in found_allocations_index]

            # Delete the person in the specific dictionary
            if person_role_to_delete == 'Staff':
                index_in_staff_dict = [index for index in range(
                    len(Amity.staff)) if Amity.staff[index]['person_id'] == person_id_to_delete][0]
                del Amity.staff[index_in_staff_dict]

            elif person_role_to_delete == 'Fellow':
                index_in_fellow_dict = [index for index in range(
                    len(Amity.fellow)) if Amity.fellow[index]['person_id'] == person_id_to_delete][0]
                del Amity.fellow[index_in_fellow_dict]

            else:
                return ('IS  NEITHER STAFF NOR FELLOW\n')

            Amity.person = Amity.fellow + Amity.staff

            # Check if delete is successful
            found_matches = Amity.search_person(self, person_to_delete)
            if isinstance(found_matches, str):
                return ('{} has been deleted successfully'.format(person_name_to_delete))
            else:
                return ('{} has NOT been deleted'.format(person_name_to_delete))

        else:
            return (found_matches)

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

        fellows_need_accommodation2 = [person_details for person_details in
                                       Amity.person if person_details['wants_accommodation'] == 'Y']

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
                                      'Unallocated':'Office'} for index in range(len(Amity.person)) if Amity.person[index]['person_id'] in not_allocated_office_id]

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

                    print ('\nSee {0} for output'.format(file_path))
                    return ('Data saved to file')

    def print_allocations(self, allocation_output_file=''):

        if not Amity.allocation:
            return ('No allocations available')
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

                print ('See {0} for output'.format(file_path))
                return ('Data saved to file')

    def save_state(self, db_name=''):

        all_people = [tuple(people.values()) for people in Amity.person]
        all_rooms = [tuple(rooms.values()) for rooms in Amity.room]
        all_allocations = [tuple(allocations.values())
                           for allocations in Amity.allocation]

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
            return ('Data saved to DB')

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

        before_person_count = len(Amity.person)
        before_room_count = len(Amity.room)
        before_allocation_count = len(Amity.allocation)

        # Default DB
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
                person_id = row[0]
                person_name = row[1]
                person_gender = row[2]
                role = row[3]
                wants_accommodation = row[4]
                Amity.staff.append({'person_id': person_id, 'person_name': person_name, 'person_gender': person_gender,
                                    'role': role, 'wants_accommodation': wants_accommodation})

            cur.execute(query_fellow)
            rows = cur.fetchall()
            for row in rows:
                person_id = row[0]
                person_name = row[1]
                person_gender = row[2]
                role = row[3]
                wants_accommodation = row[4]
                Amity.fellow.append({'person_id': person_id, 'person_name': person_name, 'person_gender': person_gender,
                                     'role': role, 'wants_accommodation': wants_accommodation})

            Amity.person = Amity.fellow + Amity.staff

            cur.execute(query_space)
            rows = cur.fetchall()
            for row in rows:
                room_id = row[0]
                room_name = row[1]
                room_type = row[2]
                max_no = row[3]
                room_gender = row[4]
                occupancy = row[5]
                Amity.space.append({'room_id': room_id, 'room_name': room_name, 'room_type': room_type,
                                    'max_no': max_no, 'room_gender': room_gender, 'occupancy': occupancy})

            cur.execute(query_office)
            rows = cur.fetchall()
            for row in rows:
                room_id = row[0]
                room_name = row[1]
                room_type = row[2]
                max_no = row[3]
                room_gender = row[4]
                occupancy = row[5]
                Amity.office.append({'room_id': room_id, 'room_name': room_name, 'room_type': room_type,
                                     'max_no': max_no, 'room_gender': room_gender, 'occupancy': occupancy})

            Amity.room = Amity.office + Amity.space

            cur.execute(query_allocations)
            rows = cur.fetchall()
            for row in rows:
                person_id = row[0]
                room_id = row[1]

                Amity.allocation.append(
                    {'person_id': person_id, 'room_id': room_id})

            after_person_count = len(Amity.person)
            after_room_count = len(Amity.room)
            after_allocation_count = len(Amity.allocation)

            if before_person_count >= after_person_count or before_room_count >= after_room_count or before_allocation_count >= after_allocation_count:
                return 'All data has not been loaded'
            else:
                return ('Data loaded successfully! Use the list functions to view the data')

        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()

            raise Exception(error)
            sys.exit(1)

        # Release the resources
        finally:
            if conn is not None:
                conn.close()
