from offtoot.store.config import STATE_LOCATION
from typing import List

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
