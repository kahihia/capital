import base64
import json
import os


class Portfolio(object):
    item_list = []
    caching = False
    cache_key = ""
    item_list_cache = []
    current_portfolio = {}
    coin_data = None

    def __init__(self, coin_data):
        self.item_list = []
        self.caching = False
        self.current_portfolio = {}
        self.coin_data = coin_data
        return

    # Start caching coin info as a source specific backup if somewhen later, reading from the original
    # source should fail. key = source key, e.g. "bitfinex", or "ETH-<someaddress>"
    def cache_initialize(self, key):
        self.caching = True
        self.cache_key = 'cache/' + base64.urlsafe_b64encode(key.encode('utf-8')).decode() + '.json'
        self.item_list_cache = []
        return

    # Reading from source went well, commit cache to main coin list, save as backup
    def cache_commit(self):
        self.caching = False
        for item in self.item_list_cache:
            self.have_coins(item["symbol"], item["amount"], item["source"])
        with open(self.cache_key, 'w') as outfile:
            json.dump(self.item_list_cache, outfile)
        return

    # Something went wrong while reading new coin data for the current cache key, restore from backup if there is one
    def cache_restore(self, destroy=False):
        self.caching = False
        try:
            with open(self.cache_key, mode='r') as cache_file:
                self.item_list_cache = json.loads(cache_file.read())
            for item in self.item_list_cache:
                self.have_coins(item["symbol"], item["amount"], item["source"])
            if destroy:
                os.remove(self.cache_key)
        except:
            pass
        return

    # How many entries do we have in the cache?
    def cache_size(self):
        return len(self.item_list_cache)

    # Add or subtract an *amount* of coins for a *coin*
    def have_coins(self, symbol, amount, source):
        symbol = self.coin_data.translate_symbol(symbol)
        if self.caching:
            self.item_list_cache.append({"symbol": symbol, "amount": amount, "source": source})
        else:
            self.item_list.append({"symbol": symbol, "amount": amount, "source": source})
            if symbol in self.current_portfolio:
                self.current_portfolio[symbol]['balance'] += amount
                self.current_portfolio[symbol]['btc_value'] = self.current_portfolio[symbol]['balance'] * self.coin_data.get_btc_price(symbol)
                self.current_portfolio[symbol]['usd_value'] = self.current_portfolio[symbol]['balance'] * self.coin_data.get_btc_price(symbol) * self.coin_data.get_btc_price_usd()
            else:
                self.current_portfolio[symbol] = {'balance': amount, 'btc_value': amount * self.coin_data.get_btc_price(symbol), 'usd_value': amount * self.coin_data.get_btc_price(symbol) * self.coin_data.get_btc_price_usd()}
        return
