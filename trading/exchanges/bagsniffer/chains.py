from .config_reader import ConfigReader
import pywaves
import json
import urllib3
import certifi


class Chains(object):
    http = None
    coin_data = None
    cryptoid_coins = {}
    public_keys = {}

    def __init__(self, coin_data):
        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        print("Obtaining cryptoid coin list...")
        try:
            r = self.http.request('GET', 'https://chainz.cryptoid.info/explorer/api.dws?q=summary')
            self.cryptoid_coins = json.loads(r.data.decode('UTF-8', errors='ignore'))
            with open('cache/cryptoid.json', 'w') as outfile:
                json.dump(self.cryptoid_coins, outfile)
        except:
            try:
                with open('cache/cryptoid.json', mode='r') as cache_file:
                    self.cryptoid_coins = json.loads(cache_file.read())
            except:
                self.cryptoid_coins = {}
        self.coin_data = coin_data
        self.public_keys = {}
        reader = ConfigReader("chains.txt", 2)
        for line in reader.fields:
            if len(line) >= 2:
                if line[0] not in self.public_keys:
                    self.public_keys[line[0]] = []
                self.public_keys[line[0]].append(line[1])
        return

    # check amount of bitcoins on address
    def get_bitcoin(self, portfolio, address):
        print('Looking for Bitcoins on ' + address[:6] + '...', end='', flush=True)
        try:
            r = self.http.request('GET', 'https://blockchain.info/q/addressbalance/' + address)
            satoshis = int(r.data.decode('UTF-8'))
            if satoshis > 0:
                amount = satoshis / (10 ** 8)
                print(' Found ' + str(round(amount, 4)) + ' BTC')
                portfolio.have_coins('BTC', amount, address)
            else:
                print(' None found')
            return True
        except:
            print(' An error occurred.')
            return False

    # check the 'symbol' hodings of 'address' on cryptoid
    def get_cryptoid(self, portfolio, symbol, address):
        print('Looking for ' + symbol + ' on ' + address[:6] + '...', end='', flush=True)
        try:
            r = self.http.request('GET',
                             'https://chainz.cryptoid.info/' + symbol.lower() + '/api.dws?q=getbalance&a=' + address)
            amount = float(r.data.decode('UTF-8'))
            if amount > 0:
                print(' Found ' + str(round(amount, 4)) + ' ' + symbol)
                portfolio.have_coins(symbol, amount, address)
            return True
        except:
            print(' An error occurred.')
            return False

    # look for NEO and NEO based tokens (insight)
    def scan_neo(self, portfolio, address):
        print('Scanning NEO address ' + address[:6] + '...')
        try:
            r = self.http.request('GET', 'https://otcgo.cn/api/v1/balances/' + address)
            data = json.loads(r.data.decode('UTF-8'))
            for entry in data["balances"]:
                amount = float(entry["total"])
                if amount > 0:
                    symbol = self.coin_data.disambiguation("neo", entry["marketSign"].upper())
                    print('Found ' + str(round(amount, 4)) + ' ' + symbol)
                    portfolio.have_coins(symbol, amount, address)
            return True
        except:
            print(' An error occurred.')
            return False

    # look for coins on an insight style block explorer
    def get_insight_style(self, portfolio, url, symbol, address):
        print('Looking for ' + symbol + ' on ' + address[:6] + '...', end='', flush=True)
        try:
            r = self.http.request('GET', url + address)
            data = json.loads(r.data.decode('UTF-8'))
            amount = float(data['balance'])
            if amount > 0:
                print(' Found ' + str(round(amount, 4)) + ' ' + symbol)
                portfolio.have_coins(symbol, amount, address)
            return True
        except:
            print(' An error occurred.')
            return False

    # look for coins on a "raw" (simply returns balance) explorer
    def get_raw(self, portfolio, url, symbol, address):
        print('Looking for ' + symbol + ' on ' + address[:6] + '...', end='', flush=True)
        try:
            r = self.http.request('GET', url + address)
            amount = float(r.data.decode('UTF-8'))
            if amount > 0:
                print(' Found ' + str(round(amount, 4)) + ' ' + symbol)
                portfolio.have_coins(symbol, amount, address)
            return True
        except:
            print(' An error occurred.')
            return False

    # look for SKY on 'address'
    def get_sky(self, portfolio, address):
        print('Looking for SKY on ' + address[:6] + '...', end='', flush=True)
        try:
            r = self.http.request('GET', 'https://explorer.skycoin.net/api/currentBalance?addrs=' + address)
            data = json.loads(r.data.decode('UTF-8'))
            amount = 0.0
            for output in data["head_outputs"]:
                amount += float(output['coins'])
            if amount > 0:
                print(' Found ' + str(round(amount, 4)) + ' SKY')
                portfolio.have_coins('SKY', amount, address)
            return True
        except:
            print(' An error occurred.')
            return False

    # look for ZEC on 'address'
    def get_zec(self, portfolio, address):
        print('Looking for ZEC on ' + address[:6] + '...', end='', flush=True)
        try:
            r = self.http.request('GET', 'https://api.zcha.in/v2/mainnet/accounts/' + address)
            data = json.loads(r.data.decode('UTF-8'))
            amount = float(data['balance'])
            if amount > 0:
                print(' Found ' + str(round(amount, 4)) + ' ZEC')
                portfolio.have_coins('ZEC', amount, address)
            return True
        except:
            print(' An error occurred.')
            return False

    # look for NTRN on 'address'
    def get_ntrn(self, portfolio, address):
        print('Looking for NTRN on ' + address[:6] + '...', end='', flush=True)
        try:
            r = self.http.request('GET', 'http://www.fuzzbawls.pw/explore/Neutron/api_fetch.php?method=getbalance&address=' + address)
            data = json.loads(r.data.decode('UTF-8'))
            amount = float(data['data'])
            if amount > 0:
                print(' Found ' + str(round(amount, 4)) + ' NTRN')
                portfolio.have_coins('NTRN', amount, address)
            return True
        except:
            print(' An error occurred.')
            return False

    # Get ether and token balances on 'address'
    def scan_ethereum_address(self, portfolio, address):
        print('Looking for Ether and tokens on ' + address[:6] + '...')
        try:
            r = self.http.request('GET', 'https://api.ethplorer.io/getAddressInfo/' + address + '?apiKey=freekey')
            data = json.loads(r.data.decode('UTF-8'))
            try:
                amount = float(data["ETH"]["balance"])
                if amount > 0:
                    print('Found ' + str(round(amount, 4)) + ' ETH')
                    portfolio.have_coins('ETH', amount, address)
            except:
                pass
            for token in data["tokens"]:
                try:
                    amount = int(token["balance"]) / (10 ** int(token["tokenInfo"]["decimals"]))
                    if amount > 0:
                        symbol = token["tokenInfo"]["symbol"]
                        print('Found ' + str(round(amount, 4)) + ' ' + symbol)
                        portfolio.have_coins(symbol, amount, address)
                        if token["tokenInfo"]["price"]:
                            self.coin_data.define_coin_price(symbol, float(
                                token["tokenInfo"]["price"]["rate"]) / self.coin_data.get_btc_price_usd())
                except:
                    pass
            return True
        except:
            return False

    # Scan a Waves address for Waves and tokens
    def scan_waves_address(self, portfolio, address):
        print('Scanning Waves Address: ' + address[:6] + ' for WAVES and tokens...')
        try:
            waves = pywaves.Address(address)
        except:
            print('An error occurred.')
            return False
        try:
            portfolio.have_coins('WAVES', waves.balance() / 10 ** 8, address)
            print('Found ' + str(round(int(waves.balance()) / (10 ** 8), 4)) + ' WAVES')
        except:
            print('Could not get amount of WAVES on this address.')
        for asset in waves.assets():
            try:
                asset_info = pywaves.Asset(asset)
            except:
                print('An error occurred.')
                continue
            try:
                balance = waves.balance(asset, 0)
                if balance > 0:
                    symbol = self.coin_data.find_symbol(asset_info.name.decode('UTF-8'))
                    if symbol != '':
                        print('Found ' + str(round(balance / 10 ** asset_info.decimals, 4)) + ' ' + symbol)
                        portfolio.have_coins(symbol, balance / 10 ** asset_info.decimals, address)
            except:
                print('Error reading balance.')
        return True

    # Scan for an individual holding on the blockchain
    def get_blockchain_holding(self, symbol, key, portfolio):
        if symbol in ["ALQO"]:
            return self.get_raw(portfolio, "https://explorer.alqo.org/api/balance/", symbol, key)
        elif symbol.lower() in self.cryptoid_coins:
            return self.get_cryptoid(portfolio, symbol, key)
        elif symbol in ['BTC']:
            return self.get_bitcoin(portfolio, key)
        elif symbol in ['CHC']:
            return self.get_raw(portfolio, "http://104.238.153.140:3001/ext/getbalance/", symbol, key)
        elif symbol in ['DASH']:
            return self.get_cryptoid(portfolio, symbol, key)
        elif symbol in ['ETH']:
            return self.scan_ethereum_address(portfolio, key)
        elif symbol in ['NEO']:
            return self.scan_neo(portfolio, key)
        elif symbol in ['NTRN']:
            return self.get_ntrn(portfolio, key)
        elif symbol in ['QTUM']:
            return self.get_insight_style(portfolio, 'https://explorer.qtum.org/insight-api/addr/', symbol, key)
        elif symbol in ['RVN']:
            return self.get_raw(portfolio, "http://explorer.threeeyed.info/ext/getbalance/", symbol, key)
        elif symbol in ['UBQ']:
            return self.get_insight_style(portfolio, 'https://ubiqexplorer.com/api/Account/', symbol, key)
        elif symbol in ['SKY']:
            return self.get_sky(portfolio, key)
        elif symbol in ['WAVES']:
            return self.scan_waves_address(portfolio, key)
        elif symbol in ['ZEC']:
            return self.get_zec(portfolio, key)
        elif symbol in ['ZEN']:
            return self.get_insight_style(portfolio, 'https://explorer.zen-solutions.io/api/addr/', symbol, key)
        return False

    # get balances for all blockchain public keys
    def get_all_blockchain_balances(self, portfolio):
        for symbol, list in self.public_keys.items():
            for key in list:
                portfolio.cache_initialize(symbol + '_' + key)
                result = self.get_blockchain_holding(symbol, key, portfolio)
                if result and portfolio.cache_size() > 0:
                    portfolio.cache_commit()
                else:
                    # if we had a result, but 0 coins were found, we try to restore the coins once, but
                    # destroy the cache afterwards
                    # this should mitigate the "exchange/blockchain API reports zero balance issue"
                    # if we didn't get a result, we (potentially) restore infintely
                    portfolio.cache_restore(result)
        return
