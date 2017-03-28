import re

from tabulate import tabulate

from person import Person, Staff, Fellow
from room import Room, LivingSpace, Office


class Amity(object):

    staff = {}
    fellow = {}
    person = {}

    person_id = 100

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

    def load_people(self, text_file):
    #(self, person_name, person_gender, role, wants_accommodation='N')
        with open ("person.txt", "r") as myfile:
            person_data = myfile.readlines()

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

            Amity.add_person(self, person_name, person_gender, role, wants_accommodation)
        

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

                    Amity.tabulate_room_output(self, list_of_found_matches)
                    return list_of_found_matches

            else:
                person_to_search = person_to_search.strip().title()

                reg_str = re.compile(
                    r'\b' + re.escape(person_to_search) + r'\b')

                found_matches = [key for key in people_dict.keys(
                ) if reg_str.search(people_dict[key][1])]
                if len(found_matches) == 0:
                    return ("No entry found for person with ID or name {0}".format(
                        person_to_search.title()))

                list_of_found_matches = {}

                for key in found_matches:
                    list_of_found_matches[key] = Amity.person[key]

                Amity.tabulate_room_output(self, list_of_found_matches)
                return list_of_found_matches

        else:
            raise TypeError('Ínvalid input')  # to correct

    def tabulate_room_output(self, found_matches):
        headers = ['ID', 'Name', 'Gender', 'Role', 'Needs Accommodation']

        print(tabulate([(k,) + tuple(v) for k, v in found_matches.items()],
                       headers=headers, tablefmt='fancy_grid'))

        # print (tabulate([found_matches[k] for k in sorted(
        #     found_matches, key=found_matches.get)], headers=headers, tablefmt='fancy_grid'))

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
            Amity.person.pop(dict_key, None)
            print ('Delete successful')

        else:
            print (found_matches)


#
a = Amity()
# john = a.add_person('John', 'M', 'guest')

# print(john)
jane = a.add_person('Jane', 'F', 'staFF', 'N')
maria = a.add_person('Maria', 'F', 'fellow')
luke = a.add_person('Luke', 'M', 'fellow')
mark = a.add_person('Mark', 'M', 'staFF', 'N')
joe = a.add_person('Joe', 'M', 'staFF', 'N')
joem = a.add_person('Joe Maina', 'M', 'fellow', 'Y')

# print ('-------------------------')
# print ("List of all persons created")
# print (a.person)
# print ('-------------------------', '\n\n')

print(a.search_person(a.person, 'joe'))


# a.change_person_role('Joe', 'staff')

# print ("After delete")
# print ((a.person))
# print ('-------------------------', '\n\n')

# a.delete_person('Joe')
# a.person[100]


# print("Printing change_person_role results",a.change_person_role(101))

# #print (a.john.pname, '\n')
# #print(john.pname, john.pgender, john.role, john.wants_accommodation)
# print("Staff:", a.staff.keys())
# print("Fellow", a.fellow.keys())
# print(a.person)


# a.load_people("person.txt")