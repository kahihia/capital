# Bagsniffer
Advanced crypto portfolio tracker, supporting close to 100 exchanges and 30 chains. 

PROOF OF CONCEPT/EARLY ALPHA. Read DEVELOPMENT.md for background info on the motivation of the project 
and the development status.

## Quickstart
Tested on Amazon EC2, Ubuntu 16.04 LTS, instance type: T2.micro, ca. 9$/month.

Don't forget to open ports 22 (SSH) and 80 (HTTP frontend), BUT LIMIT BOTH TO YOUR PRIVATE IP ONLY.

CAUTION: This is a quick start only. Please read the security precautions section 
further down before you start entering exchange keys and other sensible data.

### Bring your system up to date

    sudo apt-get update
    sudo apt-get upgrade

### Install libraries

    sudo apt-get install python3-pip
    pip3 install ccxt
    pip3 install pywaves

### Clone Bagsniffer

    cd
    git clone https://github.com/cryptic-monk/bagsniffer.git

### Add an address to scan

    cd bagsniffer/config
    cp chains_sample.txt chains.txt
    nano chains.txt

=> add one of your bitcoin addresses there, or leave the sample address if you don't mind
holding Satoshi's bags for a second.

### Test

    cd ..
    python3 bagsniffer.py

=> this should find the bitcoins on the address that you defined above

### Automate

    crontab -e

Add this line at the bottom to run bagsniffer once every hour, replacing
`<USER>` with your user name first:

    0 * * * * cd /home/<USER>/bagsniffer && python3 bagsniffer.py

Add another line to serve the frontend. Here too, don't forget to replace
`<USER>` first:

    @reboot cd /home/<USER>/bagsniffer/webroot && sudo python3 -m http.server 80

Reboot: `sudo reboot`

After reboot, should be able to see the frontend by entering your server's public IP in your browser.

### Update

Since no compilation is needed, updating is easy for now, just do:

    cd ~/bagsniffer
    git pull

## Configuration (Detailed)
All configuration files reside in the "config" subdirectory. They are simple text files that all follow the same 
base format.

For example, for the exchange keys:

    exchange1 key secret
    exchange2 key secret

After the required fields, you can add an optional comment in any format that you like, it will be ignored:

    exchange1 key secret
    exchange2 key secret <- this is my bot account

If some info contains spaces, you have to put it in quotation marks:

    exchange1 key "secret with some spaces"

Escaping is not possible, but you can use both "'" and '"':

    exchange1 key 'secret with some spaces and a "'

You can even add a full line comment if you like, just start the line with '#', and empty lines will be ignored:

    # Exchange keys, format: <ID> <key> <secret>
    
    exchange1 key secret
    exchange2 key secret


### exchanges.txt

API keys + secrets for exchanges.

    format: <ID> <key> <secret>

Bagsniffer supports all exchanges supported by ccxt, but I have not tested them all.
A list of all supported exchanges can be found here: https://github.com/ccxt/ccxt. The "id" 
column shows the ID also used in bagsniffer.

Tested exchanges: binance, bitfinex, bittrex, cryptopia, kraken, kucoin, okex, quoine

Make sure to generate separate keys for Bagsniffer and to only give read access for security reasons.

### chains.txt
Blockchain public keys to scan.

    format: <symbol> <key>

Special cases: 
- For Bitcoin, you can use your xpub key to monitor all addresses in a wallet (e.g. on your Ledger)
- Ethereum addresses are automatically scanned for tokens
- NEO addresses are automatically scanned for tokens
- WAVES addresses are automatically scanned for tokens

### coins_manual.txt
Manual holding entries, e.g. from ICOs, or wallets that cannot be checked automatically.

    format: <symbol> <amount>

### prices_manual.txt
Manual entry of coin prices in BTC for coins where the price cannot be determined automatically, e.g.
because the coin is not yet listed on an exchange.

    format: <symbol> <price>

Caution: Takes precedence over any other possible price info for that coin.

### transactions:_override.txt
Manual transaction price (buy/sell total in BTC) override.

    format: <ID> <price>

Whenever Bagsniffer discovers a new buy or sell, it creates a new transaction entry. Each new entry gets an
unique ID (starting with 1 for your very first buy). Bagsniffer tries to guess the value of the transaction,
but maybe you have bought the coins a bit cheaper, or a bit more expensive, or you mined them, or somebody
gave them to you as a present. In this case, you can override the purchase/sale total of each transaction by
using this file. 

Transactions remain how they are in perpetuity. They describe how you got the current amount of coins in 
your portfolio. For that reason, you cannot completely delete past transactions, or modify the coin count
in those transactions. If for some reason, you want to artificially manipulate the coin count in your 
portfolio, you can for example define a negative manual coin entry (in coins_manual.txt), and then override 
the price of the "sell" transaction that Bagsniffer discovers due to this entry to a price of 0.

### <xyz>_disambiguation.txt
Used to translate symbols from/to a service. Currently supported: neo, coinmarketcap.

    format: <symbo_from> <symbol_to>
    
## Security

### Key Threats
1) Disclosure of API keys
2) Disclosure of information regarding your holdings and your trading activity
3) Installation of malicious software on your server

### Mitigation
1) Use separate API keys for Bagsniffer and set them up as read-only. Distrust any exchange that does not 
offer read-only API keys.
2) Limit server access to ports 22 and 80, and to your personal IP. Instead of using Python's simple http server 
as shown in the quickstart section, use a more established server like Apache and serve the frontend via https
instead of http. 
3) Currently, the frontend can be served statically. Meaning: the web server does not require any kind
of scripting or write access to the "webroot" directory. Regularly update your server.

For the extra paranoid:
- Run the script on a server without an open web port and periodically scp the "data" directory inside "webroot" to another 
server. Then statically serve the frontend from there.
- Replace the cloud hosted .js/.css files for the web part with your local versions.

## Libraries Used
pip install ccxt, thanks to: https://github.com/ccxt/ccxt
pip install pywaves, thanks to: https://github.com/PyWaves/PyWaves

## Known Issues and ToDos
- Sometimes, ccxt, or an exchange API, reports all balances in an account to be 0, without actually reporting an 
error (observed on Bittrex for example). In this case, Bagsniffer has no way of telling whether you actually 
sold/moved your coins from that exchange, or whether an error occurred. Therefore, Bagsniffer will classify all 
the coins previously held on that exchange as a "sell", and they'll usually reappear as "buys", when the exchange 
starts reporting balances correctly again. To mitigate this issue, Bagsniffer will retry reading balances 
for an exchange that reports all balances as zero, but there's no way to completely avoid that issue.