from typing import TYPE_CHECKING
from .apierror import APIError

if TYPE_CHECKING:
    from .client import BaseAPI


class ChildAccountsAPI:
    API_VERSION: str = "application/vnd.sparebank1.v5+json; charset=utf-8"

    def __init__(self, api: BaseAPI):
        self.api = api

    def get_child_account(self, child_id: str):
        response = self.api.getApi(
            f"accounts/child/{child_id}", headers={"Accept": self.API_VERSION}
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()
