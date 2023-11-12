from typing import List
from offtoot.store.config import STATE_LOCATION
from offtoot.store.connection import get_mastodon_api
from offtoot.store.post import Status

def main(argv: List[str]):
    m = get_mastodon_api()

    since_id_file = STATE_LOCATION / "since_id"
    since_id: int | None = None
    if since_id_file.exists():
        with open(since_id_file, "r") as f:
            since_id = int(f.read())

    tour_file = STATE_LOCATION / "tour"
    tour: List[str] = []
    if tour_file.exists():
        with open(tour_file, "r") as f:
            tour = f.readlines()

    home_timeline = m.timeline_home(since_id=since_id)
    statuses: List[Status] = []
    for x in home_timeline:
        status = Status.from_mastodon(x)
        statuses.append(status)

    if len(statuses) > 0:
        since_id = statuses[0].id
        with open(since_id_file, "w") as f:
            f.write(str(since_id))

    for status in statuses:
        status.save()
        tour.append("{}::{}\n".format(status.get_acct(), status.id))

    with open(tour_file, "w+") as f:
        f.writelines(tour)
