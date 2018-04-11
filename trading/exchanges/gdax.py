import datetime
from decimal import Decimal
import gdax
import time

from .utils import Transaction


class GDAXPrivate(object):
    def __init__(self, key, secret, passphrase):
        self._passphrase = passphrase
        self._key = key
        self._secret = secret

    # _client creates and returns a GDAX client
    def _get_client(self):
        return gdax.AuthenticatedClient(self._key, self._secret,
                                        self._passphrase)

    # _to_timestamp converts the given string to a python timestamp object
    def _to_timestamp(self, ts_string):
        return datetime.datetime.strptime(ts_string[:19], "%Y-%m-%dT%H:%M:%S")

    # getTransactions pulls all transactions from the GDAX API
    def getTransactions(self):
        client = self._get_client()
        transactions = {}
        fills = client.get_fills()
        for page in fills:
            valid_fills = (fill for fill in page if fill['settled'])
            for fill in valid_fills:
                dash_index = fill['product_id'].index("-")
                currency = fill['product_id'][:dash_index].upper()
                if currency not in transactions:
                    transactions[currency] = []
                total = Decimal(fill['size']) * Decimal(fill['price'])
                if fill['side'] == 'buy':
                    total += Decimal(fill['fee'])
                else:
                    total -= Decimal(fill['fee'])
                transactions[currency].append(Transaction(
                    side=fill['side'],
                    currency=currency,
                    created_at=self._to_timestamp(fill['created_at']),
                    amount=fill['size'],
                    total=total
                ))
        return transactions


class GDAXPublic(object):
    def __init__(self):
        self._client = None

    # _client creates and returns a GDAX public client
    def _get_client(self):
        if not self._client:
            self._client = gdax.PublicClient()
        return self._client

    # getHistoryPrice the price for the specified currency for a given
    # timestamp from GDAX
    def getHistoryPrice(self, currency, ts):
        client = self._get_client()
        start = ts - datetime.timedelta(seconds=ts.second)
        end = ts.replace(second=59)
        while True:
            data = client.get_product_historic_rates(currency + '-USD',
                                                     start=start.isoformat(),
                                                     end=end.isoformat(),
                                                     granularity=60)
            if type(data) == list:
                return data[0][4]
            print("Called GDAX public API too often, sleeping for .5 seconds")
            time.sleep(.5)
