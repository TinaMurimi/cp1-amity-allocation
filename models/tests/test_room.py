# KeyError

import unittest

from models.room import Room, LivingSpace, Office


class TestRoom(unittest.TestCase):

    def setUp(self):
        self.accra = Office('Accra', 6)
        self.tsavo = LivingSpace('Tsavo', 6, 'M')

    def tearDown(self):
        pass

    def test_Room_is_an_abstact_class(self):
        """Can't instantiate abstract class Room with abstract methods room_type"""
        with self.assertRaises(Exception) as context:
            asmara = Room('Asmara', 'office', 6, '', 3)
        self.assertTrue(str(context.exception)
                        in "Can't instantiate abstract class Room with abstract methods room_type")

    def test_Office_is_a_subclass_of_Room(self):
        self.assertTrue(issubclass(Office, Room),
                        "class Office should be a subclass of Room")

    def test_LivingSpace_is_a_subclass_of_Room(self):
        self.assertTrue(issubclass(LivingSpace, Room),
                        "class LivingSpace should be a subclass of Room")

    def test_Office_instance(self):
        self.assertIsInstance(
            self.accra, Office, msg="The object is not an instance of the class 'Office'")

    def test_Office_object_type(self):
        self.assertTrue((type(self.accra) is Office),
                        msg='The object should be of type Office')

    def test_default_type_for_Office_is_offce(self):
        self.assertEqual(
            "office", self.accra.rtype,
            msg='Objects created using with the Office class should have the role Office')