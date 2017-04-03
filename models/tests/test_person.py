import unittest

from models.person import Person, Staff, Fellow


class TestPerson(unittest.TestCase):

    def setUp(self):
        self.adam = Fellow('Adam', 'M')
        self.ann = Staff('Ann', 'F')

    def tearDown(self):
        pass

    def test_Person_is_an_abstact_class(self):
        """Can't instantiate abstract class Person with abstract methods person_type"""
        with self.assertRaises(Exception) as context:
            Person('Tina', 'F', 'fellow')
        self.assertTrue(str(context.exception)
                        in "Can't instantiate abstract class Person with abstract methods person_type")

    def test_Fellow_is_a_subclass_of_person(self):
        self.assertTrue(issubclass(Fellow, Person),
                        "class Fellow should be a subclass of Person")

    def test_Staff_is_a_subclass_of_person(self):
        self.assertTrue(issubclass(Staff, Person),
                        "class Staff should be a subclass of Person")

    def test_fellow_instance(self):
        self.assertIsInstance(
            self.adam, Fellow,
            msg="The object is not an instance of the class 'Fellow'")

    def test_fellow_object_type(self):
        self.assertTrue((type(self.adam) is Fellow),
                        msg='The object should be of type Fellow')

    def test_default_role_for_fellow_is_fellow(self):
        self.assertEqual(
            "fellow", self.adam.role,
            msg='Objects created using with the Fellow class should have the role fellow')