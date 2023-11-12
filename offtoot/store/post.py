from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import datetime
from pathlib import Path
import json
from offtoot.store.config import STORAGE_LOCATION

from offtoot.store.account import Account

@dataclass_json
@dataclass
class PostInteractionStats:
    favourites: int = 0
    reblogs: int = 0
    replies: int = 0

@dataclass_json
@dataclass
class PostInteraction:
    favourite: bool = False
    reblogged: bool = False
    bookmarked: bool = False

@dataclass_json
@dataclass
class Status:
    created_at: datetime
    account: Account | str
    id: int

    @classmethod
    def load(cls, file: Path) -> "Status":
        with open(file, "r") as f:
            status_json = f.read()
        if "post" in json.loads(status_json):
            status = Reblog.from_json(status_json) #type: ignore Type checker is bad with class annotators
            assert type(status.post) == PostStub
            status.post = Post.from_stub(status.post)
        else:
            status = Post.from_json(status_json) #type: ignore Type checker is bad with class annotators
        assert type(status.account) == str
        status.account = Account.load(status.account)
        return status

    @classmethod
    def from_mastodon(cls, m) -> "Status":
        created_at = m["created_at"]
        account = Account.from_mastodon(m["account"])
        id = m["id"]
        if m["reblog"]:
            post = cls.from_mastodon(m["reblog"])
            assert type(post) == Post
            return Reblog(created_at, account, id, post)
        content = m["content"]
        url = m["url"]
        status = PostInteraction(
            favourite = m["favourited"],
            bookmarked = m["bookmarked"],
            reblogged = m["reblogged"],
        )
        stats = PostInteractionStats(
            favourites = m["favourites_count"],
            reblogs = m["reblogs_count"],
            replies = m["replies_count"],
        )
        return Post(created_at, account, id, content, url, status, stats)

    def save(self):
        assert type(self.account) == Account
        account_dir = self.account.get_dir()
        self.account.save()
        (account_dir / "posts").mkdir(parents=True, exist_ok=True)
        file = account_dir / "posts" / "{}.json".format(str(self.id))
        self.save_to(file)

    def save_to(self, file: Path):
        assert type(self.account) == Account
        self.account = self.account.acct
        status_json = self.to_json() #type: ignore Type checker is bad with class annotators
        with open(file, "w+") as f:
            f.write(status_json)

    def get_acct(self) -> str:
        if type(self.account) == Account:
            return self.account.acct
        elif type(self.account) == str:
            return self.account
        return ""

@dataclass
class Post(Status):
    content: str = ""
    url: str = ""
    status: PostInteraction = field(default_factory=PostInteraction)
    stats: PostInteractionStats = field(default_factory=PostInteractionStats)

    @classmethod
    def from_stub(cls, stub: "PostStub") -> "Post":
        file = STORAGE_LOCATION / stub.acct / "posts" / "{}.json".format(stub.id)
        post = cls.load(file)
        assert type(post) == Post
        return post

@dataclass
class PostStub():
    acct: str
    id: int

    @classmethod
    def from_post(cls, post: Post):
        return cls(acct=post.get_acct(), id=post.id)

@dataclass
class Reblog(Status):
    post: Post | PostStub | None = None

    def save(self):
        if type(self.post) == Post:
            self.post.save()
            self.post = PostStub.from_post(self.post)
        super().save()

