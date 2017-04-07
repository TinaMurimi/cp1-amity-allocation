"""
 This example uses docopt with the built in cmd module to demonstrate an
 interactive command application.

 Usage:
    Amity create_room <room_type> <room_name> <room_gender>...
    Amity add_person <person_name> <FELLOW|STAFF> [wants_accommodation]
    Amity reallocate_person <person_identifier> <new_room_name>
    Amity load_people
    Amity print_allocations [-o=filename]
    Amity print_unallocated [-o=filename]
    Amity  print_room <room_name>
    Amity save_state [--db=sqlite_database]
    Amity load_state <sqlite_database>
    Amity (-i | --interactive)
    Amity (-h | --help | --version)

 Options:
     -i, --interactive  Interactive Mode
     -h, --help  Show this screen and exit
 """

import cmd
import os
import sys

from colorama import *
from docopt import docopt, DocoptExit
from pyfiglet import figlet_format
from termcolor import cprint

from view.amity import Amity

init(wrap=True)


def docopt_cmd(func):
    def fn(self, arg):
        try:
            opt = docopt(fn.__doc__, arg)
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
        cprint("4. To quit: quit ".center(10), "green")

    intro = introduction()
    prompt = "(Amity)>> "
    file = None

    @docopt_cmd
    def do_count(self, args):
        """Amity create_room <room> <room_name> <room_gender>..."""
        print(word_counter())

    def do_quit(self, arg):
        """Quits out of Interactive Mode."""

        cprint("Exiting Application. Catch you later!", "red")
        exit()


if __name__ == "__main__":
    try:
        AmityApp().cmdloop()
    except KeyboardInterrupt:
        # os.system("clear")
        cprint("Exiting Application. Catch you later!", "red")