from .config_reader import ConfigReader
import ccxt
import json


class CoinData(object):
    prices_manual = None
    coin_data = None
    disambiguation_tables = {}

    def __init__(self):
        print("Obtaining coinmarketcap ticker...")
        try:
            coinmarketcap = ccxt.coinmarketcap()
            self.coin_data = coinmarketcap.fetch_tickers()
            with open('cache/coinmarketcap.json', 'w') as outfile:
                json.dump(self.coin_data, outfile)
        except:
            with open('cache/coinmarketcap.json', mode='r') as cache_file:
                self.coin_data = json.loads(cache_file.read())
        self.prices_manual = []
        reader = ConfigReader("prices_manual.txt", 2)
        for line in reader.fields:
            if len(line) >= 2:
                self.prices_manual.append({"symbol": line[0], "price": float(line[1])})
        self.disambiguation_tables = {}
        self.read_disambiguation_table("neo")
        self.read_disambiguation_table("coinmarketcap")
        return

    # read disambiguation table for "name"
    def read_disambiguation_table(self, name):
        self.disambiguation_tables[name] = {}
        reader = ConfigReader(name + "_disambiguation.txt", 2)
        for line in reader.fields:
            if len(line) >= 2:
                self.disambiguation_tables[name][line[0]] = line[1]
        return

    # translate a symbol from "name" to the common symbol (if there's one)
    def disambiguation(self, name, original):
        if name not in self.disambiguation_tables:
            return original
        if original in self.disambiguation_tables[name]:
            return self.disambiguation_tables[name][original]
        return original

    # Translate a common symbol to the one used on "name" (if there's one)
    def disambiguation_reverse(self, name, original):
        if name not in self.disambiguation_tables:
            return original
        for symbol_from, symbol_to in self.disambiguation_tables[name].items():
            if symbol_to == original:
                return symbol_from
        return original

    # unify coin symbols
    def translate_symbol(self, symbol):
        if symbol == 'SONM':
            return 'SNM'
        return symbol

    # Define BTC price for a coin (e.g. from an external source)
    def define_coin_price(self, symbol, price):
        for entry in self.prices_manual:
            if entry["symbol"] == symbol:
                return
        self.prices_manual.append({"symbol": symbol, "price": price})
        return

    # Get price (in Bitcoin) for symbol
    def get_btc_price(self, symbol):
        for entry in self.prices_manual:
            if entry["symbol"] == symbol:
                return float(entry["price"])
        if symbol == "USD" or symbol == "USDT":
            return 1/self.get_btc_price_usd()
        else:
            cmcap_symbol = self.disambiguation_reverse("coinmarketcap", symbol)
            try:
                if cmcap_symbol + "/USD" in self.coin_data:
                    return float(self.coin_data[cmcap_symbol + "/USD"]["info"]["price_btc"])
            except:
                return 0.0
        return 0.0

    # Get BTC price in 'murican dollas
    def get_btc_price_usd(self):
        return float(self.coin_data["BTC/USD"]["last"])

    # Get market cap for symbol
    def get_market_cap(self, symbol):
        cmcap_symbol = self.disambiguation_reverse("coinmarketcap", symbol)
        try:
            if cmcap_symbol + "/USD" in self.coin_data:
                return float(self.coin_data[cmcap_symbol + "/USD"]["info"]["market_cap_usd"])
        except:
            return 0.0
        return 0.0

    # Get 24h % change for symbol
    def get_percent_change_24h(self, symbol):
        cmcap_symbol = self.disambiguation_reverse("coinmarketcap", symbol)
        try:
            if cmcap_symbol + "/USD" in self.coin_data:
                return float(self.coin_data[cmcap_symbol + "/USD"]["info"]["percent_change_24h"])
        except:
            return 0.0
        return 0.0

    # Get 7d % change for symbol
    def get_percent_change_7d(self, symbol):
        cmcap_symbol = self.disambiguation_reverse("coinmarketcap", symbol)
        try:
            if cmcap_symbol + "/USD" in self.coin_data:
                return float(self.coin_data[cmcap_symbol + "/USD"]["info"]["percent_change_7d"])
        except:
            return 0.0
        return 0.0

    # Try to guess a coin symbol based on the coin name using cmcap data
    def find_symbol(self, name):
        for ticker in self.coin_data:
            if self.coin_data[ticker]["info"]["name"] == name:
                return self.coin_data[ticker]["info"]["symbol"]
        return name

