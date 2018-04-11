from datetime import timedelta

from .utils import AssetSale


# _extract_transactions pulls all transactions from the specified exchanges and
# groups them by currencies
def _extract_transactions(exchanges):
    transactions = {}
    for exchange in exchanges:
        for key, values in exchange.getTransactions().items():
            if key not in transactions:
                transactions[key] = []
            transactions[key] += values
    return transactions


# _process_sale calculates the gain or loss of the specified sale considering
# the given lots. It also applies a wash sale if necessary.
def _process_sale(sale, lots):
    asset_sales = []
    while sale.amount > 0:
        if not lots:
            print(sale.side, sale.currency, sale.created_at, sale.amount, sale.total)
        lot = max(lots, key=lambda lot: lot.price)
        asset_sale = AssetSale(
            property=sale.currency,
            aquired_at=lot.created_at,
            sold_at=sale.created_at
        )
        # the chosen lot is being used up completley for this sale
        if lot.amount <= sale.amount:
            proceeds = lot.amount / sale.amount * sale.total
            asset_sale.proceeds = proceeds
            asset_sale.basis = lot.total
            lots.remove(lot)
            sale.amount -= lot.amount
            sale.total -= proceeds
        # only part of the chosen lot is used for this sale
        else:
            basis = sale.amount / lot.amount * lot.total
            asset_sale.proceeds = sale.total
            asset_sale.basis = basis
            lot.amount -= sale.amount
            lot.total -= basis
            sale.amount = 0
        asset_sales.append(asset_sale)
    return asset_sales


# calculate_gains_losses calculates the gains and losses for all the
# transactions from the given exchanges
def calculate_gains_losses(exchanges):
    transactions = _extract_transactions(exchanges)

    asset_sales = []
    leftover_lots = []
    for currency, c_transactions in transactions.items():
        lots = []
        c_transactions.sort(key=lambda transaction: transaction.created_at)
        for transaction in c_transactions:
            if transaction.side == 'buy':
                lots.append(transaction)
            elif transaction.side == 'sell':
                asset_sales += _process_sale(transaction, lots)
        leftover_lots += lots
    return asset_sales, leftover_lots
