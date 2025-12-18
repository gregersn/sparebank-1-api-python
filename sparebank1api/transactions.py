from datetime import date
from typing import TYPE_CHECKING, Any, Literal
from .apierror import APIError

if TYPE_CHECKING:
    from .client import BaseAPI


class TransactionsAPI:
    API_VERSION: str = "application/vnd.sparebank1.v1+json; charset=utf-8"
    api: BaseAPI

    def __init__(self, api: BaseAPI):
        self.api = api

    def list_transactions(
        self,
        account_keys: list[str],
        from_date: date | None = None,
        to_date: date | None = None,
        row_limit: int | None = None,
        transaction_source: list[Literal["RECENT", "HISTORIC", "ALL"]] | None = None,
        enrich_with_payment_details: bool | None = None,
    ):
        """GET /transactions - List transactions entities"""
        if account_keys is str:
            account_keys = [account_keys]
        params = [("accountKey", k) for k in account_keys]
        if from_date:
            params.append(("fromDate", from_date.strftime("%Y-%m-%d")))
        if to_date:
            params.append(("toDate", to_date.strftime("%Y-%m-%d")))
        if row_limit:
            params.append(("rowLimit", str(row_limit)))
        if transaction_source:
            params.append(("transactionSource", ", ".join(transaction_source)))
        if enrich_with_payment_details is not None:
            params.append(
                ("enrichWithPaymentDetails", str(enrich_with_payment_details).lower())
            )
        response = self.api.getApi(
            "transactions", params=params, headers={"Accept": self.API_VERSION}
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def export_transactions_to_csv(
        self, account_key: str, from_date: date, to_date: date
    ):
        """GET /transactions/export - Exports booked transactions to CSV for a given period"""
        response = self.api.getApi(
            "transactions/export",
            params={
                "accountKey": account_key,
                "fromDate": from_date,
                "toDate": to_date,
            },
            headers={"Accept": "application/csv;charset=UTF-8"},
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.content

    def list_classified_transactions(
        self,
        account_keys: list[str],
        from_date: date | None = None,
        to_date: date | None = None,
        row_limit: int | None = None,
        transaction_source: list[Literal["RECENT", "HISTORIC", "ALL"]] | None = None,
        enrich_with_payment_details: bool | None = None,
        enrich_with_merchant_logo: bool | None = None,
    ):
        """GET /transactions/classified - List transactions entities with classification"""
        if account_keys is str:
            account_keys = [account_keys]
        params = [("accountKey", k) for k in account_keys]
        if from_date:
            params.append(("fromDate", from_date.strftime("%Y-%m-%d")))
        if to_date:
            params.append(("toDate", to_date.strftime("%Y-%m-%d")))
        if row_limit:
            params.append(("rowLimit", str(row_limit)))
        if transaction_source:
            params.append(("transactionSource", ", ".join(transaction_source)))
        if enrich_with_payment_details is not None:
            params.append(
                ("enrichWithPaymentDetails", str(enrich_with_payment_details).lower())
            )
        if enrich_with_merchant_logo is not None:
            params.append(
                ("enrichWithMerchantLogo", str(enrich_with_merchant_logo).lower())
            )
        response = self.api.getApi(
            "transactions/classified",
            params=params,
            headers={"Accept": self.API_VERSION},
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_transaction_details(self, transaction_id: str):
        response = self.api.getApi(
            f"transactions/{transaction_id}/details",
            headers={"Accept": self.API_VERSION},
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()

    def get_classified_transaction_details(
        self, transaction_id: str, enrich_with_merchant_data: Any = None
    ):
        response = self.api.getApi(
            f"transactions/{transaction_id}/details/classified",
            params=(
                enrich_with_merchant_data is not None
                if {"enrichWithMerchantData": enrich_with_merchant_data}
                else None
            ),
            headers={"Accept": self.API_VERSION},
        )
        if not response.ok:
            raise APIError(response.status_code, response.text)
        return response.json()
