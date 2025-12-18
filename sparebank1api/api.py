from .client import BaseAPI
from .accounts import AccountsAPI
from .child_accounts import ChildAccountsAPI
from .transactions import TransactionsAPI
from .transfers import TransfersAPI

from .config import Config


class SpareBank1API:
    accounts: AccountsAPI
    transactions: TransactionsAPI
    transfers: TransfersAPI
    child_accounts: ChildAccountsAPI
    _base: BaseAPI

    def __init__(self, config: Config):
        self.config = config
        self._base = BaseAPI(config)
        self.accounts = AccountsAPI(self._base)
        self.transactions = TransactionsAPI(self._base)
        self.transfers = TransfersAPI(self._base)
        self.child_accounts = ChildAccountsAPI(self._base)

    def authenticate(self):
        self._base.authenticate()
