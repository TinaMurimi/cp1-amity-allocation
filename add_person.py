from person import *
from room import *


class Amity(object):
    # add_person <person_name> <FELLOW|STAFF> [wants_accommodation]

    # super(Staff, self).__init__(pname, pgender, 'staff', 'N')

    staff = {}
    fellow = {}
    person = {}

    person_id = 100


    def add_person(self, person_name, person_gender, role, wants_accommodation='N'):
    
        #person = {**staff, **fellow}
        
        person_name = person_name.strip().title()
        person_gender = person_gender.strip().lower()
        role = role.strip().lower()
        wants_accommodation = wants_accommodation.strip().lower()

        if role not in ['staff', 'fellow']:
            raise RuntimeError(
                'A person can either have the role STAFF or FELLOW')

        if role == 'staff':
            if wants_accommodation != 'n':
                raise RuntimeError('Staff cannot be allocated living spaces')
            else:
                new_staff = Staff(person_name, person_gender)

                if len(new_staff.pname) > 0:
                    if len(Amity.person.keys()) == 0:
                        Amity.person_id = 100
                    else:
                        Amity.person_id = max(Amity.person.keys()) + 1

                    Amity.staff[Amity.person_id] = [Amity.person_id, new_staff.pname, new_staff.pgender.upper(), new_staff.role.title(), new_staff.wants_accommodation.upper()]

        if role == 'fellow':
            new_fellow = Fellow(person_name, person_gender, wants_accommodation)

            if len(new_fellow.pname) > 0:
                if len(Amity.person.keys()) == 0:
                    Amity.person_id = 100
                else:
                    Amity.person_id = max(Amity.person.keys()) + 1

                Amity.fellow[Amity.person_id] = [Amity.person_id, new_fellow.pname, new_fellow.pgender.upper(), new_fellow.role.title(), new_fellow.wants_accommodation.upper()]
        
        Amity.person = {**Amity.staff, **Amity.fellow}


    def change_person_role(self, person_to_change, new_role):
        
        person_to_change = person_name.strip().title()
        new_role = new_role.strip().lower()

        if person_to_change.isdigit():
            person_to_change = int(person_to_change)
            
            if person_id_to_change not in Amity.person.keys():
                raise RuntimeError ("The person does not exist")
            
            if new_role not in ['staff', 'fellow']:
                raise RuntimeError(
                'A person can either have the role STAFF or FELLOW')
                
        


a = Amity()
john = a.add_person('John', 'M', 'staFF')
jane = a.add_person('Jane', 'F', 'staFF', 'N')
maria = a.add_person('Maria', 'F', 'fellow')
luke = a.add_person('Luke', 'M', 'fellow')
mark = a.add_person('Mark', 'M', 'staFF', 'N')
joe = a.add_person('Joe', 'M', 'staFF', 'N')

print (a.person.keys())

# print("Printing change_person_role results",a.change_person_role(101))

# #print (a.john.pname, '\n')
# #print(john.pname, john.pgender, john.role, john.wants_accommodation)
# print("Staff:", a.staff.keys())
# print("Fellow", a.fellow.keys())
# print(a.person)