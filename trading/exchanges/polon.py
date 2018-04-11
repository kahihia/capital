import datetime
from decimal import Decimal
from ccxt import poloniex

from .utils import Transaction, opposite_side

PRECISION = 8


class Poloniex(object):
    def __init__(self, key, secret, gdaxAPI):
        self._key = key
        self._secret = secret
        self._gdax = gdaxAPI

    # _client creates and returns a Poloniex client
    def _client(self):
        return poloniex({'api_key':self._key, 'secret':self._secret})

    # _to_timestamp converts the given string to a python timestamp object
    def _to_timestamp(self, ts_string):
        return datetime.datetime.strptime(ts_string, "%Y-%m-%d %H:%M:%S")

    # getTransactions pulls all transactions from the GDAX API
    def getTransactions(self):
        client = self._client()
        transactions = {}
        start_date = datetime.datetime(datetime.datetime.now().year, 1, 1)
        fills = client.fetch_my_trades()
        for key, history in fills.items():
            underscore_index = key.index("_")
            currency = key[underscore_index + 1:].upper()
            base_currency = key[:underscore_index].upper()
            if currency not in transactions:
                transactions[currency] = []
            if base_currency not in transactions:
                transactions[base_currency] = []
            for transaction in history:
                # first the currency that was traded
                transaction_ts = self._to_timestamp(transaction['date'])
                amount = Decimal(transaction['amount'])
                base_amount = amount * Decimal(transaction['rate'])
                if transaction['type'] == 'buy':
                    fee = Decimal(transaction['fee']) * amount
                    amount -= round(fee, PRECISION)
                else:
                    fee = Decimal(transaction['fee']) * base_amount
                    base_amount -= round(fee, PRECISION)
                base_price = self._gdax.getHistoryPrice(base_currency,
                                                        transaction_ts)
                total = base_amount * Decimal(base_price)
                transactions[currency].append(Transaction(
                    side=transaction['type'],
                    currency=currency,
                    created_at=transaction_ts,
                    amount=amount,
                    total=total
                ))
                # now the base currency, something like btc or eth
                transactions[base_currency].append(Transaction(
                    side=opposite_side(transaction['type']),
                    currency=base_currency,
                    created_at=transaction_ts,
                    amount=base_amount,
                    total=total
                ))
        return transactions
