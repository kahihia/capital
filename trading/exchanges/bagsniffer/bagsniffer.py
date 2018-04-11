# -*- coding: utf-8 -*-

from .coin_data import CoinData
from .portfolio import Portfolio
from .chains import Chains
from .exchanges import Exchanges
from .coins_manual import CoinsManual
from .analyzer import Analyzer
from collections import OrderedDict
import json
import time
import os
from datetime import datetime, date, timedelta

#from google.cloud import storage
#from google.cloud.storage import blob

#client =  storage.Client.from_service_account_json('/app/trading/service_account.json')
#bucket = client.get_bucket('mdollar-bee50.appspot.com')
#portfolio_blob = bucket.blob('data/portfolio.json')
#summary_blob = bucket.blob('data/summary.json')
#transactions_blob = bucket.blob('data/transactions.json')
#treemap_blob = bucket.blob('data/treemap.json')


# Keep track of how much time we spend
start_time = time.time()

# Prepare caching dir
if not os.path.exists('cache'):
    os.makedirs('cache')

# Prepare history dir
if not os.path.exists('history'):
    os.makedirs('history')

# Prepare data dir for frontend
if not os.path.exists('webroot/data'):
    os.makedirs('webroot/data')

# Initialize helper objects
coin_data = CoinData()
portfolio = Portfolio(coin_data)
chains = Chains(coin_data)
exchanges = Exchanges()
coins_manual = CoinsManual()

# Scan for holdings
chains.get_all_blockchain_balances(portfolio)
exchanges.get_all_exchange_balances(portfolio)
coins_manual.get_all_manual_balances(portfolio)

# Analysis

# Read previous summary if available
summary = {}
try:
    with open('history/summary.json', mode='r') as summary_file:
        summary = json.loads(summary_file.read())
except:
    summary = {}

# Try to read portfolio from last scan, used to find new transactions
past_portfolio = {}
if "last_scan" in summary:
    try:
        path_last_scan = 'history/' + str(summary["last_scan"]["year"]) + '/' + str(summary["last_scan"]["month"]) + '/' \
               + str(summary["last_scan"]["day"]) + '/' + str(summary["last_scan"]["hour"])
        with open(path_last_scan + '/portfolio.json', mode='r') as portfolio_file:
            past_portfolio = json.loads(portfolio_file.read())
            print (past_portfolio)
    except:
        past_portfolio = {}

analyzer = Analyzer(coin_data)
analyzer.find_transactions(past_portfolio, portfolio.current_portfolio)
transactions = sorted(analyzer.transactions, key=lambda item: item['ID'], reverse=True)

# Determine current scan date/time
now = datetime.now()
current_scan = {"year": now.year, "month": now.month, "day": now.day, "hour": now.hour}
path_current_scan = 'history/' + str(now.year) + '/' + str(now.month) + '/' + str(now.day) + '/' + str(now.hour)
if not os.path.exists(path_current_scan):
    os.makedirs(path_current_scan)

summary["last_scan"] = current_scan

# dump historical data for further analysis
with open(path_current_scan + '/portfolio.json', 'w') as outfile:
    json.dump(portfolio.current_portfolio, outfile)
with open(path_current_scan + '/coin_data.json', 'w') as outfile:
    json.dump(coin_data.coin_data, outfile)
with open(path_current_scan + '/prices_manual.json', 'w') as outfile:
    json.dump(coin_data.prices_manual, outfile)
with open(path_current_scan + '/transactions.json', 'w') as outfile:
    json.dump(transactions, outfile)

# Analyze portfolio, generate portfolio for frontend
current_portfolio = OrderedDict(sorted(portfolio.current_portfolio.items(), key=lambda item: item[1]['usd_value'], reverse=True))
total_btc = 0.0
total_usd = 0.0
count = 0
dust_count = 0
portfolio_frontend = []
for symbol, entry in current_portfolio.items():
    count += 1
    balance = entry['balance']
    marketcap = coin_data.get_market_cap(symbol)
    percent_24h = coin_data.get_percent_change_24h(symbol) / 100
    percent_7d = coin_data.get_percent_change_7d(symbol) / 100
    if symbol == 'USD' or symbol == 'USDT':
        usd_value = balance
    else:
        usd_value = entry['usd_value']
    btc_cost = analyzer.get_coin_price(symbol)
    btc_value = entry['btc_value']
    if btc_cost > 0:
        pl = ((btc_value - btc_cost) / btc_cost)
        portfolio_frontend.append([symbol, round(marketcap, 0), round(percent_24h, 6), round(percent_7d, 6), round(balance, 4),
                                   round(usd_value, 2), round(btc_cost, 4), round(btc_value, 4), round(pl, 6)])
    else:
        portfolio_frontend.append([symbol, round(marketcap, 0), round(percent_24h, 6), round(percent_7d, 6), round(balance, 4),
                                   round(usd_value, 2), round(btc_cost, 4), round(btc_value, 4), ""])
    total_btc += btc_value
    total_usd += usd_value
    if usd_value < 10:
        dust_count += 1
print("Total: " + str(total_usd))
with open('webroot/data/portfolio.json', 'w') as outfile:
    json.dump(portfolio_frontend, outfile)

# Update summary
# 30 day history
if "history" in summary:
    last_date = date(summary["history"][29]["year"], summary["history"][29]["month"], summary["history"][29]["day"])
    this_date = date(now.year, now.month, now.day)
    delta = this_date - last_date
    if delta.days == 1:
        # just pop the oldest entry if we started a new day
        summary["history"].pop(0)
        summary["history"].append({})
    elif delta.days > 1:
        # pad the history if we missed some days
        day = now - timedelta(days=delta.days - 1)
        for i in range(0, delta.days - 1):
            summary["history"].pop(0)
            summary["history"].append({})
            summary["history"][29] = {"year": day.year, "month": day.month, "day": day.day, "total_usd": 0.0, "total_btc": 0.0}
            day = day + timedelta(days=1)
        summary["history"].pop(0)
        summary["history"].append({})
else:
    summary["history"] = []
    # create an empty history
    day = now - timedelta(days=29)
    for i in range(0, 30):
        summary["history"].append({"year": day.year, "month": day.month, "day": day.day, "total_usd": 0.0, "total_btc": 0.0})
        day = day + timedelta(days=1)
# update current day
summary["history"][29] = {"year": now.year, "month": now.month, "day": now.day, "total_usd": total_usd, "total_btc": total_btc}
with open('history/summary.json', 'w') as outfile:
    json.dump(summary, outfile)

# Generate summary for frontend
summary_frontend = {}
summary_frontend["total_usd"] = total_usd
summary_frontend["total_btc"] = total_btc
if summary["history"][28]["total_usd"] > 0:
    summary_frontend["24h_chg_usd"] = ((total_usd - summary["history"][28]["total_usd"]) / summary["history"][28]["total_usd"])
else:
    summary_frontend["24h_chg_usd"] = 0.0
if summary["history"][28]["total_btc"] > 0:
    summary_frontend["24h_chg_btc"] = ((total_btc - summary["history"][28]["total_btc"]) / summary["history"][28]["total_btc"])
else:
    summary_frontend["24h_chg_btc"] = 0.0
summary_frontend["30d_performance_usd"] = []
summary_frontend["30d_labels_usd"] = []
for i in range(0, 30):
    summary_frontend["30d_performance_usd"].append(round(summary["history"][i]["total_usd"], 2))
summary_frontend["30d_performance_btc"] = []
summary_frontend["30d_labels"] = []
for i in range(0, 30):
    summary_frontend["30d_performance_btc"].append(round(summary["history"][i]["total_btc"], 4))
    summary_frontend["30d_labels"].append(str(summary["history"][i]["year"]) + "-" + str(summary["history"][i]["month"]) + "-" + str(summary["history"][i]["day"]))
summary_frontend["recent_transactions"] = []
for transaction in transactions:
    transaction_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(transaction["time"]))
    summary_frontend["recent_transactions"].append([transaction_time, transaction["symbol"], transaction["type"], round(transaction["balance"], 0), str(round(transaction["price"], 4)) + " ₿"])
    if len(summary_frontend["recent_transactions"]) > 3:
        break
with open('webroot/data/summary.json', 'w') as outfile:
    json.dump(summary_frontend, outfile)

# Generate transactions for frontend
transactions_frontend = []
for transaction in transactions:
    transaction_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(transaction["time"]))
    transactions_frontend.append([transaction["ID"], transaction_time, transaction["symbol"], transaction["type"], round(transaction["balance"], 4), round(transaction["price"], 4)])
with open('webroot/data/transactions.json', 'w') as outfile:
    json.dump(transactions_frontend, outfile)

# Generate treemap for frontend
treemap = [['Symbol', 'Parent', 'Share', 'Change'], [{'v': 'Current', 'f': 'Current Portfolio'}, None, 0, 0], [{'v': '24h', 'f': '24h Performance'}, 'Current', 0, 0], [{'v': '7d', 'f': '7d Performance'}, 'Current', 0, 0]]
for symbol, entry in current_portfolio.items():
    btc_value = entry['btc_value']
    if btc_value > 0:
        percent_24h = coin_data.get_percent_change_24h(symbol) / 100
        percent_7d = coin_data.get_percent_change_7d(symbol) / 100
        treemap.append([{'v': symbol + '24h', 'f': symbol}, '24h', 100/total_btc * btc_value, percent_24h])
        treemap.append([{'v': symbol + '7d', 'f': symbol}, '7d', 100/total_btc * btc_value, percent_7d])
with open('webroot/data/treemap.json', 'w') as outfile:
    json.dump(treemap, outfile)

end_time = time.time()
print("Spent " + str(int(end_time - start_time)) + " seconds looking for your bags")
print(str(count) + " unique bags sniffed. " + str(dust_count) + " bags look dusty.")
