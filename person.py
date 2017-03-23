#O-Reilly Programming Python 4th error()
# pg 28
# pg 34, 1304: shelve pr pickle

# https://jeffknupp.com/blog/2014/06/18/improve-your-python-python-classes-and-object-oriented-programming/
# http://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python
# https://docs.python.org/3/library/exceptions.html#TypeError

from abc import ABC, ABCMeta, abstractmethod

class Person(ABC):
    """Abstract base class
    
    A person is an employee at Andela. that can be assigned an Amity facility A person can either be a:
        1. fellow
        2. staff

    Attributes:
        - pid: A string representing the employee ID
        - pname: A string representing the person's name
        - pgender: A string M or F representing the person's gender
        - pType: A string representing if a person is a fellow or staff
    """

    __metaclass__ = ABCMeta

    counter = 0

    def __init__(self, pid, pname, pgender, pType):
        Person.counter += 1
        self.pid = pid
        self.pname = pname
        self.pgender = pgender
        self.pType = pType

        if self.pType not in ['staff', 'fellow']:
             raise RuntimeError ("A person can only be a fellow or staff")

    def change_pType(self, new_pType):
        """Returns the new employee type a person is"""

        old_rType = self.pType
        self.pType = new_pType
        return (self.pType )

    def __del__(self):
        Person.counter -= 1
    
    @abstractmethod
    def person_type(self):
        """"Return a string representing the type of employyee a person is"""
        raise NotImplementedError()

class Fellow(Person):
    """Fellow: An employee of Andela

    Attributes:
        - pid: A string representing the staff ID
        - pname: A string representing the fellow's name
        - pgender: A string M or F representing the fellow's gender
    """

    def __init__(self, pid, pname, pgender):
        #super(Fellow, self).__init__()
        Person.__init__(self, pid, pname, pgender, 'fellow')

    def afunction(self):
        pass

    def person_type(self):
        """"Return a string representing the type of employee a person is this is"""
        return 'fellow'

        
class Staff(Person):
    """Staff: An employee of Andela

    Attributes:
        - pid: A string representing the staff ID
        - pname: A string representing the staff's name
        - pgender: A string M or F representing the staff's gender
    """

    def __init__(self, pid, pname, pgender):
        #super(Fellow, self).__init__()
        Person.__init__(self, pid, pname, pgender, 'staff')

    def afunction(self):
        pass
        
    def person_type(self):
        """"Return a string representing the type of employee a person is this is"""
        return 'staff'


assert issubclass(Fellow, Person)
#assert isinstance((), Person)

if __name__ == '__main__':
    #tina = Person('C15-NBO-1234', 'Tina', 'F', 'guest')
    
    #tina = Person('C15-NBO-1234', 'Tina', 'F', 'fellow')
    adam = Fellow('C15-NBO-1235', 'Adam', 'M')
    # ruth = Staff('C15-NBO-1236', 'Ruth', 'F')

    #print (tina.pid, tina.pname, tina.pgender, tina.pType)
    print (adam.pid, adam.pname, adam.pgender, adam.pType)
    # print (ruth.pid, ruth.pname, ruth.pgender, ruth.pType)

    # print (tina.counter)
    # print (Person.counter)



    # print ('\n')
    # zack = Fellow('C15-NBO-1236', 'Zack', 'M')
    # print (zack.pType)
    # zack.change_pType('staff')
    # print (zack.pType)

    # print ('Number of objects created',Person.counter)
    # print ('\nwe are deleting', adam.pname)
    del adam
    print (adam.pid, adam.pname, adam.pgender, adam.pType)

    # print (Person.counter)
    
    # print ('\nwe are deleting', tina.pname)
    # del tina
    # print (Person.counter)