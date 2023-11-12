from sys import argv
import offtoot.store
import offtoot.reader

def main():
    if len(argv) < 2:
        print("You need to provide at least one argument!")
        exit(1)
    match argv[1]:
        case "store":
            offtoot.store.main(argv[2:])
        case "reader":
            offtoot.reader.main(argv[2:])
