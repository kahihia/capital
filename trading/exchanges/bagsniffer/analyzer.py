from .config_reader import ConfigReader
import time
import json

class Analyzer(object):
    transactions = []
    override = {}
    coin_data = None
    timestamp = None

    def __init__(self, coin_data):
        self.transactions = []
        self.coin_data = coin_data
        self.timestamp = time.time()
        self.override = {}
        reader = ConfigReader("transactions_override.txt", 2)
        for line in reader.fields:
            if len(line) >= 2:
                self.override[int(line[0])] = float(line[1])
        return

    def is_extreme_dust(self, symbol, amount):
        # Ignore BTC transactions below 1 sat
        if symbol == 'BTC' and amount < 1e-8:
            return True
        # Ignore ETH transactions below 1 Mwei (lovelace), and other tiny transactions
        # TODO: this is a tad crude, but so far, I don't know of any coins where such tiny amounts would be relevant
        if amount < 1e-12:
            return True
        return False

    def report_buy(self, symbol, balance):
        if self.is_extreme_dust(symbol, balance):
            return
        price = balance * self.coin_data.get_btc_price(symbol)
        print("Found buy of " + str(balance) + " " + symbol + " for " + str(price) + " BTC")
        self.transactions.append({"ID": len(self.transactions) + 1, "type": "buy", "symbol": symbol, "balance": balance, "price": price, "time": self.timestamp})
        return

    def report_stake(self, symbol, balance):
        if self.is_extreme_dust(symbol, balance):
            return
        print("Found stake of " + str(balance) + " " + symbol)
        self.transactions.append({"ID": len(self.transactions) + 1, "type": "stake", "symbol": symbol, "balance": balance, "price": 0.0, "time": self.timestamp})
        return

    def report_sell(self, symbol, balance):
        if self.is_extreme_dust(symbol, balance):
            return
        price = balance * self.coin_data.get_btc_price(symbol)
        print("Found sell of " + str(balance) + " " + symbol + " for " + str(price) + " BTC")
        self.transactions.append({"ID": len(self.transactions) + 1, "type": "sell", "symbol": symbol, "balance": balance, "price": price, "time": self.timestamp})
        return

    def find_transactions(self, past_portfolio, current_portfolio):
        print("Analyzing transactions...")
        try:
            with open('history/transactions.json', mode='r') as transactions_file:
                self.transactions = json.loads(transactions_file.read())
        except:
            self.transactions = []
        for symbol in past_portfolio:
            if symbol in current_portfolio:
                if current_portfolio[symbol]["balance"] > past_portfolio[symbol]["balance"]:
                    amount = current_portfolio[symbol]["balance"] - past_portfolio[symbol]["balance"]
                    if amount * 100 <= past_portfolio[symbol]["balance"]:
                        self.report_stake(symbol, amount)
                    else:
                        self.report_buy(symbol, amount)
                elif current_portfolio[symbol]["balance"] < past_portfolio[symbol]["balance"]:
                    self.report_sell(symbol, past_portfolio[symbol]["balance"] - current_portfolio[symbol]["balance"])
            else:
                self.report_sell(symbol, past_portfolio[symbol]["balance"])
        for symbol in current_portfolio:
            if symbol not in past_portfolio:
                self.report_buy(symbol, current_portfolio[symbol]["balance"])
        with open('history/transactions.json', 'w') as outfile:
            json.dump(self.transactions, outfile)
        for item in self.transactions:
            if item["ID"] in self.override:
                item["price"] = self.override[item["ID"]]
        return

    def get_coin_price(self, symbol):
        price = 0.0
        for item in self.transactions:
            if item["symbol"] == symbol:
                if item["type"] == "buy":
                    price += item["price"]
                if item["type"] == "sell":
                    price -= item["price"]
        return price
