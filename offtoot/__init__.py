from sys import argv
from typing import List
import offtoot.store
import offtoot.reader

def main(args: List[str] = []):
    if len(args) == 0:
        args = argv[1:]
    if len(args) < 1:
        print("You need to provide at least one argument!")
        exit(1)
    match args[0]:
        case "store":
            offtoot.store.main(args[1:])
        case "reader":
            offtoot.reader.main(args[1:])
        case "help" | "--help" | _:
            print('Available subcommands: "store", "reader"')
