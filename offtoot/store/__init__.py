from typing import List
from offtoot.store.config import STATE_LOCATION
from offtoot.store.connection import get_mastodon_api, mastodon_login, mastodon_logout
from offtoot.store.post import Status
from offtoot.store.lists import read_tour, write_tour

def sync():
    m = get_mastodon_api()
    since_id_file = STATE_LOCATION / "since_id"
    since_id: int | None = None
    if since_id_file.exists():
        with open(since_id_file, "r") as f:
            since_id = int(f.read())

    tour = read_tour()

    print("Fetching home timeline...")
    home_timeline = m.timeline_home(since_id=since_id)
    statuses: List[Status] = []
    for x in home_timeline:
        print("Fetching status {}/{}".format(len(statuses)+1, len(home_timeline)))
        status = Status.from_mastodon(x)
        statuses.append(status)

    if len(statuses) > 0:
        since_id = statuses[0].id
        with open(since_id_file, "w") as f:
            f.write(str(since_id))

    to_add_to_tour = []
    for status in statuses:
        status.save()
        to_add_to_tour.append("{}::{}\n".format(status.get_acct(), status.id))

    tour += to_add_to_tour

    write_tour(tour)

def main(argv: List[str]):
    if len(argv) == 0:
        print("You need an argument for the store!")
        exit(1)

    match argv[0]:
        case "sync":
            sync()
        case "login":
            if len(argv) < 2:
                print("You need to provide the url of your mastodon server!")
                exit(1)
            mastodon_login(argv[1])
        case "logout":
            print("You are trying to log out of your account.")
            print("You will have to reauthenticate.")
            confirmation = input("Log out? (y/N): ").lower() == "y"
            if confirmation:
                mastodon_logout()
                print("Logged out.")
            print("Logout aborted.")
        case _:
            print("Invalid argument")
