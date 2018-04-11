import ccxt
from .config_reader import ConfigReader


class Exchanges(object):
    exchange_keys = {}

    def __init__(self):
        self.exchange_keys = {}
        reader = ConfigReader("exchanges.txt", 3)
        for line in reader.fields:
            if len(line) >= 3:
                self.exchange_keys[line[0]] = {"key": line[1], "secret": line[2]}
        return

    # Get balances from a single exchange
    def get_single_exchange_balances(self, portfolio, exchange, api):
        print("Obtaining " + exchange + " balances...")
        try:
            # TODO: nasty fix for non-unified access to Bitfinex wallet types (also: at least one type is missing)
            if exchange == 'bitfinex':
                result = api.fetch_balance({'type': 'deposit'})
                for symbol, amount in result['total'].items():
                    if amount > 0:
                        print('Found ' + str(round(amount, 4)) + ' ' + symbol)
                        portfolio.have_coins(symbol, amount, exchange)
            result = api.fetch_balance()
            for symbol, amount in result['total'].items():
                if amount > 0:
                    print('Found ' + str(round(amount, 4)) + ' ' + symbol)
                    portfolio.have_coins(symbol, amount, exchange)
            return True
        except:
            print("An error occurred...")
            return False

    # get balances for all exchanges
    def get_all_exchange_balances(self, portfolio):
        print("Obtaining all exchange balances...")
        for exchange, api_key in self.exchange_keys.items():
            # bail if we don't have key + secret
            if len(api_key["key"]) == 0 or len(api_key["secret"]) == 0:
                continue
            api = None
            if exchange in ccxt.exchanges:
                api = getattr(ccxt, exchange)({
                    'apiKey': api_key["key"],
                    'secret': api_key["secret"],
                })
            else:
                print("Unknown exchange: " + exchange)
            if api is not None:
                portfolio.cache_initialize(exchange)
                result = self.get_single_exchange_balances(portfolio, exchange, api)
                if result and portfolio.cache_size() > 0:
                    portfolio.cache_commit()
                else:
                    # if we had a result, but 0 coins were found, we try to restore the coins once, but
                    # destroy the cache afterwards
                    # this should mitigate the "exchange/blockchain API reports zero balance issue"
                    # if we didn't get a result, we (potentially) restore infintely
                    portfolio.cache_restore(result)
            else:

                print('No api here')
        return
