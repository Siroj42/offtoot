from offtoot.store.config import STATE_LOCATION, STORAGE_LOCATION
from offtoot.store.post import Status
from pathlib import Path
from typing import List

def read_list(location: Path) -> List[str]:
    l: List[str] = []
    if location.exists():
        with open(location, "r") as f:
            l = f.readlines()
    return l

def write_list(l: List[str], location: Path):
    location.parent.mkdir(parents=True, exist_ok=True)
    with open(location, "w+") as f:
        f.writelines(l)

def read_tour() -> List[str]:
    tour_file = STATE_LOCATION / "tour" # TODO: Deduplicate tour reading/writing
    return read_list(tour_file)

def write_tour(tour: List[str]):
    tour_file = STATE_LOCATION / "tour"
    write_list(tour, tour_file)

def read_fetch_later() -> List[str]:
    fetch_later_file = STATE_LOCATION / "fetch_later"
    return read_list(fetch_later_file)

def write_fetch_later(fetch_later: List[str]):
    fetch_later_file = STATE_LOCATION / "fetch_later"
    write_list(fetch_later, fetch_later_file)

def get_post_from_tour_format(p: str) -> Status | int:
    p = p.removesuffix("\n")
    acct = p.split("::")[0]
    id = p.split("::")[1]
    path = STORAGE_LOCATION / acct / "posts" / "{}.json".format(id)
    if path.exists():
        status = Status.load(path)
        return status
    return int(id)
