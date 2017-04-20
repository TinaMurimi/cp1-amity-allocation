import re
import unittest

from models.amity import Amity


class TestAmity(unittest.TestCase):

    def setUp(self):
        Amity.office = []
        Amity.space = []
        Amity.room = []

        Amity.staff = []
        Amity.fellow = []
        Amity.person = []

        Amity.allocation = []

        self.platform = Amity.create_room(self, 'office', ' ', ['platform'])
        self.skew = Amity.create_room(self, 'space', 'm', ['skew'])

        self.harry = Amity.add_person(self, 'harry', 'M', 'fellow')
        self.matt = Amity.add_person(self, 'matt', 'M', 'fellow', 'Y')

    def tearDown(self):
        del self.platform
        del self.skew
        del self.harry
        del self.matt

    def test_create_room_allows_creating_multiple_rooms(self):
        """Test a user can create as many rooms as possible by specifying multiple room names"""
        result = Amity.create_room(self, 'space', 'male', [
                                   'boys', 'men', 'dudes'])
        self.assertEqual(result, '3 rooms added successfully')

    def test_create_room_checks_for_room_type(self):
        """Test a room added is either office or a living space"""
        result = Amity.create_room(self, 'game room', 'male', ['occulus'])
        self.assertEqual(
            result, 'A room can either be an OFFICE or a LIVING SPACE')

    def test_create_room_checks_for_duplicate(self):
        """Test a room with a similar name cannot be added"""
        result = Amity.create_room(self, 'office', ' ', ['platform'])
        self.assertEqual(result, 'Room already exists')

    def test_office_added_has_no_gender(self):
        """Test that an office added has no gender specified"""
        result = Amity.create_room(self, 'office', 'male', ['occulus'])
        self.assertEqual(
            result, 'An office can be occupied by both male and female')

    def test_living_space_added_has_gender(self):
        """Test that a living space added has gender specified"""
        result = Amity.create_room(self, 'space', ' ', ['Ruby'])
        self.assertEqual(
            result, 'Please specify if the living space is for male or female')

    def test_add_person_checks_person_role(self):
        """Test a person added is either staff or a fellow"""
        result = Amity.add_person(self, 'Mark', 'M', 'guest')
        self.assertEqual(result,
                         'A person can either have the role STAFF or FELLOW')

    def test_staff_cannot_be_allocated_living_space(self):
        """Test staff cannot be allocated living spaces"""
        result = Amity.add_person(self, 'Ann Maina', 'F', 'staff', 'Y')
        self.assertEqual(result, 'Staff cannot be allocated living spaces')

    def test_search_person_by_id_or_name(self):  # rephrase
        """Test search_person searches using name and ID"""
        harry_id = [people['person_id']
                    for people in Amity.person if people['person_name'] == 'Harry'][0]

        result_str = Amity.search_person(self, 'harry')
        result_int = Amity.search_person(self, harry_id)
        self.assertEqual(result_str, result_int,
                         msg='Search text should search with either name and ID')

    def test_search_person_output_when_no_search_results_found(self):
        """Test output wheh search yields no results"""
        result = Amity.search_person(self, 'No Name')
        self.assertEqual(
            'No entry found for person with ID or name No Name', result)

    def test_load_people_adds_people_correctly(self):
        """Test people can be added from a text file"""
        result = Amity.load_people(self)
        self.assertEqual(result, '7 people loaded!')

    def test_person_allocated_room(self):
        """Test a person is allocated room on creation"""
        result = Amity.add_person(self, 'Agatha', 'F', 'fellow')
        self.assertEqual(result, 'Person added and allocated room')

    def test_person_is_reallocated(self):
        """Test a person is reallocated to a room successfully"""
        Amity.create_room(self, 'office', ' ', ['tsavo'])
        result = Amity.reallocate_person(self, 'harry', 'tsavo')
        self.assertEqual(
            result, 'Harry has been reallocated office from Platform to Tsavo')

    def test_reallocation_to_space(self):
        """Test a person is not realocated to a room of the wrong gender"""
        Amity.create_room(self, 'space', 'f', ['ruby'])
        result = Amity.reallocate_person(self, 'harry', 'ruby')
        self.assertEqual(
            result, 'A person of gender M is being allocated to a living space for F')

    def test_room_deletion(self):
        """Test a room is deleted successfully"""
        result = Amity.delete_room(self, 'PLATFORM')
        self.assertEqual(result, 'Platform has been deleted successfully')

    def test_person_deletion(self):
        """Test a person is deleted successfully"""
        result = Amity.delete_person(self, 'harry')
        self.assertEqual(result, 'Harry has been deleted successfully')

    def test_print_room_output(self):
        """Test the output for the print_room is correct"""
        dome = Amity.create_room(self, 'space', 'm', ['dome'])
        Amity.reallocate_person(self, 'matt', 'dome')
        result = Amity.print_room(self, 'dome')
        self.assertEqual(result, ['Matt'])

    def test_find_unallocated_output(self):
        """Test the output of print_allocations is correct"""
        Amity.delete_room(self, 'platform')
        result = Amity.find_unallocated(self)
        self.assertEqual(result[0]['person_name'], 'Harry')

    def test_print_allocation_outputs_to_file(self):
        """Test the output of print allocations can be written to a file"""
        result = Amity.print_allocations(self)
        self.assertEqual(result, 'Data saved to file')

    def test_data_saved_to_db(self):
        """Test data is saved to DB successfully"""
        result = Amity.save_state(self, 'test_amity')
        self.assertEqual(
            result, 'Session data successfully saved to DB named: test_amity.db')

    def test_load_state_loads_data_to_app(self):
        """Test data is loaded successfully from DB to application"""
        result = Amity.load_state(self, 'test_amity')
        self.assertEqual(
            result, 'Data loaded successfully! Use the list functions to view the data')
