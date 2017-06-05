import os
import os.path
import random
import re
import string

from colorama import *
from operator import itemgetter
from sqlalchemy import create_engine, exc
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from tabulate import tabulate
from termcolor import colored, cprint

from models.person import Staff, Fellow
from models.room import LivingSpace, Office
from models.models import Base, Allocations, Employees, Rooms
from settings import CP1_DIR


class Amity(object):
    office = []
    space = []
    room = []

    staff = []
    fellow = []
    person = []

    allocation = []

    def create_room(self, room_type, room_gender, *rooms_to_add):
        """create as many rooms as possible by specifying multiple room name"""

        prev_no_of_rooms = len(Amity.room)

        room_type = room_type.strip().lower()
        room_gender = room_gender.strip().upper()

        if room_gender == '':
            room_gender = 'N'

        if room_gender.title() not in ('Male', 'Female', 'M', 'F', 'N'):
            return colored(
                'Use Male or Female to specify gender that will occupy room', 'red')

        else:
            if rooms_to_add:
                Amity.room = Amity.office + Amity.space

                # Generate unique ID for rooms
                if Amity.room:
                    new_room_id = max([rooms['room_id']
                                       for rooms in Amity.room]) + 1
                else:
                    new_room_id = 1

                # Check if the room_name exists
                pattern = re.compile(
                    r"[\d{}]+".format(re.escape(string.punctuation)))
                invalid_name = [name for name in rooms_to_add[0]
                                if pattern.search(name) or re.search('\d', name)]
                if invalid_name:
                    return colored('A room name cannot contain numbers or special characters: {}'.format(', '.join(invalid_name)), 'red')

                for room_name in rooms_to_add[0]:
                    room_name = room_name.strip().title()
                    found_matches = Amity.search_room(self, room_name)

                    if isinstance(found_matches, dict) and found_matches:
                        return colored('Room already exists', 'red')

                    else:
                        if room_type not in ['office', 'space', 'living space']:
                            return colored('A room can either be an OFFICE or a LIVING SPACE', 'red')

                        elif room_type == 'office':
                            if room_gender != 'N':
                                return colored(
                                    'An office can be occupied by both male and female', 'red')
                            else:
                                new_office = Office(room_name)

                                Amity.office.append({'room_id': new_room_id,
                                                     'room_name': new_office.room_name.title(),
                                                     'room_type': new_office.room_type.lower(),
                                                     'capacity': new_office.capacity,
                                                     'room_gender': new_office.room_gender.upper(),
                                                     'occupancy': new_office.occupancy})

                                cprint('{0} added successfully with ID {1}'.format(
                                    new_office.room_name, new_room_id), 'green')

                        elif room_type == 'space' or room_type == 'living space':
                            if room_gender == 'N':
                                return colored(
                                    'Please specify if the living space is for male or female', 'red')
                            else:
                                new_space = LivingSpace(room_name, room_gender)

                                Amity.space.append({'room_id': new_room_id,
                                                    'room_name': new_space.room_name.title(),
                                                    'room_type': new_space.room_type.lower(),
                                                    'capacity': new_space.capacity,
                                                    'room_gender': new_space.room_gender.upper(),
                                                    'occupancy': new_space.occupancy})

                                cprint('{0} added successfully with ID {1}'.format(
                                    new_space.room_name, new_room_id), 'green')

                        else:
                            print ('ROOM TYPE WITH WRONG FORMAT')

                        new_room_id += 1

            else:
                return colored('No rooms to add', 'yellow')

        Amity.room = Amity.office + Amity.space

        if len(Amity.room) - prev_no_of_rooms != len(rooms_to_add[0]):
            return colored('Rooms not added', 'red')
        else:
            return colored('{} rooms added successfully'.format(len(rooms_to_add[0])), 'green')

    def search_room(self, room_to_search):
        """Search if a room exists using the room name or room ID"""
        dict_to_search = Amity.room

        if isinstance(room_to_search, int) or isinstance(room_to_search, str):
            room_to_search = str(room_to_search)
            room_to_search = room_to_search.strip().title()

            reg_str = re.compile(
                r'\b' + re.escape(room_to_search) + r'\b')

            found_matches = [{'index': index, 'details': value}
                             for index, value in enumerate(dict_to_search)
                             if reg_str.search(str(value['room_id']))
                             or reg_str.search(value['room_name'])]

            if not found_matches:
                return colored("No entry found for room with ID or name {0}".format(
                    room_to_search.title()), 'yellow')
            else:
                return found_matches[0]

        else:
            return colored('Invalid input', 'red')

    def list_rooms(self):
        """List the details of all rooms created or loaded from DB"""

        headers = ['Room ID', 'Room Name', 'Room Type',
                   'Capacity', 'Room Gender', 'Current Occupancy']

        list_of_rooms = sorted(
            Amity.room, key=itemgetter('room_id'))

        if not list_of_rooms:
            cprint('No rooms to list. Create them first', 'yellow')
        else:
            cprint(tabulate([item.values() for item in list_of_rooms],
                            headers=headers, tablefmt='fancy_grid'), 'cyan')

    def delete_room(self, room_to_delete):
        """Delete a room and allocations to the room"""
        found_matches = Amity.search_room(self, room_to_delete)

        if isinstance(found_matches, dict) and found_matches:
            room_id_to_delete = found_matches['details']['room_id']
            room_type_to_delete = found_matches['details']['room_type']
            room_name_to_delete = found_matches['details']['room_name']

            # Delete allocations for room
            found_allocations = [index for index, allocations in enumerate(
                Amity.allocation) if allocations['room_id'] == room_id_to_delete]

            Amity.allocation = [allocations for index, allocations in enumerate(
                Amity.allocation) if index not in found_allocations]

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
                return colored('{} has been deleted successfully'.format(
                    room_name_to_delete), 'green')
            else:
                return colored('{} has NOT deleted'.format(room_name_to_delete), 'red')

        else:
            return (found_matches)

    def add_person(self, person_name, person_gender, role, wants_accommodation='N'):
        """Adds a person to the system and allocates the person to a random room"""
        prev_no_of_people = len(Amity.person)

        person_name = str(person_name).strip().title()
        person_gender = str(person_gender).strip().upper()
        role = str(role).strip().title()
        wants_accommodation = str(wants_accommodation).strip().upper()

        pattern = re.compile(r"[\d{}]+".format(re.escape(string.punctuation)))
        invalid_name = [name for name in person_name if pattern.search(
            name) or re.search('\d', name)]
        if invalid_name:
            return colored("Person's name, {}, cannot contain numbers or special characters".format(person_name), 'red')

        if role.title() not in ['Staff', 'Fellow']:
            return colored(
                'A person can either have the role STAFF or FELLOW', 'red')

        if person_gender[0].upper() not in ('M', 'F'):
            return colored('Use Male, M, Female, F to specify gender', 'red')
        else:
            person_gender = person_gender[0].upper()

        if not wants_accommodation:
            wants_accommodation = 'N'
        else:
            if wants_accommodation[0].upper() not in ('Y', 'N'):
                return colored(
                    'Use Yes, Y, No, N to specify if a person wants accommodation or not', 'red')

        # Check if person already exists before adding them
        found_people = Amity.search_person(self, person_name)

        if found_people and isinstance(found_people, list):
            return colored('{} already exists. Add an initial to differentiate the names'.format(
                person_name), 'red')

        else:
            Amity.person = Amity.fellow + Amity.staff

            # Generate unique ID for rooms
            if Amity.person:
                new_person_id = max([persons['person_id']
                                     for persons in Amity.person]) + 1
            else:
                new_person_id = 100

            if role == 'Staff':
                if wants_accommodation != 'N':
                    return colored('Staff cannot be allocated living spaces', 'red')
                else:
                    new_staff = Staff(person_name, person_gender)

                    Amity.staff.append({'person_id': new_person_id,
                                        'person_name': new_staff.person_name,
                                        'person_gender': new_staff.person_gender,
                                        'role': new_staff.role.title(),
                                        'wants_accommodation': wants_accommodation})

                    cprint('\n{0} added successfully with ID {1}'.format(
                        new_staff.person_name, new_person_id), 'green')

                    # Allocate Office and Living Space
                    Amity.allocate_room(self, new_person_id)

            elif role == 'Fellow':
                new_fellow = Fellow(person_name, person_gender,
                                    wants_accommodation)

                Amity.fellow.append({'person_id': new_person_id,
                                     'person_name': new_fellow.person_name,
                                     'person_gender': new_fellow.person_gender,
                                     'role': new_fellow.role.title(),
                                     'wants_accommodation': new_fellow.wants_accommodation})

                cprint('\n{0} added successfully with ID {1}'.format(
                    new_fellow.person_name, new_person_id), 'green')

                # Allocate Office and Living Space
                Amity.allocate_room(self, new_person_id)

            Amity.person = Amity.fellow + Amity.staff

            if len(Amity.person) - prev_no_of_people != 1:
                return colored('Person not added!', 'red')

            else:
                # Check a person has been allocated rooms
                found_allocations = [
                    allocations for allocations in Amity.allocation if allocations['person_id'] == new_person_id]
                if found_allocations:
                    return colored('Person added and allocated room', 'green')
                else:
                    return colored('Person added but not allocated (all) rooms', 'yellow')

    def allocate_room(self, person_id_to_allocate):
        """Allocates person to an office and living space"""

        Amity.person = Amity.fellow + Amity.staff

        person_details = [
            person_details for person_details in Amity.person if person_details['person_id'] == person_id_to_allocate][0]

        person_name = person_details['person_name']
        person_gender = person_details['person_gender'].upper()
        wants_accommodation = person_details['wants_accommodation']

        found_allocations = [{'index': index, 'room_id': value['room_id']}
                             for index, value in enumerate(Amity.allocation)
                             if value['person_id'] == person_id_to_allocate]

        found_room = [rooms['room_id'] for rooms in found_allocations]

        all_offices = [office_details['room_id']
                       for office_details in Amity.office]
        all_spaces = [space_details['room_id']
                      for space_details in Amity.space]

        if found_allocations and (set(found_room) & set(all_offices)):
            msg = 'Person already allocated office'

        else:
            # Check for available office then randomly select an office to
            # allocate
            available_office_list = [{'index': index, 'room_id': offices['room_id']} for index, offices in enumerate(Amity.office)
                                     if offices['capacity'] > offices['occupancy']]

            if not available_office_list or not Amity.office:
                cprint('No offices to allocate', 'yellow')
            else:
                # Allocate office
                office_to_allocate = random.choice(available_office_list)
                Amity.allocation.append(
                    {'person_id': person_id_to_allocate, 'room_id': office_to_allocate['room_id']})

                cprint('\n{} has been allocated to office'.format(
                    person_name), 'green')

                # Update the number of the randomly selected office occupants
                prev_occupancy = Amity.office[office_to_allocate['index']]['occupancy']
                new_occupancy = prev_occupancy + 1

                Amity.office[office_to_allocate['index']
                             ]['occupancy'] = new_occupancy

        # Allocate living space
        if found_allocations and (set(found_room) & set(all_spaces)):
            msg = 'Person already allocated living space'

        else:
            if wants_accommodation == 'Y':
                if not Amity.space:
                    cprint('No living spaces to allocate', 'yellow')

                else:
                    # Check for available living spaces then randomly select a
                    # space to allocate
                    available_male_spaces = [{'index': index, 'room_id': spaces['room_id']}
                                             for index, spaces in enumerate(Amity.space)
                                             if spaces['room_gender'].upper() == 'M' and
                                             spaces['capacity'] > spaces['occupancy']]

                    available_female_spaces = [{'index': index, 'room_id': spaces['room_id']}
                                               for index, spaces in enumerate(Amity.space)
                                               if spaces['room_gender'].upper() == 'F' and
                                               spaces['capacity'] > spaces['occupancy']]

                    # Allocate living space
                    if (available_male_spaces or available_female_spaces):
                        if person_gender == 'M':
                            if not available_male_spaces:
                                cprint(
                                    'No available male living spaces to allocate', 'yellow')
                            else:
                                space_to_allocate = random.choice(
                                    available_male_spaces)

                                # Add the new allocation to the allocation
                                # dictionary
                                Amity.allocation.append(
                                    {'person_id': person_id_to_allocate, 'room_id': space_to_allocate['room_id']})

                                cprint(
                                    '\n{} has been allocated to Living Space'.format(person_name), 'green')

                                # Update the number of the randomly selected living
                                # space occupants
                                prev_occupancy = Amity.space[space_to_allocate['index']
                                                             ]['occupancy']
                                new_occupancy = prev_occupancy + 1
                                Amity.space[space_to_allocate['index']
                                            ]['occupancy'] = new_occupancy

                        elif person_gender == 'F':
                            if not available_female_spaces:
                                cprint(
                                    'No available female living spaces to allocate', 'yellow')
                            else:
                                space_to_allocate = random.choice(
                                    available_female_spaces)

                                # Add the new allocation to the allocation
                                # dictionary
                                Amity.allocation.append(
                                    {'person_id': person_id_to_allocate, 'room_id': space_to_allocate['room_id']})

                                cprint(
                                    '{} has been allocated to Living Space'.format(person_name), 'green')

                                # Update the number of the randomly selected living space
                                # occupants
                                prev_occupancy = Amity.space[space_to_allocate['index']
                                                             ]['occupancy']
                                new_occupancy = prev_occupancy + 1
                                Amity.space[space_to_allocate['index']
                                            ]['occupancy'] = new_occupancy

        Amity.room = Amity.office + Amity.space

    def allocate_unallocated(self, person_to_alocate=''):
        # Check if the person exists

        if not Amity.room:
            return colored('No existing rooms', 'yellow')

        else:
            if person_to_alocate != '':
                found_people = Amity.search_person(self, person_to_alocate)

                if isinstance(found_people, list) and len(found_people) > 1:
                    return colored('There is more than one person with the name {0}.\
                            Please view the list of all people and use their ID instead'.format(person_to_alocate.title()), 'yellow')

                elif isinstance(found_people, list) and len(found_people) == 1:
                    found_people = found_people[0]
                    person_id = found_people['details']['person_id']
                    Amity.allocate_room(self, person_id)

                else:
                    return (found_people)

            else:
                unallocated_persons = Amity.find_unallocated(self)

                if not unallocated_persons:
                    return colored('No pending allocations\n', 'yellow')

                elif isinstance(unallocated_persons, list):
                    # If there are unallocated people, allocate them to a
                    # random room
                    for people in unallocated_persons:
                        person_id = people['person_id']
                        Amity.allocate_room(self, person_id)

    def reallocate_person(self, person_to_reallocate, room_to_allocate):
        """Reallocate a person with an existing allocation to another room"""

        # Check if the person exists
        found_people = Amity.search_person(self, person_to_reallocate)

        if isinstance(found_people, list) and len(found_people) > 1:
            return colored('There is more than one person with the name {0}.\
                    Please view the list of all people and use their ID instead'.format(person_to_reallocate.title()), 'yellow')

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

                available_room_list = [{'index': index, 'room_id': rooms['room_id']}
                                       for index, rooms in enumerate(Amity.room)
                                       if rooms['capacity'] > rooms['occupancy']]

                available_rooms_ids = [rooms['room_id']
                                       for rooms in available_room_list]

                if room_id_to_reallocate not in available_rooms_ids:
                    return colored('{0} is not available'.format(new_room_name), 'red')

                else:
                    person_id_to_reallocate = found_people['details']['person_id']
                    person_name = found_people['details']['person_name']
                    person_gender = found_people['details']['person_gender']
                    role = found_people['details']['role']

                    found_allocations = [{'index': index, 'room_id': allocations['room_id']}
                                         for index, allocations in enumerate(Amity.allocation)
                                         if allocations['person_id'] == person_id_to_reallocate]

                    if not found_allocations:
                        return colored(
                            'No allocations available for {0}'.format(person_name), 'yellow')

                    else:
                        if new_room_type == 'office':

                            new_office_index = [index for index, offices in enumerate(Amity.office)
                                                if offices['room_id'] == room_id_to_reallocate][0]

                            office_ids = [offices['room_id']
                                          for offices in Amity.office]

                            prev_allocated_office = [allocations for allocations in found_allocations
                                                     if allocations['room_id'] in office_ids]

                            if not prev_allocated_office:
                                return colored('No {0} allocations available for {1}'.format(new_room_type, person_name), 'yellow')

                            else:
                                prev_allocated_office_index = prev_allocated_office[0]['index']
                                prev_allocated_office_id = prev_allocated_office[0]['room_id']

                                prev_office = [{'index': index, 'details': Amity.office[index]} for index in range(
                                    len(Amity.office)) if Amity.office[index]['room_id'] == prev_allocated_office_id][0]

                                prev_room_name = prev_office['details']['room_name']
                                prev_room_index = prev_office['index']

                                # Reallocate office
                                if prev_allocated_office_id == room_id_to_reallocate:
                                    return colored('{0} is already allocated to {1}'.format(
                                        person_name, prev_room_name), 'yellow')

                                else:
                                    Amity.allocation[prev_allocated_office_index] = {
                                        'person_id': person_id_to_reallocate, 'room_id': room_id_to_reallocate}

                                    # Update the occupancy
                                    Amity.office[prev_room_index]['occupancy'] -= 1
                                    Amity.office[new_office_index]['occupancy'] += 1

                                    return colored('{0} has been reallocated office from {1} to {2}'.format(
                                        person_name, prev_room_name, new_room_name), 'green')

                        elif new_room_type == 'space':
                            space_ids = [Amity.space[index]['room_id']
                                         for index in range(len(Amity.space))]

                            space_ids = [spaces['room_id']
                                         for spaces in Amity.space]

                            new_space_index = [index for index, spaces in enumerate(Amity.space)
                                               if spaces['room_id'] == room_id_to_reallocate][0]

                            prev_allocated_space = [allocations for allocations in found_allocations
                                                    if allocations['room_id'] in space_ids]

                            if role == 'Staff':
                                return colored(
                                    'Staff cannot be allocated living spaces', 'red')

                            else:
                                if new_room_gender != person_gender:
                                    return colored('A person of gender {0} is being allocated to a living space for {1}'.format(
                                        person_gender, new_room_gender), 'red')

                                else:
                                    if not prev_allocated_space:
                                        return colored('No {0} allocations available for {1}'.format(new_room_type, person_name), 'yellow')

                                    else:
                                        prev_allocated_space_index = prev_allocated_space[0]['index']
                                        prev_allocated_space_id = prev_allocated_space[0]['room_id']

                                        prev_space = [{'index': index, 'details': spaces}
                                                      for index, spaces in enumerate(Amity.space)
                                                      if spaces['room_id'] == prev_allocated_space_id][0]

                                        prev_room_name = prev_space['details']['room_name']
                                        prev_room_index = prev_space['index']

                                        # Reallocate space
                                        if prev_allocated_space_id == room_id_to_reallocate:
                                            return colored('{0} is already allocated to {1}'.format(
                                                person_name, prev_room_name), 'green')

                                        else:
                                            Amity.allocation[prev_allocated_space_index] = {
                                                'person_id': person_id_to_reallocate, 'room_id': room_id_to_reallocate}

                                            # Update the occupancy
                                            Amity.space[prev_room_index]['occupancy'] -= 1
                                            Amity.space[new_space_index]['occupancy'] += 1

                                            return colored('{0} has been reallocated living space from {1} to {2}'.format(
                                                person_name, prev_room_name, new_room_name), 'green')

                        Amity.room = Amity.office + Amity.space

            else:
                return colored(found_rooms, 'yellow')

        else:
            return colored(found_people, 'yellow')

    def load_people(self):
        """Adds people to rooms from a txt file"""

        text_file = os.path.join(CP1_DIR, 'person.txt')

        prev_no_of_people = len(Amity.person)

        if os.path.isfile(text_file):
            with open(text_file, "r") as myfile:
                people = myfile.readlines()

            if not people:
                cprint('The file is empty', 'red')
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
                return colored('People not loaded!', 'red')
            else:
                return colored('{} people loaded!'.format(len(people)), 'green')

        else:
            raise FileNotFoundError('File does not exist')

    def search_person(self, person_to_search):
        """Search if a person exists using the person name or person ID"""

        if isinstance(person_to_search, int) or isinstance(person_to_search, str):
            person_to_search = str(person_to_search)
            person_to_search = person_to_search.strip().title()

            reg_str = re.compile(
                r'\b' + re.escape(person_to_search) + r'\b')

            found_matches = [{'index': index, 'details': people}
                             for index, people in enumerate(Amity.person)
                             if reg_str.search(str(people['person_id'])) or
                             (reg_str.search(people['person_name']) and people['person_name'] == person_to_search)]

            if not found_matches:
                return colored("No entry found for person with ID or name {0}".format(
                    person_to_search.title()), 'yellow')
            else:
                return found_matches

        else:
            return colored('Invalid input', 'red')

    def list_people(self):
        """List the details of all people created or loaded from DB"""

        headers = ['ID', 'Name', 'Gender', 'Role', 'Needs Accommodation']

        list_of_people = sorted(
            Amity.person, key=itemgetter('person_id'))

        if not list_of_people:
            cprint('No people to list. Create or load first', 'yellow')

        else:
            cprint(tabulate([item.values() for item in list_of_people],
                            headers=headers, tablefmt='fancy_grid'), 'cyan')

    def delete_person(self, person_to_delete):
        """Delete a person and allocations for the person"""

        found_matches = Amity.search_person(self, person_to_delete)

        if isinstance(found_matches, list) and len(found_matches) > 1:
            return colored('There is more than one person with the name {0}.\
            Please view the list of all people and use their ID instead'.format(person_to_delete.title()), 'yellow')

        elif isinstance(found_matches, list) and len(found_matches) == 1:

            found_matches = found_matches[0]

            person_id_to_delete = found_matches['details']['person_id']
            person_role_to_delete = found_matches['details']['role']
            person_name_to_delete = found_matches['details']['person_name']

            found_allocations = [{'index': index, 'room_id': value['room_id']}
                                 for index, value in enumerate(Amity.allocation)
                                 if value['person_id'] == person_id_to_delete]

            # Update the current room occupancy by -1
            office_ids = [offices['room_id'] for offices in Amity.office]
            space_ids = [spaces['room_id'] for spaces in Amity.space]

            if found_allocations:
                # UPDATE the occupancy for OFFICE person was allocated

                prev_allocated_office = [allocation_details for allocation_details in found_allocations
                                         if allocation_details['room_id'] in office_ids]

                if prev_allocated_office:
                    prev_allocated_office_id = prev_allocated_office[0]['room_id']

                    prev_office = [{'index': index, 'details': value}
                                   for index, value in enumerate(Amity.office)
                                   if value['room_id'] == prev_allocated_office_id][0]

                    prev_office_index = prev_office['index']
                    Amity.office[prev_office_index]['occupancy'] -= 1

                # UPDATE the occupancy for LIVING SPACE person was allocated
                prev_allocated_space = [allocation_details for allocation_details in found_allocations
                                        if allocation_details['room_id'] in space_ids]

                if prev_allocated_space:
                    prev_allocated_space_id = prev_allocated_space[0]['room_id']

                    prev_space = [{'index': index, 'details': spaces}
                                  for index, spaces in enumerate(Amity.space)
                                  if spaces['room_id'] == prev_allocated_space_id][0]

                    prev_space_index = prev_space['index']
                    Amity.space[prev_space_index]['occupancy'] -= 1

                Amity.room = Amity.office + Amity.space

                # Delete the allocations for that person
                found_allocations_index = [item['index']
                                           for item in found_allocations]

                Amity.allocation = [allocations for index, allocations in enumerate(Amity.allocation)
                                    if index not in found_allocations_index]

            # Delete the person in the specific dictionary
            if person_role_to_delete == 'Staff':
                index_in_staff_dict = [index for index, people in enumerate(
                    Amity.staff) if people['person_id'] == person_id_to_delete][0]
                del Amity.staff[index_in_staff_dict]

            elif person_role_to_delete == 'Fellow':

                index_in_fellow_dict = [index for index, people in enumerate(
                    Amity.fellow) if people['person_id'] == person_id_to_delete][0]
                del Amity.fellow[index_in_fellow_dict]

            else:
                return ('IS  NEITHER STAFF NOR FELLOW\n')

            Amity.person = Amity.fellow + Amity.staff

            # Check if delete == successful
            found_matches = Amity.search_person(self, person_to_delete)
            if isinstance(found_matches, str):
                return colored('{} has been deleted successfully'.format(person_name_to_delete), 'green')
            else:
                return colored('{} has NOT been deleted'.format(person_name_to_delete), 'red')

        else:
            return (found_matches)

    def print_room(self, room_to_print):
        """Prints the names of all the people in  room_name  on the screen"""

        # First check if the room exists
        found_rooms = Amity.search_room(self, room_to_print)

        if isinstance(found_rooms, dict) and found_rooms:
            room_id = found_rooms['details']['room_id']
            room_name = found_rooms['details']['room_name']

            found_allocations = [allocations['room_id'] for allocations in Amity.allocation
                                 if allocations['room_id'] == room_id]

            if not found_allocations:
                return colored('There are no allocations for {0}'.format(room_name), 'yellow')
            else:
                persons_in_room = [allocations['person_id']
                                   for allocations in Amity.allocation
                                   if allocations['room_id'] == room_id]

                person_name = sorted(
                    [people['person_name'] for people in Amity.person if people['person_id'] in persons_in_room])

                headers = ['Person Name']
                cprint(tabulate([[name] for name in person_name],
                                headers=headers, tablefmt='fancy_grid'), 'cyan')

                return (person_name)

        else:
            cprint(found_rooms, 'red')

    def find_unallocated(self):
        """Finds all unallocated people"""

        # Find peeoplw not allocated living space
        living_spaces_list = [spaces['room_id'] for spaces in Amity.space]

        fellows_need_accommodation = [people['person_id'] for people in Amity.person
                                      if people['wants_accommodation'] == 'Y']

        fellows_allocated_living_space = [allocations['person_id'] for allocations in Amity.allocation
                                          if allocations['room_id'] in living_spaces_list]

        fellows_ids_not_allocated_space = list(
            set(fellows_need_accommodation) - set(fellows_allocated_living_space))

        fellows_not_allocated_space = [{'person_id': people['person_id'],
                                        'person_name':people['person_name'],
                                        'Unallocated':'Living Space'}
                                       for people in Amity.person
                                       if people['person_id'] in fellows_ids_not_allocated_space]

        # Find people who have no office allocated
        office_list = [offices['room_id'] for offices in Amity.office]
        all_people = [people['person_id'] for people in Amity.person]

        people_allocated_office = [allocations['person_id'] for allocations in Amity.allocation
                                   if allocations['room_id'] in office_list]

        people_ids_not_allocated_office = list(
            set(all_people) - set(people_allocated_office))

        # People not allocated both office and living space
        unallocated_both_office_and_space = list(
            set(fellows_ids_not_allocated_space) & set(people_ids_not_allocated_office))

        # List of IDs of all unallocated persons
        people_ids_unallocated = list(
            set(fellows_ids_not_allocated_space + people_ids_not_allocated_office))

        for index in range(len(people_ids_unallocated)):
            if people_ids_unallocated[index] in unallocated_both_office_and_space:
                position = [position for position in range(len(fellows_not_allocated_space))
                            if people_ids_unallocated[index] == fellows_not_allocated_space[position]['person_id']][0]
                fellows_not_allocated_space[position]['Unallocated'] = 'Office, Living Space'

        # List of people without only office allocation
        not_allocated_office_id = list(
            set(people_ids_not_allocated_office) - set(unallocated_both_office_and_space))
        people_unallocated_office = [{'person_id': people['person_id'],
                                      'person_name':people['person_name'],
                                      'Unallocated':'Office'}
                                     for people in Amity.person
                                     if people['person_id'] in not_allocated_office_id]

        # List with details of pending allocations
        people_unallocated = fellows_not_allocated_space + people_unallocated_office
        people_unallocated = sorted(
            people_unallocated, key=itemgetter('person_name'))

        return (people_unallocated)

    def print_unallocated(self, unallocated_persons_file=''):
        """Prints a list of unallocated people to the screen and outputs the information to the txt file provided"""

        people_unallocated = Amity.find_unallocated(self)

        if not people_unallocated:
            cprint('All people have been allocated rooms', 'yellow')
        else:
            headers = ['ID', 'Person Name', 'Pending Allocation']
            cprint(tabulate([item.values() for item in people_unallocated],
                            headers=headers, tablefmt='fancy_grid'), 'cyan')

            if unallocated_persons_file != '':
                # Ensure that the file is created in the folder containing the
                # project
                if re.search(r'[a-zA-Z0-9]+\.[a-z]+', unallocated_persons_file):
                    file_path = os.path.join(
                        CP1_DIR, unallocated_persons_file)
                else:
                    file_path = os.path.join(
                        CP1_DIR, unallocated_persons_file + '.txt')

                with open(file_path, 'w') as output_file:
                    for details in people_unallocated:
                        output_file.write(
                            str(details['person_id']) + '\t' + details['person_name'] + '\t' + details['Unallocated'] + '\n')

                    cprint('\nSee {0} for output'.format(file_path), 'green')

    def print_allocations(self, allocation_output_file=''):
        """Prints a list of allocations onto the screen and outputs the registered allocations to a txt file"""

        if not Amity.allocation:
            cprint('No allocations available', 'yellow')
        else:
            allocated_rooms = list(
                set([item['room_id'] for item in Amity.allocation]))

            if allocation_output_file == '':
                file_path = os.path.join(CP1_DIR, 'allocation.txt')
            elif re.search(r'[a-zA-Z0-9]+\.[a-z]+', allocation_output_file):
                file_path = os.path.join(CP1_DIR, allocation_output_file)
            else:
                file_path = os.path.join(
                    CP1_DIR, allocation_output_file + '.txt')

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

                    cprint(room_info['room_name'] + '\n' + '------------------------------' +
                           '\n' + ', '.join(sorted(name_of_people_in_room)) + '\n\n', 'cyan')

                cprint('See {0} for output'.format(file_path), 'green')
                return ('Data saved to file')

    def save_state(self, db_name=''):
        """Persists all the data stored in the app to a Postgres database. Specifying the DB explicitly stores the data in the DB specified"""

        if db_name == '':
            db_name = 'amity.db'

        if not re.search(r'[a-zA-Z0-9]+\.db', db_name):
            db_name = db_name + '.db'

        if not Amity.room and not Amity.person:
            return colored('No session data available\n', 'yellow')

        try:
            # Create an engine that stores data in the local directory's
            # sqlalchemy_example.db file.
            sqlite_db = {'drivername': 'sqlite', 'database': db_name}
            db_url = URL(**sqlite_db)
            engine = create_engine(db_url)

            # Drop all tables if exist
            Base.metadata.drop_all(engine)

            # Create all tables in the engine statements in raw SQL
            Base.metadata.create_all(engine)

            # Bind the engine to the metadata of the Base class so that the
            # declaratives can be accessed through a DBSession instance
            Base.metadata.bind = engine

            DBSession = sessionmaker(bind=engine)
            session = DBSession()

            # Insert a Person in the person table
            session.bulk_insert_mappings(Employees, Amity.person)
            session.bulk_insert_mappings(Rooms, Amity.room)
            session.bulk_insert_mappings(Allocations, Amity.allocation)
            session.commit()

            return colored('Session data successfully saved to DB named: {}'.format(db_name), 'green')

        except exc.SQLAlchemyError as error:
            return colored('Error: ', error, 'red')

    def load_state(self, db_name):
        """Loads data from a database into the application"""

        if not re.search(r'[a-zA-Z0-9]+\.db', db_name):
            db_name = db_name + '.db'

        file_path = os.path.join(CP1_DIR, db_name)

        if not os.path.isfile(file_path):
            return colored('Database does not exist', 'red')

        else:
            if not re.search(r'[a-zA-Z0-9]+\.db', db_name):
                db_name = db_name + '.db'

            engine = create_engine('sqlite:///' + db_name)

            Base.metadata.bind = engine
            DBSession = sessionmaker()
            DBSession.bind = engine

            session = DBSession()

            # Check if the database has the correct table
            table_names = ['Allocations', 'Employees', 'Rooms']
            conn = engine.connect()

            db_tables = []
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
                if row[0] in table_names:
                    db_tables.append(row[0])

            if not db_tables:
                return colored('Tables {} do not exist'.format(', '.join(table_names)), 'red')

            else:
                try:
                    # Count before load
                    before_person_count = len(Amity.person)
                    before_room_count = len(Amity.room)
                    before_allocation_count = len(Amity.allocation)

                    # Load Person data into app
                    result = session.query(Employees).all()
                    for row in result:
                        person_id = row.person_id
                        person_name = row.person_name
                        person_gender = row.person_gender
                        role = row.role
                        wants_accommodation = row.wants_accommodation
                        Amity.person.append({'person_id': person_id,
                                             'person_name': person_name,
                                             'person_gender': person_gender,
                                             'role': role,
                                             'wants_accommodation': wants_accommodation})

                    if Amity.person:
                        for people in Amity.person:
                            if people['role'] == 'Staff':
                                Amity.staff.append(people)
                            elif people['role'] == 'Fellow':
                                Amity.fellow.append(people)
                            else:
                                return ('Is neither staff nor fellow')

                    # Load Room data into app
                    result = session.query(Rooms).all()
                    for row in result:
                        room_id = row.room_id
                        room_name = row.room_name
                        room_type = row.room_type
                        capacity = row.capacity
                        room_gender = row.room_gender
                        occupancy = row.occupancy
                        Amity.room.append({'room_id': room_id,
                                           'room_name': room_name,
                                           'room_type': room_type,
                                           'capacity': capacity,
                                           'room_gender': room_gender,
                                           'occupancy': occupancy})

                    if Amity.room:
                        for rooms in Amity.room:
                            if rooms['room_type'] == 'office':
                                Amity.office.append(rooms)
                            elif rooms['room_type'] == 'space':
                                Amity.space.append(rooms)
                            else:
                                return ('Is neither office nor space')

                    # Load Allocations data into app
                    result = session.query(Allocations).all()
                    for row in result:
                        person_id = row.person_id
                        room_id = row.room_id
                        Amity.allocation.append(
                            {'person_id': person_id, 'room_id': room_id})

                    after_person_count = len(Amity.person)
                    after_room_count = len(Amity.room)
                    after_allocation_count = len(Amity.allocation)

                    if (before_person_count >= after_person_count) or (before_room_count >= after_room_count) or (before_allocation_count >= after_allocation_count):
                        return colored('Not all data has not been loaded! Check missing data using list functions', 'yellow')
                    else:
                        return colored('Data loaded successfully! Use the list functions to view the data', 'green')

                except SQLAlchemyError as error:
                    return colored('SQLAlchemyError: ', error, 'red')
