from os import get_terminal_size
from offtoot.store.config import STATE_LOCATION, STORAGE_LOCATION

from offtoot.store.post import Post, Reblog, Status
from offtoot.store.account import Account
from typing import List

def sanitize_html(text: str, indent: int = 0):
    text = text.removeprefix("<p>")
    text = text.removesuffix("</p>")
    manual_lines = text.split("<br>")

    lines = []
    for manual_line in manual_lines:
        width = get_terminal_size().columns
        ls = [ manual_line ]
        while len(ls[len(ls)-1])+indent > width:
            l = ls.pop()
            ls += [l[:width-indent],l[width-indent:].removeprefix(" ")]
        lines += ls

    if len(lines) == 1:
        return lines[0]
    else:
        return lines

def printi(text, indent: int, sanitize = False):
    if sanitize:
        text = sanitize_html(text, indent)
    i = ""
    while len(i) < indent:
        i += " "
    if type(text) == str:
        print(i+text)
    elif type(text) == list:
        for l in text:
            print(i+l)

def print_status(status: Status, indent: int = 0):
    assert type(status.account) == Account
    printi("User: {}".format(status.account.display_name or status.account.acct), indent)
    if type(status) == Reblog:
        printi("Reblogging:", indent)
        assert type(status.post) == Post
        print_status(status.post, indent + 2)
    else:
        assert type(status) == Post
        printi("Url: {}".format(status.url), indent)
        printi("Content:", indent)
        printi(status.content, indent+2, sanitize=True)

def read_tour() -> List[str]:
    tour_file = STATE_LOCATION / "tour" # TODO: Deduplicate tour reading/writing
    tour: List[str] = []
    if tour_file.exists():
        with open(tour_file, "r") as f:
            tour = f.readlines()
    return tour

def write_tour(tour: List[str]):
    tour_file = STATE_LOCATION / "tour"
    with open(tour_file, "w+") as f:
        f.writelines(tour)

def show_post_from_tour(p: str):
    p = p.removesuffix("\n")
    acct = p.split("::")[0]
    id = p.split("::")[1]
    path = STORAGE_LOCATION / acct / "posts" / "{}.json".format(id)
    status = Status.load(path)
    print_status(status)

def list_new():
    posts = read_tour()
    for p in posts:
        show_post_from_tour(p)

def tour():
    tour = read_tour()
    show_post_from_tour(tour.pop())
    write_tour(tour)

def main(argv):
    if len(argv) == 0:
        print("You need an argument for the reader!")
        exit(1)
    match argv[0]:
        case "list":
            list_new()
        case "tour":
            tour()
