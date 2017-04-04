import psycopg2
import psycopg2.extras
import re
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

        allocation_id = 1

        conn = None
        try:
            conn = psycopg2.connect(database='cp1_amity')
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # To avoid duplicate primary keys from being added
            sql_query = ("""SELECT MAX(room_id) FROM room""")
            cur.execute(sql_query)
            row = cur.fetchall()[0][0]

            if row is not None:
                Amity.room_id = row + 1
            else:
                Amity.room_id = 1

            sql_query = ("""SELECT MAX(person_id) FROM person""")
            cur.execute(sql_query)
            row = cur.fetchall()[0][0]

            if row is not None:
                Amity.person_id = row + 2
            else:
                Amity.person_id = 1

            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()

            raise Exception(error)

        finally:
            if conn is not None:
                conn.close()

        platform = Amity.create_room(self, 'Platform:office')
        asmara = Amity.create_room(self, 'Asmara:office')
        tsavo = Amity.create_room(self, 'Tsavo:office')

        leila = Amity.add_person(self, 'leila', 'F', 'fellow', 'Y')

    def test_create_room_allows_creating_several_rooms(self):
        """Test a user can create as many rooms as possible by specifying multiple room names"""
        before_create = Amity.room.__len__()
        Amity.create_room(self, 'dome:office', 'home:space:m')
        after_create = Amity.room.__len__()

        self.assertEqual(2, after_create - before_create)

    def test_create_room_arguments_format(self):
        result = Amity.create_room(self, 'room', 'more rooms')
        self.assertEqual('The following rooms will not added due to input format errors: room, more rooms', result)

    def test_create_room_checks_for_room_type(self):
        """Test a room added is either office or a living space"""
        occulus = Amity.create_room('Occulus:Game Room')
        self.assertNotEqual(
            'A room can either be an OFFICE or a LIVING SPACE', occulus)

    def test_create_room_checks_for_duplicate(self):
        """Test a room with a similar name cannot be added"""
        with self.assertRaises(ValueError):
            result = Amity.create_room(self, 'Platform:office')

    def test_add_person_checks_person_role(self):
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
            key for key in Amity.allocation.keys() if Amity.allocation[key][0] == Amity.person_id]
        self.assertIn(len(found_allocations), [1, 2])

    def test_person_reallocated(self):
        """Test a person is reallocated to a room successfully"""
        Dojo = Amity.create_room(self, 'Dojo:Office')
        old_room = Amity.allocation[1][1]
        Amity.reallocate_room(self, Amity.person_id, Amity.room_id - 1)
        new_room = Amity.allocation[1][1]
        self.assertNotEqual(old_room, new_room)

    def test_occupancy_updated_after_reallocation(self):
        Dojo = Amity.create_room(self, 'Dojo:Office')
        old_occupancy = Amity.room[Amity.room_id - 1][4]
        Amity.reallocate_room(self, Amity.person_id, Amity.room_id - 1)
        new_occupancy = Amity.room[Amity.room_id - 1][4]
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
        Amity.delete_person(self, Amity.person_id)
        with self.assertRaises(KeyError) as context:
            Amity.person[100]

    def test_allocations_are_deleted_when_person_is_deleted(self):
        """Test that allocations are deleted when a person is deleted"""
        Amity.delete_person(self, Amity.person_id)
        found_allocations = [
            key for key in Amity.allocation.keys() if Amity.allocation[key][0] == 100]
        self.assertEqual(0, len(found_allocations))

    def test_print_room_output(self):
        """Test the output for the print_room is correct"""
        # ('There are no allocations for {0}'.format(room_name))
        Dojo = Amity.create_room(self, 'Dojo:Office')
        Amity.reallocate_room(self, Amity.person_id, Amity.room_id - 1)

        result = Amity.print_room(self, Amity.room_id - 1)
        self.assertEqual(result, {Amity.person_id: [
                         'Leila', 'F', 'Fellow', 'Y']})

    def test_print_room_outputs_to_file(self):
        """Test the output of print allocations can be written to a file"""
        pass

    def test_print_unallocated_output_to_file(self):
        """Test the output of print_allocations is correct"""
        unallocated = Amity.print_unallocated(self, 'unallocated_persons')
        with open('unallocated_persons.txt', 'r') as output_file:
            file_data = [line.split('\t') for line in output_file][0]

        file_data = [re.sub('\n', '', fdata) for fdata in file_data]
        self.assertEqual(list(file_data), ['Leila', 'Living Space'])

    def test_print_allocation_outputs_to_file(self):
        """Test the output of print allocations can be written to a file"""
        Amity.reallocate_room(self, 100, 1)
        pass

    def test_save_state_db_exists(self):
        with self.assertRaises(Exception) as error:
            Amity.save_state(self, 'db_name')

    def test_data_saved_to_db(self):

        conn = psycopg2.connect(database='cp1_amity')
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        query = ("""SELECT * FROM room""")
        cur.execute(query)
        count_before_insert = cur.rowcount

        Amity.save_state(self, 'cp1_amity')

        query = ("""SELECT * FROM room""")
        cur.execute(query)
        count_after_insert = cur.rowcount

        self.assertEqual(count_after_insert - count_before_insert, 3)

        cur.close()
        conn.commit()

    def test_load_state_db_exists(self):
        with self.assertRaises(Exception) as error:
            Amity.save_state(self, 'db_name')

    def test_load_state_loads_data_to_app(self):
        """Test data is loaded successfully from DB to application"""
        before_load = Amity.person.__len__()
        Amity.load_state(self, 'cp1_amity')
        after_load = Amity.person.__len__()

        self.assertGreater(after_load, before_load)