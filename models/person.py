from abc import ABC, abstractmethod


class Person(ABC):
    """Abstract Base Class

    A person is an employee at Andela. that can be assigned an Amity facility. A person can either be a:
        1. fellow
        2. staff

    Attributes:
        - person_name: A string representing the person's name
        - person_gender: A string M or F representing the person's gender
        - role: A string representing if a person is a fellow or staff
    """

    def __init__(self, person_name, person_gender):
        "Creates an object with the attributes"
        self.person_name = person_name
        self.person_gender = person_gender

    @abstractmethod
    def person_type(self):
        """"Return a string representing the type of employyee a person is"""
        raise NotImplementedError()


class Fellow(Person):
    """Fellow: An employee of Andela

    Attributes:
        - person_name: A string representing the fellow's name
        - person_gender: A string M or F representing the fellow's gender
    """

    def __init__(self, person_name, person_gender, wants_accommodation='N'):
        super(Fellow, self).__init__(person_name, person_gender)

        self.wants_accommodation = wants_accommodation
        self.role = 'fellow'

    def person_type(self):
        """"Return a string representing the type of employee a person is this is"""
        return 'fellow'


class Staff(Person):
    """Staff: An employee of Andela

    Attributes:
        - person_name: A string representing the staff's name
        - person_gender: A string M or F representing the staff's gender
    """

    def __init__(self, person_name, person_gender):
        super(Staff, self).__init__(person_name, person_gender)
        self.role = 'staff'

    def person_type(self):
        """"Return a string representing the type of employee a person is this is"""
        return 'staff'