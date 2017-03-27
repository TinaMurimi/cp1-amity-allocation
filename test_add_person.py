import unittest

from add_person import Amity


class TestAmity(unittest.TestCase):

    def setUp(self):
        leila = Amity.add_person(self, 'leila', 'F', 'fellow')

    # def tearDown(self):
    #     pass

    def test_person_added_is_either_staff_or_fellow(self):
        """Test a person added is either staff or a fellow"""
        mark = Amity.add_person(self, 'Mark', 'M', 'guest')
        self.assertEqual(
            'A person can either have the role STAFF or FELLOW', mark)

    def test_default_for_wants_accommodation_is_no(self):
        """Test default for want_accommodation is 'N'"""
        leila = Amity.add_person(self, 'leila', 'F', 'staff')
        result = Amity.person[Amity.person_id][4]
        self.assertEqual(
            result, 'N', msg="Default for wants_accommodation should be 'N'")

    def test_staff_cannot_be_allocated_living_space(self):
        """Test staff cannot be allocated living spaces"""
        ann = Amity.add_person(self, 'Ann Maina', 'F', 'staff', 'Y')
        self.assertEqual('Staff cannot be allocated living spaces', ann)

    # to correct
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

    def test_change_role_updates_role_successsfully(self):
        """Test role has been updated successfully"""
        before_change = Amity.person[Amity.person_id][3]
        Amity.change_person_role(self, Amity.person_id, 'staff')
        after_change = Amity.person[Amity.person_id][3]
        self.assertNotEqual(before_change, after_change)

    def test_change_role_updates_needs_accommodation_accordingly(self):
        """Test needs_accommodation is update when a person's role is updated to staff"""
        bruce = Amity.add_person(self, 'Bruce', 'M', 'fellow', 'Y')
        before_change = Amity.person[Amity.person_id][4]
        Amity.change_person_role(self, Amity.person_id, 'staff')
        after_change = Amity.person[Amity.person_id][4]
        self.assertNotEqual(before_change, after_change)

    def test_a_person_is_deleted_successfully(self):
        """Test a person is deleted successfully"""
        Amity.delete_person(self, 100)
        with self.assertRaises(KeyError) as context:
            Amity.person[100]
