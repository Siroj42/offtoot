from dataclasses import dataclass
from pathlib import Path
from dataclasses_json import dataclass_json
from enum import Enum
import requests

from offtoot.store.config import MEDIA_SIZE, STORAGE_LOCATION

# Maybe for an option that only syncs below a certain threshold? i.e. it might download images, gifs and audio, but stay away from videos and unknown files for bandwidth reasons
class MediaType(Enum):
    IMAGE = 0
    GIFV = 1
    AUDIO = 2
    VIDEO = 3
    UNKNOWN = 4

    @classmethod
    def from_mastodon(cls, t) -> "MediaType":
        match t:
            case "image":
                return MediaType.IMAGE
            case "gifv":
                return MediaType.GIFV
            case "audio":
                return MediaType.AUDIO
            case "video":
                return MediaType.VIDEO
            case "unknown" | _:
                return MediaType.UNKNOWN

def get_media_type_name(media_type: MediaType):
    match media_type.name:
        case "IMAGE":
            return "image"
        case "GIFV":
            return "animated gif"
        case "AUDIO":
            return "audio"
        case "VIDEO":
            return "video"
        case "UNKNOWN":
            return "unknown"

# This should allow for selectively downloading a certain quality of image, or accessing it from the original host
@dataclass_json
@dataclass
class MediaUrl:
    local: str
    preview: str
    remote: str

@dataclass_json
@dataclass
class Media:
    id: int
    description: str
    media_type: MediaType
    url: MediaUrl

    @classmethod
    def from_mastodon(cls, attachment) -> "Media":
        m = Media(
            id = attachment["id"],
            description = attachment["description"] or "",
            media_type = MediaType.from_mastodon(attachment["type"]),
            url = MediaUrl(
                local = attachment["url"],
                preview = attachment["preview_url"],
                remote = attachment["remote_url"],
            ),
        )
        m.download()
        return m

    def get_path(self) -> Path:
        p = STORAGE_LOCATION
        domain = self.url.remote.split("://")[1]
        domain = domain.split("/")[0]
        file_ending = self.url.remote.split(".").pop()
        filename = "{}.{}".format(self.id, file_ending)
        p = p / domain / filename
        return p

    def download(self):
        path = self.get_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        match MEDIA_SIZE:
            case "preview":
                url = self.url.preview
            case "local":
                url = self.url.local
            case "remote":
                url = self.url.remote
        download_media(url, path)


def download_media(url: str, path: Path):
    if not path.is_file():
        print("Downloading media from {}".format(url))
        r = requests.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
