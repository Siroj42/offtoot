from os import get_terminal_size
from offtoot.store.config import STATE_LOCATION
from offtoot.store.lists import read_tour, write_tour, get_post_from_tour_format
from unicodedata import east_asian_width
from bs4 import BeautifulSoup, Tag

from offtoot.store.post import Post, Reblog, Status
from offtoot.store.account import Account
from offtoot.reader.media import display_media
from typing import List, Tuple

def sanitize_html(text: str, indent: int) -> Tuple[List[str], List[str]]:
    sanitized = "" 
    soup = BeautifulSoup(text, "html.parser")
    links = []
    for p in soup.find_all("p"):
        assert type(p) == Tag
        for c in p.children:
            if type(c) == Tag:
                match c.name:
                    case "br":
                        sanitized += "\n"
                    case "a":
                        links.append(c.attrs["href"])
                        if "class" in c.attrs and "hashtag" in c.attrs["class"]:
                            sanitized += c.text + "[{}]".format(len(links))
                        else:
                            sanitized += "[{}]".format(len(links))
                    case "span":
                        assert type(c.a) == Tag
                        links.append(c.a.attrs["href"])
                        sanitized += c.a.text + "[{}]".format(len(links))
            else:
                sanitized += c.text
        sanitized += "\n"
    sanitized = sanitized[:len(sanitized)-1]
    manual_lines = sanitized.split("\n")

    lines = []
    for manual_line in manual_lines:
        width = get_terminal_size().columns
        while len(manual_line) > 0 and manual_line[len(manual_line)-1] == " ":
            manual_line = manual_line[:len(manual_line)-1]

        ls = [ manual_line ]
        while len(ls[len(ls)-1])+indent > width:
            l = ls.pop()
            ls += [l[:width-indent],l[width-indent:].removeprefix(" ")]
        lines += ls

    if len(lines) == 1:
        return ([lines[0]], links)
    else:
        return (lines, links)

def get_account_displayname(account: Account) -> str:
    return str(account.display_name or account.acct)

def sep(char="-"):
    width = get_terminal_size().columns
    print(char*width)

# Helps properly judge the width of emoji characters. Maybe not the most optimal/complete way to do that.
def display_string_width(string: str) -> int:
    width = len(string)
    for char in string:
        if east_asian_width(char) == "W":
            width += 1
    return width

def print_lr(left: str, right: str):
    width = get_terminal_size().columns
    middle = " "*(width-(display_string_width(left)+display_string_width(right)))
    print(left + middle + right)

def print_status(status: Status, indent: int = 0):
    assert type(status.account) == Account
    if type(status) == Reblog:
        print("󰑖 Reposted by {}".format(get_account_displayname(status.account)))
        assert type(status.post) == Post
        print_status(status.post, indent)
    else:
        assert type(status) == Post
        user_field = " " + get_account_displayname(status.account)
        url_field = status.url + " 󰖟"
        sep()
        print_lr(user_field, url_field)
        sep()
        (text, links) = sanitize_html(status.content, indent)
        if type(text) == str:
            print(text)
        else:
            for l in text:
                print(l)
        sep()
        if len(status.media) > 0:
            for media_item in status.media:
                display_media(media_item)
            sep()
        if len(links) > 0:
            for i in range(len(links)):
                print("[{}] {}".format(i+1, links[i]))
            sep()
    print("")

def print_ancestors(status: Status):
    if type(status) == Post:
        ancestors = status.get_ancestor_list();
        for ancestor in ancestors:
            print_status(ancestor)
    else:
        print_status(status)

def show_post_from_tour(p: str):
    status = get_post_from_tour_format(p)
    if isinstance(status, Status):
        print_status(status)
    else:
        print("Post {} not available in store".format(p))

def list_new():
    posts = read_tour()
    for p in posts:
        show_post_from_tour(p)

def tour():
    tour = read_tour()
    if len(tour) > 0:
        post = tour.pop()
        show_post_from_tour(post)
        write_current(post)
        write_tour(tour)
    else:
        print("Tour is empty!")

def thread():
    current = read_current()
    if current:
        post = get_post_from_tour_format(current)
        assert type(post) == Post
        if post:
            print_ancestors(post)
        p = post
        assert type(p) == Post
        def check_same_account(x):
            assert type(x) == Post
            return x.account==post.account
        descendants = list(filter(check_same_account, p.descendants))
        while len(descendants) > 0:
            d = descendants.pop()
            assert type(d) == Post
            print_status(d)
    else:
        print("No current post!")

def read_current() -> str:
    current_file = STATE_LOCATION / "current"
    current: str = ""
    if current_file.exists():
        with open(current_file, "r") as f:
            current = f.read()
    return current

def write_current(current: str):
    current_file = STATE_LOCATION / "current"
    with open(current_file, "w+") as f:
        f.write(current)

def main(argv):
    if len(argv) == 0:
        print("You need an argument for the reader!")
        exit(1)
    match argv[0]:
        case "list":
            list_new()
        case "tour":
            tour()
        case "thread":
            thread()
        case _:
            print("Invalid argument!")
