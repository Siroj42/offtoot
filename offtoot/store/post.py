from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List
from datetime import datetime
from pathlib import Path
import json
from offtoot.store.config import STORAGE_LOCATION

from offtoot.store.account import Account
from offtoot.store.connection import get_mastodon_api
from offtoot.store.media import Media

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
            if status.ancestor:
                status.ancestor = Post.from_stub(status.ancestor)

            status.descendants = list(map(lambda d: Post.from_stub(d), status.descendants))
        assert type(status.account) == str
        status.account = Account.load(status.account)
        return status

    @classmethod
    def from_mastodon(cls, m, is_descendant=False, is_ancestor=False, ancestors=[]) -> "Status":
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
        media = []
        for media_attachment in m["media_attachments"]:
            media.append(Media.from_mastodon(media_attachment))

        ancestor = None
        descendants = []

        context = None
        if not is_descendant:
            context = fetch_context(id)
            ancestors = context["ancestors"]

            if len(ancestors) > 0:
                ancestor_m = ancestors.pop()
                ancestor = cls.from_mastodon(ancestor_m, is_ancestor=True)
                assert type(ancestor) == Post
            
        if not is_ancestor:
            if not context:
                context = fetch_context(id)
            descendants_m = context["descendants"]
            for d in descendants_m:
                descendant = cls.from_mastodon(d, is_descendant=True)
                descendants.append(descendant)

        post = Post(created_at, account, id, content, url, status, stats, media, ancestor, descendants)
        return post

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
    media: List[Media] = field(default_factory=list)
    ancestor: "Post | PostStub | None" = None
    descendants: "List[Post | PostStub]" = field(default_factory=list)

    @classmethod
    def from_stub(cls, stub) -> "Post":
        if type(stub) == PostStub:
            file = STORAGE_LOCATION / stub.acct / "posts" / "{}.json".format(stub.id)
            post = cls.load(file)
            assert type(post) == Post
            return post
        else:
            assert type(stub) == Post
            return stub

    def save(self):
        if self.ancestor:
            assert type(self.ancestor) == Post
            self.ancestor.save()
            self.ancestor = PostStub.from_post(self.ancestor)
        def save_d(d):
            d.save()
            return PostStub.from_post(d)

        self.descendants = list(map(save_d, self.descendants))
        super().save()

    def get_ancestor_list(self) -> "List[Post]":
        ancestors: List[Post] = [ self ]
        if self.ancestor:
            assert type(self.ancestor) == Post
            ancestors = self.ancestor.get_ancestor_list() + ancestors
        return ancestors

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

def fetch_context(id: int):
    m = get_mastodon_api()
    context = m.status_context(id)
    return context
