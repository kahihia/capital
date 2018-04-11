from .config_reader import ConfigReader


class CoinsManual(object):
    holdings = []

    def __init__(self):
        self.holdings = []
        reader = ConfigReader("coins_manual.txt", 2)
        for line in reader.fields:
            if len(line) >= 2:
                self.holdings.append({"symbol": line[0], "amount": float(line[1])})
        return

    # get all manually entered balances
    def get_all_manual_balances(self, portfolio):
        for holding in self.holdings:
            print('Manual holding entry: ' + str(round(holding["amount"], 4)) + ' ' + holding["symbol"])
            portfolio.have_coins(holding["symbol"], holding["amount"], "manual")
        return
