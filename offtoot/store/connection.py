from mastodon import Mastodon
from offtoot.store.config import TOKEN_LOCATION, URL_LOCATION

def get_mastodon_api() -> Mastodon:
    with open(TOKEN_LOCATION) as f:
        token = f.read().removesuffix("\n")
    with open(URL_LOCATION) as f:
        url = f.read().removesuffix("\n")
    m = Mastodon(api_base_url="https://troet.cafe", access_token=token)
    return m
