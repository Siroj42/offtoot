from dataclasses import dataclass
from dataclasses_json import dataclass_json
from pathlib import Path

from offtoot.store.config import STORAGE_LOCATION

@dataclass_json
@dataclass
class Account:
    acct: str
    url: str
    display_name: str = ""
    followers_count: int = 0
    following_count: int = 0

    @classmethod
    def get_acct_dir(cls, acct) -> Path:
        return STORAGE_LOCATION / acct

    @classmethod
    def load(cls, acct) -> "Account":
        file = cls.get_acct_dir(acct) / "data.json"
        with open(file, "r") as f:
            account_json = f.read()
        return cls.from_json(account_json) #type: ignore Type checker is bad with class annotators
    @classmethod
    def from_mastodon(cls, m) -> "Account":
        acct = m["acct"]
        url = m["url"]
        display_name = m["display_name"]
        followers_count = m["followers_count"]
        following_count = m["following_count"]
        return cls(acct, url, display_name, followers_count, following_count)

    def save(self):
        self.get_dir().mkdir(parents=True, exist_ok=True)
        file = self.get_dir() / "data.json"
        account_json = self.to_json() #type: ignore Type checker is bad with class annotators

        with open(file, "w+") as f:
            f.write(account_json)

    def get_server(self) -> str | None:
        acct_split = self.acct.split("@")
        if len(acct_split) < 2:
            return None # TODO: This means that the user and this account share the server
        return acct_split[1]

    def get_dir(self) -> Path:
        return Account.get_acct_dir(self.acct)
