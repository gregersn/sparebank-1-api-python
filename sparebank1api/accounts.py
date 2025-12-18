from typing import TYPE_CHECKING, Any
from .apierror import (
    APIError,
)

if TYPE_CHECKING:
    from .client import BaseAPI


class AccountsAPI:
    API_VERSION = "application/vnd.sparebank1.v5+json; charset=utf-8"
    api: BaseAPI

    def __init__(
        self, api: BaseAPI
    ):  # Remove type hint to avoid circular import at runtime
        self.api = api

    def list_accounts(
        self,
        include_nok_accounts: bool = True,
        include_currency_accounts: bool = False,
        include_bsu_accounts: bool = False,
        include_creditcard_accounts: bool = False,
        include_ask_accounts: bool = False,
        include_pension_accounts: bool = False,
    ) -> list[dict[str, Any]]:
        response = self.api.getApi(
            "accounts",
            params={
                "includeNokAccounts": include_nok_accounts,
                "includeCurrencyAccounts": include_currency_accounts,
                "includeBsuAccounts": include_bsu_accounts,
                "includeCreditcardAccounts": include_creditcard_accounts,
                "includeAskAccounts": include_ask_accounts,
                "includePensionAccounts": include_pension_accounts,
            },
            headers={"Accept": self.API_VERSION},
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json().get("accounts", [])

    def get_account_keys(self, account_numbers: list[str]):
        response = self.api.getApi(
            "accounts/keys",
            params=[("accountNumber", n) for n in account_numbers],
            headers={"Accept": self.API_VERSION},
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_account_balance(self, account_number: str):
        response = self.api.postApi(
            "accounts/balance",
            json={"accountNumber": account_number},
            headers={"Content-Type": self.API_VERSION, "Accept": self.API_VERSION},
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_default_account(self):
        response = self.api.getApi(
            "accounts/default", headers={"Accept": self.API_VERSION}
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_account(self, account_key: str):
        response = self.api.getApi(
            f"accounts/{account_key}", headers={"Accept": self.API_VERSION}
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_account_roles(self, account_key: str):
        response = self.api.getApi(
            f"accounts/{account_key}/roles", headers={"Accept": self.API_VERSION}
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_account_details(self, account_key: str):
        response = self.api.getApi(
            f"accounts/{account_key}/details", headers={"Accept": self.API_VERSION}
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()
