# O-Reilly Programming Python 4th error()
# pg 28
# pg 34, 1304: shelve pr pickle

# https://jeffknupp.com/blog/2014/06/18/improve-your-python-python-classes-and-object-oriented-programming/
# http://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python
# https://docs.python.org/3/library/exceptions.html#TypeError

from abc import ABC, ABCMeta, abstractmethod


class Person(ABC):
    """Abstract Base Class

    A person is an employee at Andela. that can be assigned an Amity facility. A person can either be a:
        1. fellow
        2. staff

    Attributes:
        - pname: A string representing the person's name
        - pgender: A string M or F representing the person's gender
        - role: A string representing if a person is a fellow or staff
    """

    def __init__(self, pname, pgender, role):
        "Creates an object with the attributes"
        self.pname = pname
        self.pgender = pgender
        self.role = role

    def __del__(self):
        #Person.counter -= 1
        pass

    @abstractmethod
    def person_type(self):
        """"Return a string representing the type of employyee a person is"""
        raise NotImplementedError()


class Fellow(Person):
    """Fellow: An employee of Andela

    Attributes:
        - pname: A string representing the fellow's name
        - pgender: A string M or F representing the fellow's gender
    """

    def __init__(self, pname, pgender, wants_accommodation='N'):
        self.wants_accommodation = wants_accommodation
        super(Fellow, self).__init__(pname, pgender, 'fellow')

    def person_type(self):
        """"Return a string representing the type of employee a person is this is"""
        return 'fellow'


class Staff(Person):
    """Staff: An employee of Andela

    Attributes:
        - pname: A string representing the staff's name
        - pgender: A string M or F representing the staff's gender
    """

    def __init__(self, pname, pgender):
        #super(Fellow, self).__init__()
        super(Staff, self).__init__(pname, pgender, 'staff')

    def person_type(self):
        """"Return a string representing the type of employee a person is this is"""
        return 'staff'



# if __name__ == '__main__':
    #tina = Person('Tina', 'F', 'guest')

    #tina = Person('Tina', 'F', 'fellow')
    # adam = Fellow('Adam', 'M', 'Y')
    #ann = Fellow('ann', 'M')

    # ruth = Staff('Ruth', 'F')

    #print (tina.pname, tina.pgender, tina.role, tina.wants_accommodation)
    # print (adam.pname, adam.pgender, adam.role, adam.wants_accommodation)
    # print (ruth.pname, ruth.pgender, ruth.role, ruth.wants_accommodation)

    # print (locals())

    # print (tina.created_fellows)
    #print (Fellow.created_fellows)

    # print ('\n')
    # zack = Fellow('Zack', 'M')
    # print (zack.role)
    # zack.change_role('staff')
    # print (zack.role)

    # print ('Number of objects created',Person.counter)
    # print ('\nwe are deleting', adam.pname)
    #del adam
    #print (adam.pname, adam.pgender, adam.role)

    # print (Person.counter)

    # print ('\nwe are deleting', tina.pname)
    # del tina
    # print (Person.counter)
