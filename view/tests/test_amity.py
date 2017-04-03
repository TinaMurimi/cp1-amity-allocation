import unittest

from view.amity import Amity


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

    def test_room_type(self):
        """Test a room added is either office or a living space"""
        occulus = Amity.create_room(self, 'Occulus', 'Game Room', 6, 'M')
        self.assertEqual(
            'A room can either be an OFFICE or a LIVING SPACE', occulus)

    def test_room_duplicate(self):
        """Test a room with a similar name cannot be added"""
        with self.assertRaises(ValueError):
            result = Amity.create_room(self, 'Platform', 'office', 6, '')

    def test_office_capacity(self):
        """Test that the maximum capacity for offices is 6"""
        with self.assertRaises(ValueError):
            Amity.create_room(self, 'Occulus', 'office', 8, '')

    def test_living_space_capacity(self):
        """Test that the maximum capacity for offices is 4"""
        with self.assertRaises(ValueError):
            Amity.create_room(self, 'Occulus', 'space', 8, '')

    def test_person_type(self):
        """Test a person added is either staff or a fellow"""
        mark = Amity.add_person(self, 'Mark', 'M', 'guest')
        self.assertEqual(
            'A person can either have the role STAFF or FELLOW', mark)

    def test_staff_cannot_be_allocated_living_space(self):
        """Test staff cannot be allocated living spaces"""
        ann = Amity.add_person(self, 'Ann Maina', 'F', 'staff', 'Y')
        self.assertEqual('Staff cannot be allocated living spaces', ann)

    def test_search_person_by_id_or_name(self):  # rephrase
        """Test search_person searches using name and ID"""
        harry = Amity.add_person(self, 'harry', 'M', 'fellow')
        result_str = Amity.search_person(self, Amity.person, 'harry')
        result_int = Amity.search_person(self, Amity.person, Amity.person_id)
        self.assertEqual(result_str, result_int,
                         msg='Search text should search with either name and ID')

    def test_search_person_output_when_no_search_results_found(self):
        """Test output wheh search yields no results"""
        result = Amity.search_person(self, Amity.person, 'No Name')
        self.assertEqual(
            'No entry found for person with ID or name No Name', result)

    def test_load_people_takes_a_file(self):
        """Test if file to load people exists"""
        with self.assertRaises(FileNotFoundError) as error:
            result = Amity.load_people(self, "text_file.txt")

    def test_load_people_adds_people_correctly(self):
        """Test people can be added from a text file"""
        old_dict_key = [key for key in Amity.person.keys()]
        Amity.load_people(self, 'person.txt')
        new_dict_key = [key for key in Amity.person.keys()]
        self.assertEqual(7, len(new_dict_key) - len(old_dict_key))

    def test_person_allocated_room(self):
        """Test a person is allocated room on creation"""
        found_allocations = [
            key for key in Amity.allocation.keys() if Amity.allocation[key][0] == 100]
        self.assertIn(len(found_allocations), [1, 2])

    def test_person_reallocated(self):
        """Test a person is reallocated to a room successfully"""
        Dojo = Amity.create_room(self, 'Dojo', 'Office', 6)
        old_room = Amity.allocation[1][1]
        Amity.reallocate_room(self,100, Amity.room_id)
        new_room = Amity.allocation[1][1]
        self.assertNotEqual(old_room, new_room)

    def test_occupancy_updated_after_reallocation(self):
        Dojo = Amity.create_room(self, 'Dojo', 'Office', 6)
        old_occupancy = Amity.room[Amity.room_id][4]
        Amity.reallocate_room(self,100, Amity.room_id)
        new_occupancy = Amity.room[Amity.room_id][4]
        self.assertNotEqual(old_occupancy, new_occupancy)

    def test_room_deletion(self):
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

    def test_person_deletion(self):
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

    def test_print_room_output(self):
        """Test the output for the print_room is correct"""
        # ('There are no allocations for {0}'.format(room_name))
        Dojo = Amity.create_room(self, 'Dojo', 'Office', 6)
        Amity.reallocate_room(self,100, Amity.room_id)

        result = Amity.print_room(self, Amity.room_id)
        self.assertEqual(result, {100: ['Leila', 'F', 'Fellow', 'N']})


    def test_print_allocation_output_to_file(self):
        """Test the output of print allocations can be written to a file"""
        pass
