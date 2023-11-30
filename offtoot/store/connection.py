from mastodon import Mastodon
from getpass import getpass
from offtoot.store.config import APP_LOCATION, TOKEN_LOCATION, URL_LOCATION

def get_mastodon_api() -> Mastodon:
    with open(TOKEN_LOCATION) as f:
        token = f.read().removesuffix("\n")
    with open(URL_LOCATION) as f:
        url = f.read().removesuffix("\n")
    m = Mastodon(api_base_url=url, access_token=token)
    return m

def mastodon_login(base_url: str):
    TOKEN_LOCATION.parent.mkdir(parents=True, exist_ok=True)
    Mastodon.create_app(
        "offtoot",
        api_base_url = base_url,
        to_file = APP_LOCATION,
    )
    with open(APP_LOCATION) as f:
        lines = f.readlines()
        client_id = lines[0].removesuffix("\n")
        client_secret = lines[1].removesuffix("\n")

    m = Mastodon(
        api_base_url = base_url,
        client_id = client_id,
        client_secret = client_secret,
    )
    login_url = m.auth_request_url()
    print("Log in at: {}".format(login_url))
    code = getpass("Input the code you get here: ")
    
    token = m.log_in(code=code)
    URL_LOCATION.parent.mkdir(parents=True, exist_ok=True)
    with open(URL_LOCATION, "w+") as f:
        f.write(base_url)
    TOKEN_LOCATION.parent.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_LOCATION, "w+") as f:
        f.write(token)

def mastodon_logout():
    m = get_mastodon_api()
    m.revoke_access_token()
    APP_LOCATION.unlink()
    TOKEN_LOCATION.unlink()
    URL_LOCATION.unlink()
