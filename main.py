"""
 This example uses docopt with the built in cmd module to demonstrate an
 interactive command application.
 Usage:
    Amity create_room <room> <room_name> [room_gender]
    Amity add_person <person_name> <person_gender> <role [<wants_accommodation>]
    Amity reallocate_person <person_identifier> <new_room_name>
    Amity load_people
    Amity print_allocations [-o=filename]
    Amity print_unallocated [-o=filename]
    Amity print_room <room_name>
    Amity save_state [--db=sqlite_database]
    Amity load_state <sqlite_database>
    Amity (-i | --interactive)
    Amity (-h | --help)
    Amity (--version)
 Options:
    -i, --interactive   Interactive Mode
    -h, --help Show on this screen and then exit
    --version   Show version and exit
    -o=filename]    Specify output file
    --db=sqlite_database Database to save session data
 """

import argparse
import cmd
import os
import sys


from colorama import *
from docopt import docopt, DocoptExit
from pyfiglet import figlet_format
from termcolor import cprint

from view.amity import Amity
 
# init(wrap=True)


def docopt_cmd(func):
    def fn(self, arg):
        try:
            opt = docopt(fn.__doc__, arg, version='Amity 1.0')

        except DocoptExit as error:

            # The DocoptExit is thrown when the args do not match
            # We print a message to the user and the usage block
            print("Invalid Command!")
            print(error)
            return

        except SystemExit:
            # The SystemExit exception prints the usage for --help
            # We do not need to do the print here
            return

        return func(self, opt)

    fn.__name__ = func.__name__
    fn.__doc__ = func.__doc__
    fn.__dict__.update(func.__dict__)

    return fn


class AmityApp(cmd.Cmd):
    cprint("\n")
    cprint(figlet_format("AMITY ALLOCATION".center(
        15), font="standard"), "yellow", attrs=["bold"])

    def introduction():
        """ Amity Commands
        """
        cprint("\n")
        # cprint("TSA COMMAND LIST:".center(30), "green")
        # cprint("\n")
        # cprint("1. Perform a word-frequency analysis: count".center(10), "green")
        # cprint("2. Perform sentiment analysis using the Alchemy API: sentim ".center(
        #     10), "green")
        # cprint(
        #     "3. Perform emotion analysis using the Alchemy API: emo".center(10), "green")
        # cprint("4. To quit: quit ".center(10), "green")

    intro = introduction()
    prompt = "(Amity)>> "
    file = None

    @docopt_cmd
    def do_create_room(self, args):
        """Usage: create_room (Office|Living-Space|Space) (Male|m|Female|f|None|n) <room_name>..."""

        if args['Office']:
            room_type = 'office'
        elif args['Living-Space'] or args['Space']:
            room_type = 'space'

        if args['Male'] or args['m']:
            room_gender = 'M'
        elif args['Female'] or args['f']:
            room_gender = 'F'
        elif args['None'] or args['n']:
            room_gender = ''

        Amity.create_room(self, room_type, room_gender, args['<room_name>'])

    @docopt_cmd
    def do_list_rooms(self, args):
        """Usage: list_rooms"""

        Amity.list_rooms(self)

    @docopt_cmd
    def do_delete_room(self, args):
        """Usage: delete_room <room_identifier>"""

        Amity.delete_room(self, args['<room_identifier>'])

    @docopt_cmd
    def do_add_person(self, args):
        """Usage: add_person <person_name> <person_gender> (Fellow|Staff) [<wants_accommodation>]"""

        if args['Fellow']:
            role = 'Fellow'
        elif args['Staff']:
            role = 'Staff'

        if not args['<wants_accommodation>']:
            args['<wants_accommodation>'] = 'N'

        Amity.add_person(self, args['<person_name>'], args['<person_gender>'], role, args['<wants_accommodation>'])

    @docopt_cmd
    def do_list_people(self, args):
        """Usage: list_people"""

        Amity.list_people(self)

    @docopt_cmd
    def do_delete_person(self, args):
        """Usage: delete_person <person_identifier>"""

        Amity.delete_person(self, args['<person_identifier>'])

    @docopt_cmd
    def do_reallocate_person(self, args):
        """Usage: reallocate_person <person_identifier> <new_room_name>"""
        Amity.reallocate_room(self, args['<person_identifier>'], args['<new_room_name>'])

    @docopt_cmd
    def do_load_people(self, args):
        """Usage: load_people"""
        Amity.load_people(self)

    @docopt_cmd
    def do_print_allocations(self, args):
        """Usage: print_allocations [-o=filename]"""

        if not args['-o']:
            args['-o'] = 'allocations.txt'

        Amity.print_allocations(self, args['-o'])

    @docopt_cmd
    def do_print_unallocated(self, args):
        """Usage: print_unallocated [-o=filename]"""

        if not args['-o']:
            args['-o'] = 'Unallocated.txt'

        Amity.print_unallocated(self, args['-o'])

    @docopt_cmd
    def do_print_room(self, args):
        """Usage: print_room <room_name>"""

        Amity.print_room(self, args['<room_name>'])

    @docopt_cmd
    def do_save_state(self, args):
        """Usage: save_state [--db=<sqlite_database>]"""

        if not args['--db']:
            args['--db'] = 'cp1_amity'

        Amity.save_state(self, args['--db'])

    @docopt_cmd
    def do_load_state(self, args):
        """Usage: load_state [--db=<sqlite_database>]"""

        if not args['--db']:
            args['--db'] = 'cp1_amity'

        print(Amity.load_state(self, args['--db']))

    def do_quit(self, arg):
        """Quits out of Interactive Mode."""

        cprint("Exiting Application. Catch you later!", "red")
        exit()


# opt = docopt(__doc__, sys.argv[1:])

# if opt['--interactive']:
#     AmityApp().cmdloop()

# print(opt)

if __name__ == "__main__":
    try:
        AmityApp().cmdloop()
    except KeyboardInterrupt:
        # os.system("clear")
        cprint("Exiting Application. Catch you later!", "red")