import hashlib
import os
import time
from urllib import parse

import flask
import requests

AUTH_URL = "https://discord.com/api/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"
TOKEN_REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"
USER_ENDPOINT = "https://discord.com/api/users/@me"
REDIRECT_URL = os.environ["AUTH_REDIRECT_URL"]
CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
CLIENT_SECRET = os.environ["DISCORD_CLIENT_SECRET"]


def create_state() -> str:
    return hashlib.blake2b(
        f"{time.perf_counter_ns()}".encode("utf-8"), digest_size=12
    ).hexdigest()


def get_auth_url() -> tuple:
    state = create_state()
    return (
        AUTH_URL
        + "?"
        + parse.urlencode(
            {
                "response_type": "code",
                "client_id": CLIENT_ID,
                "scope": "identify",
                "state": state,
                "redirect_uri": REDIRECT_URL,
                "prompt": "consent",
            }
        )
    ), state


def exchange_code(request: flask.Request) -> tuple:
    code = request.args["code"]
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URL,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    resp.raise_for_status()
    tokens = resp.json()

    resp = requests.get(
        USER_ENDPOINT, headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    resp.raise_for_status()
    user_info = resp.json()

    return user_info, tokens


def refresh_token(token: str) -> dict:
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": token,
        },
    )
    resp.raise_for_status()
    return resp.json()
