import unittest

from amity import Amity


class TestAmity(unittest.TestCase):

    def setUp(self):
        Amity.office = {}
        Amity.space = {}
        Amity.room = {}

        Amity.staff = {}
        Amity.fellow = {}
        Amity.person = {}

        Amity.allocation = {}

        Amity.person_id = 100
        Amity.room_id = 1
        Amity.allocation_id = 1

        platform = Amity.create_room(self, 'Platform', 'office', 6, '')
        asmara = Amity.create_room(self, 'Asmara', 'office', 6, '')
        tsavo = Amity.create_room(self, 'Tsavo', 'office', 6, '')

        leila = Amity.add_person(self, 'leila', 'F', 'fellow')

    # def tearDown(self):
    #     pass
    def test_room_added_is_either_office_or_living(self):
        """Test a room added is either office or a living space"""
        occulus = Amity.create_room(self, 'Occulus', 'Game Room', 6, 'M')
        self.assertEqual(
            'A room can either be an OFFICE or a LIVING SPACE', occulus)

    def test_room_duplicate(self):
        """Test a room with a similar name cannot be added"""
        with self.assertRaises(Exception):
            platform = Amity.create_room(self, 'Platform', 'office', 6, '')

    def test_person_added_is_either_staff_or_fellow(self):
        """Test a person added is either staff or a fellow"""
        mark = Amity.add_person(self, 'Mark', 'M', 'guest')
        self.assertEqual(
            'A person can either have the role STAFF or FELLOW', mark)

    def test_default_for_wants_accommodation_is_no(self):
        """Test default for want_accommodation is 'N'"""
        leila = Amity.add_person(self, 'leila', 'F', 'staff')
        result = Amity.person[Amity.person_id][3]
        self.assertEqual(
            result, 'N', msg="Default for wants_accommodation should be 'N'")

    def test_staff_cannot_be_allocated_living_space(self):
        """Test staff cannot be allocated living spaces"""
        ann = Amity.add_person(self, 'Ann Maina', 'F', 'staff', 'Y')
        self.assertEqual('Staff cannot be allocated living spaces', ann)

    def test_search_person_only_searches_for_a_single_string(self):
        """Test search_person text to search type"""
        with self.assertRaises(TypeError) as context:
            Amity.search_person(self, Amity.person, '[Mark]')

    def test_search_person_only_searches_for_a_single_string(self):
        """Test search_person searches using name and ID"""
        harry = Amity.add_person(self, 'harry', 'M', 'fellow')
        result_str = Amity.search_person(self, Amity.person, 'harry')
        result_int = Amity.search_person(self, Amity.person, Amity.person_id)
        self.assertEqual(result_str, result_int,
                         msg='Search text should search with both name and ID')

    def test_search_person_output_when_no_search_results_found(self):
        """Test output wheh search yields no results"""
        result = Amity.search_person(self, Amity.person, 'No Name')
        self.assertEqual(
            'No entry found for person with ID or name No Name', result)

    def test_search_result_output_for_search_is_dict(self):
        """Test search results are in a dictionary"""
        result = Amity.search_person(self, Amity.person, 'leila')
        self.assertIsInstance(
            result, dict, "Search output shoule be a dictionary")

    def test_load_peopl_takes_a_file(self):
        """Test if file to load people exists"""
        with self.assertRaises(FileNotFoundError) as error:
            result = Amity.load_people(self, "text_file.txt")

    def test_person_allocated_room(self):
        """Test a person is allocated room on creation"""
        found_allocations = [
            key for key in Amity.allocation.keys() if Amity.allocation[key][0] == 100]
        self.assertIn(len(found_allocations), [1, 2])

    def test_a_room_is_deleted_successfully(self):
        """Test a room is deleted successfully"""
        Amity.delete_room(self, 'PLATFORM')
        with self.assertRaises(KeyError) as context:
            Amity.room[1]

    def test_allocations_are_deleted_when_room_is_deleted(self):
        """Test that allocations are deleted when a room is deleted"""
        Amity.delete_room(self, 'PLATFORM')
        found_allocations = [
            key for key in Amity.allocation.keys() if Amity.allocation[key][1] == 1]
        self.assertEqual(0, len(found_allocations))

    def test_a_person_is_deleted_successfully(self):
        """Test a person is deleted successfully"""
        Amity.delete_person(self, 100)
        with self.assertRaises(KeyError) as context:
            Amity.person[100]

    def test_allocations_are_deleted_when_person_is_deleted(self):
        """Test that allocations are deleted when a person is deleted"""
        Amity.delete_person(self, 100)
        found_allocations = [
            key for key in Amity.allocation.keys() if Amity.allocation[key][0] == 100]
        self.assertEqual(0, len(found_allocations))

    def test_load_people_adds_people_correctly(self):
        """Test people can be added from a text file"""
        old_dict_key = [key for key in Amity.person.keys()]
        Amity.load_people(self, 'person.txt')
        new_dict_key = [key for key in Amity.person.keys()]
        self.assertEqual(7, len(new_dict_key) - len(old_dict_key))

    # print_allocations [-o=filename]  - Prints a list of allocations onto the
    # screen. Specifying the optional  -o  option here outputs the registered
    # allocations to a txt file.

#     ROOM NAME
# -------------------------------------
# MEMBER 1, MEMBER 2, MEMBER 3
# ROOM NAME
# -------------------------------------
# MEMBER 1, MEMBER 2

    # print_room <room_name>  - Prints the names of all the people in
    # room_name  on the screen.
