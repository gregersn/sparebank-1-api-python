from datetime import datetime
from genericpath import exists
import io
import json
from time import time
from typing import Any, TypedDict, cast
import requests
import secrets
from urllib.parse import urlencode, urlparse, parse_qs

from .config import Config
from .server import wait_for_callback


class Token(TypedDict):
    access_token: str
    expires_at: int
    refresh_token: str


class ResponseToken(TypedDict):
    access_token: str
    expires_in: int
    refresh_token: str


class BaseAPI:
    BASE_URL: str = "https://api.sparebank1.no"
    AUTH_URL: str = f"{BASE_URL}/oauth/authorize"
    TOKEN_URL: str = f"{BASE_URL}/oauth/token"
    API_URL: str = f"{BASE_URL}/personal/banking"
    config: Config
    _last_state: str | None

    token: Token | None = None

    def __init__(self, config: Config):
        self.config = config
        self._last_state = None

    def build_headers(self, additional_headers: dict[str, str]) -> dict[str, str]:
        if not self.ensure_token():
            raise
        assert self.token
        headers = {
            "Authorization": f"Bearer {self.token['access_token']}",
            "User-Agent": "SpareBank1API/1.0",
        }
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def get(
        self, url: str, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> requests.Response:
        if headers is None:
            headers = {}
        return requests.get(url, headers=self.build_headers(headers), **kwargs)

    def post(
        self, url: str, headers: dict[str, str] | None = None, **kwargs: Any
    ) -> requests.Response:
        if headers is None:
            headers = {}

        return requests.post(url, headers=self.build_headers(headers), **kwargs)

    def getApi(self, url: str, **kwargs: Any) -> requests.Response:
        return self.get(f"{self.API_URL}/{url}", **kwargs)

    def postApi(self, url: str, **kwargs: Any) -> requests.Response:
        return self.post(f"{self.API_URL}/{url}", **kwargs)

    def authenticate(self):
        if exists("token.json"):
            with io.open("token.json", "r", encoding="utf-8") as f:
                self.token = json.load(f)
                assert self.token
                print(
                    f"Imported token, valid until {datetime.fromtimestamp(self.token['expires_at'])}"
                )
                _ = self.ensure_token()
                return

        url = self.get_authorization_url()
        print(f"Go to the following URL to authorize: {url}")
        redirect_response = wait_for_callback(
            urlparse(self.config.redirect_uri).port or 80
        )["path"]
        self.fetch_token(redirect_response)

    def set_token(self, response: requests.Response):
        token = cast(ResponseToken, response.json())
        expiry = response.headers.get("date")
        expires_at = (
            datetime.strptime(expiry, "%a, %d %b %Y %H:%M:%S GMT")
            if expiry
            else datetime.now()
        )
        self.token = {
            "access_token": token.get("access_token"),
            "expires_at": int(token.get("expires_in", 0)) + int(expires_at.timestamp()),
            "refresh_token": token.get("refresh_token"),
        }

        print(
            f"New token, valid until {datetime.fromtimestamp(self.token['expires_at'])}"
        )
        with io.open("token.json", "w", encoding="utf-8") as f:
            _ = f.write(
                json.dumps(
                    self.token,
                )
            )

    def get_authorization_url(self):
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "state": state,
            "finInst": self.config.fin_inst,
        }
        url = f"{self.AUTH_URL}?{urlencode(params)}"
        self._last_state = state
        return url

    def fetch_token(self, authorization_response: str):
        # Extract code and state from the redirect URL
        parsed = urlparse(authorization_response)
        query = parse_qs(parsed.query)
        code = query.get("code", [None])[0]
        state = query.get("state", [None])[0]
        if not code or not state:
            raise ValueError("Missing code or state in authorization response.")
        if state != self._last_state:
            raise ValueError("State mismatch. Possible CSRF attack.")
        response = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.config.redirect_uri,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
            },
        )
        response.raise_for_status()
        self.set_token(response)

    def refresh_token(self):
        assert self.token
        response = requests.post(
            self.TOKEN_URL,
            data={
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "refresh_token": self.token.get("refresh_token"),
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()
        self.set_token(response)

    def ensure_token(self, refresh_threshold: int = 60) -> bool:
        """Check if the current token is valid."""
        if (
            not self.token
            or "access_token" not in self.token
            or "expires_at" not in self.token
        ):
            raise Exception("Not authenticated. Please authenticate first.")

        if int(time()) >= self.token["expires_at"] - refresh_threshold:
            self.refresh_token()
            if not self.token or "access_token" not in self.token:
                raise Exception("Failed to refresh token. Please re-authenticate.")

        return True
