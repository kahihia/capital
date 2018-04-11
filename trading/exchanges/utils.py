from datetime import datetime
from decimal import Decimal


class Transaction(object):
    def __init__(self, side, currency, created_at, amount, total):
        self.side = side
        self.currency = currency
        self.created_at = created_at
        self.amount = Decimal(amount)
        self.total = Decimal(total)

    # price returns the price per share of the Transaction
    @property
    def price(self):
        return self.total / self.amount


# opposite_side returns the opposite of the given side
def opposite_side(side):
    if side == 'sell':
        return 'buy'
    return 'sell'
