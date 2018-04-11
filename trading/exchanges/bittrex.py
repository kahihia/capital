import codecs
import csv
import datetime
from decimal import Decimal

from .utils import Transaction, opposite_side


class Bittrex(object):
    def __init__(self, csv_file, gdaxAPI):
        self._csv_file = csv_file
        self._gdax = gdaxAPI

    # _to_timestamp converts the given string to a python timestamp object
    def _to_timestamp(self, ts_string):
        return datetime.datetime.strptime(ts_string, "%m/%d/%Y %I:%M:%S %p")

    # getTransactions pulls all transactions from the GDAX API
    def getTransactions(self):
        transactions = {}
        with codecs.open(self._csv_file, 'rb', 'utf-16le') as f:
            reader = csv.DictReader(f)
            for transaction in reader:
                product = transaction['Exchange']
                dash_index = product.index('-')
                currency = product[dash_index + 1:].upper()
                base_currency = product[:dash_index].upper()
                if currency not in transactions:
                    transactions[currency] = []
                if base_currency not in transactions:
                    transactions[base_currency] = []
                # first the currency that was traded
                underscore_index = transaction['Type'].index('_')
                transaction_type = transaction['Type'][underscore_index + 1:]
                transaction_type = transaction_type.lower()
                transaction_ts = self._to_timestamp(transaction['Closed'])
                # very badly named, this is actually the Cost/ Proceeds in the
                # base currency without considering the fees
                amount = transaction['Quantity']
                base_amount = Decimal(transaction['Price'])
                if transaction_type == 'buy':
                    base_amount += Decimal(transaction['CommissionPaid'])
                else:
                    base_amount -= Decimal(transaction['CommissionPaid'])
                base_price = self._gdax.getHistoryPrice(base_currency,
                                                        transaction_ts)
                total = base_amount * Decimal(base_price)
                c_t = Transaction(
                    side=transaction_type,
                    currency=currency,
                    created_at=transaction_ts,
                    amount=amount,
                    total=total
                )
                transactions[currency].append(c_t)
                # now the base currency, something like btc or eth
                transactions[base_currency].append(Transaction(
                    side=opposite_side(transaction_type),
                    currency=base_currency,
                    created_at=transaction_ts,
                    amount=base_amount,
                    total=total
                ))
        return transactions
