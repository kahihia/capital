import krakenex
import datetime
from decimal import Decimal

from .utils import Transaction, opposite_side


class Kraken(object):
    def __init__(self, key, secret, gdaxAPI):
        self._key = key
        self._secret = secret
        self._gdax = gdaxAPI

    # _client creates and returns a Kraken client
    def _client(self):
        return krakenex.API(key=self._key, secret=self._secret)

    # _to_timestamp converts the given string to a python timestamp object
    def _to_timestamp(self, ts):
        return datetime.datetime.utcfromtimestamp(ts)

    # getTransactions pulls all transactions from the Kraken API
    def getTransactions(self):
        client = self._client()
        trades = client.query_private('TradesHistory')

        transactions = {}
        for trade in trades['result']['trades'].values():
            pair = trade['pair'][1:]
            x_index = pair.index("X")
            currency = pair[:x_index].upper()
            base_currency = pair[x_index + 1:].upper()
            if currency not in transactions:
                transactions[currency] = []
            if base_currency not in transactions:
                transactions[base_currency] = []
            # first the currency that was traded
            trade_ts = self._to_timestamp(trade['time'])
            base_amount = trade['cost']
            base_price = self._gdax.getHistoryPrice(base_currency,
                                                    trade_ts)
            total = Decimal(base_amount) * Decimal(base_price)
            c_t = Transaction(
                side=trade['type'],
                currency=currency,
                created_at=trade_ts,
                amount=trade['vol'],
                total=total
            )
            transactions[currency].append(c_t)
            # now the base currency, something like btc or eth
            transactions[base_currency].append(Transaction(
                side=opposite_side(trade['type']),
                currency=base_currency,
                created_at=trade_ts,
                amount=base_amount,
                total=total
            ))
        return transactions
