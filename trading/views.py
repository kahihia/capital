import os
import json
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET, require_POST,require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from account.models import *
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from trading.forms import *
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core import serializers
from .utils import SATOSHIS_PER_BTC, satoshis_to_btc, get_display_time, get_display_number, call_bitmex_api, \
    textToColor, update_exchange_trx_generic
from django.views.generic import TemplateView
from account.forms import Settings_APIForm
from account.models import Trading_Platform, MyUser
import profig

from .exchanges.bagsniffer.coin_data import CoinData
from .exchanges.bagsniffer.portfolio import Portfolio
from .exchanges.bagsniffer.chains import Chains
from .exchanges.bagsniffer.exchanges import Exchanges
from .exchanges.bagsniffer.coins_manual import CoinsManual
from .exchanges.bagsniffer.analyzer import Analyzer
from collections import OrderedDict
import time
from datetime import datetime, date, timedelta
from .exchanges import *
from .tax_calculator import *
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_FILE = os.path.join(BASE_DIR , 'trading/config.cfg')

def init_exchanges(config):
    config_keys = config.as_dict(dict_type=dict).keys()
    exchanges = []
    if 'bittrex' in config_keys:
        bittrex = Bittrex(config['bittrex.csv_file'], GDAXPublic())
        exchanges.append(bittrex)
    if 'coinbase' in config_keys:
        coinbase = Coinbase(config['coinbase.key'], config['coinbase.secret'])
        exchanges.append(coinbase)
    if 'gdax' in config_keys:
        gdaxPrivate = GDAXPrivate(config['gdax.key'], config['gdax.secret'],
                                  config['gdax.passphrase'])
        exchanges.append(gdaxPrivate)
    if 'kraken' in config_keys:
        kraken = Kraken(config['kraken.key'], config['kraken.secret'],
                        GDAXPublic())
        exchanges.append(kraken)
    if 'poloniex' in config_keys:
        poloniex = Poloniex(config['poloniex.key'], config['poloniex.secret'],
                            GDAXPublic())
        exchanges.append(poloniex)

    return exchanges
#from quadriga import QuadrigaClient
# Create your views here.environmental1
@require_GET
@login_required(login_url = 'login')
def dashboard(request , id):
        context = {}
        user = get_object_or_404(MyUser , id = request.user.id)
        context['user'] = user
        # -*- coding: utf-8 -*-
        # Keep track of how much time we spend
        start_time = time.time()

        # Prepare caching dir
        #if not os.path.exists('cache'):
            #os.makedirs('cache')

        ## Prepare history dir
        #if not os.path.exists('history'):
            #os.makedirs('history')

        ## Prepare data dir for frontend
        #if not os.path.exists('webroot/data'):
            #os.makedirs('webroot/data')

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
            with open('/app/trading/exchanges/bagsniffer/history/summary.json', mode='r') as summary_file:
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
            except:
                past_portfolio = {}

        analyzer = Analyzer(coin_data)
        analyzer.find_transactions(past_portfolio, portfolio.current_portfolio)
        transactions = sorted(analyzer.transactions, key=lambda item: item['ID'], reverse=True)

        # Determine current scan date/time
        now = datetime.now()
        current_scan = {"year": now.year, "month": now.month, "day": now.day, "hour": now.hour}
        path_current_scan = '/app/trading/exchanges/bagsniffer/history/' + str(now.year) + '/' + str(now.month) + '/' + str(now.day) + '/' + str(now.hour)
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
        with open('/app/trading/exchanges/bagsniffer/webroot/data/portfolio.json', 'w') as outfile:
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
        with open('/app/trading/exchanges/bagsniffer/history/summary.json', 'w') as outfile:
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
        with open('/app/trading/exchanges/bagsniffer/webroot/data/summary.json', 'w') as outfile:
            json.dump(summary_frontend, outfile)

        # Generate transactions for frontend
        transactions_frontend = []
        for transaction in transactions:
            transaction_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(transaction["time"]))
            transactions_frontend.append([transaction["ID"], transaction_time, transaction["symbol"], transaction["type"], round(transaction["balance"], 4), round(transaction["price"], 4)])
        with open('/app/trading/exchanges/bagsniffer/webroot/data/transactions.json', 'w') as outfile:
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
        with open('/app/trading/exchanges/bagsniffer/webroot/data/treemap.json', 'w') as outfile:
            json.dump(treemap, outfile)

        end_time = time.time()
        print("Spent " + str(int(end_time - start_time)) + " seconds looking for your bags")
        print(str(count) + " unique bags sniffed. " + str(dust_count) + " bags look dusty.")
        ##from rotkelchen.args import app_args
        ##from rotkehlchen.rotkehlchen import Rotkehlchen
        ###args = app_args()
        ##r = Rotkehlchen()
        #config = profig.Config(CONFIG_FILE)
        #config.sync()

        #exchanges = init_exchanges(config)

        #asset_sales, leftover_lots = calculate_gains_losses(exchanges)

        #total_gain_loss = sum(sale.gain_loss for sale in asset_sales)
        #print("total gains/loss:")
        #print("{} USD".format(total_gain_loss))

        #for lot in leftover_lots:
            #print(lot.currency, lot.created_at, lot.amount, lot.price)

        #fills_json=update_exchange_trx_generic(service_type='Poloniex', api_key='AKI9ESB1-9M2J5AFG-E67UAP5O-YCI8POKP', api_secret='4cf4d82316c03852802a2526f9e087808e565a385784cd9efa180742207fa77249eba457f83facb043f9ccf44dd8ee1712e0adc0f4230ac701edb4a3129c1406')
        #print(fills_json)
        #for exchange in ['Quadrigacx', 'Quoine', 'Kraken', 'Bitfinex', 'Poloniex', 'Bitmex']:
            #try:
                #api_credentials = Trading_Platform.objects.get( user = user, trading_platform=exchange)
            #except:
                #api_credentials = 404

            #if api_credentials != 404 and exchange != 'Bitmex':
                #fills_json=update_exchange_trx_generic(service_type=exchange, api_key=api_credentials.api_key, api_secret=api_credentials.secret)
                #context[exchange]=fills_json
            #if exchange == 'Bitmex':
                #user={}
                #user['api_key']="4YFgfRe713-feq7ovWHtl_da"
                #user['api_secret']="SWkuxaufF9G2n_YgLONCAKAvtPBwBBYy17ZW0Fn8kH2iUs0m"
                #positions_json = call_bitmex_api('/position', api_key=user['api_key'], api_secret=user['api_secret'])


                #fills_json = call_bitmex_api('/execution/tradeHistory', {"reverse": "true"}, api_key=user['api_key'],
                                             #api_secret=user['api_secret'])
                #context['Bitmex']=fills_json
                #order_json = call_bitmex_api('/order', {"reverse": "true", "filter": '{"ordStatus":"New", "ordType":"Limit"}'},
                                             #api_key=user['api_key'], api_secret=user['api_secret'])
                #stop_json = call_bitmex_api('/order', {"reverse": "true", "filter": '{"ordStatus":"New", "ordType":"Stop"}'},
                                            #api_key=user['api_key'], api_secret=user['api_secret'])
                #instruments = call_bitmex_api('/instrument/indices', {"filter": '{"symbol":"."}'}, api_key=user['api_key'],
                                              #api_secret=user['api_secret'])
                #wallet = call_bitmex_api('/user/wallet', api_key=user['api_key'], api_secret=user['api_secret'])

                #order_history = call_bitmex_api('/order', {"reverse": "true"}, api_key=user['api_key'], api_secret=user['api_secret'])

                #wallet_history = call_bitmex_api('/user/walletHistory', api_key=user['api_key'], api_secret=user['api_secret'])

                ##wallet["amount"] = satoshis_to_btc(wallet["amount"])

               ##multiplier = 1
                #if user.hide_balance and wallet["amount"] != 0:
                    #multiplier = 1 / wallet["amount"]

                #wallet["amount"] *= multiplier

                #for u in allUsers:
                    #w = call_bitmex_api('/user/wallet', api_key=u.key_pub, api_secret=u.key_secret)
                    #w["amount"] = satoshis_to_btc(w["amount"])

                    #u.multiplier = 1
                    #if u.hide_balance and w["amount"] != 0:
                        #u.multiplier = 1 / w["amount"]

                    #w["amount"] *= u.multiplier
                    #u.wallet = w

                    #pos = call_bitmex_api('/position', api_key=u.key_pub, api_secret=u.key_secret)
                    #total_pos_value = 0
                    #for p in pos:
                        #if p["symbol"] == "XBTUSD":
                            #p["value"] = p["currentCost"] / SATOSHIS_PER_BTC
                        #else:
                            #if p["markPrice"] is None: p["markPrice"] = 0
                            #p["value"] = p["currentQty"] * p["markPrice"]
                        #p["value"] = get_display_number(p["value"])
                        #total_pos_value += p["value"]
                    #if w["amount"] != 0:
                        #if u.hide_balance:
                            #u.total_positions_value = get_display_number(multiplier * total_pos_value)
                        #else:
                            #u.total_positions_value = str(round(total_pos_value / w["amount"], 2)) + \
                                                      #"X ~ " + str(get_display_number(multiplier * total_pos_value))
                    #else:
                        #u.total_positions_value = 0
                        #w["amount"] = 0

                #closed_positions_json = [item for item in positions_json if not item["isOpen"]]
                #positions_json = [item for item in positions_json if item["isOpen"]]

                #for cp in closed_positions_json:
                    #cp["prevRealisedPnl"] = str(satoshis_to_btc(cp["prevRealisedPnl"])) + " BTC"

                #for p in positions_json:
                    #p['maintMargin'] = str(round(float(p["maintMargin"]) / SATOSHIS_PER_BTC, 2)) + \
                                       #(" (Cross)", "")[p["crossMargin"] == "1"]
                    #p["unrealisedGrossPnl"] = round(multiplier * p["unrealisedGrossPnl"] / SATOSHIS_PER_BTC, 4)
                    #p["realizedPnl"] = round(
                        #multiplier * (float(p["rebalancedPnl"]) + float(p["realisedPnl"])) / SATOSHIS_PER_BTC, 4)
                    #if p["symbol"] == "XBTUSD":
                        #p["value"] = p["currentCost"] / SATOSHIS_PER_BTC
                    #else:
                        #p["value"] = p["currentQty"] * p["markPrice"]
                    #p["value"] = round(multiplier * p["value"], 4)
                    #p["timestamp"] = get_display_time(p["timestamp"])
                    #if p["currentQty"] < 0:
                        #p["side"] = "Short"
                    #else:
                        #p["side"] = "Long"

                    #p["currentQty"] = multiplier * p["currentQty"]

                    #p["currentQty"] = get_display_number(p["currentQty"])

                #for s in stop_json:
                    #if not s["price"]:
                        #s["price"] = "Market"
                    #if not s["triggered"]:
                        #s["status"] = "Untriggered"
                    #s["timestamp"] = get_display_time(s["timestamp"])
                    #if not s["avgPx"]:
                        #s["avgPx"] = "-"

                    #s["cumQty"] = get_display_number(s["cumQty"] * multiplier)

                #for h in order_history:
                    #if not h["price"]:
                        #h["price"] = "Market"
                    #h["timestamp"] = get_display_time(h["timestamp"])
                    #if h["ordType"] == "Stop":
                        #if not h["triggered"]:
                            #h["status"] = "Untriggered"
                        #else:
                            #h["status"] = "Triggered"
                    #else:
                        #h["status"] = "-"
                        #h["stopPx"] = "-"
                    #if h["side"] == "Sell":
                        #h["orderQty"] = "-" + str(h["orderQty"])

                #for f in fills_json:
                    #f["shortId"] = f["orderID"][0:7]
                    #f["idColor"] = textToColor(f["orderID"])
                    #if f["symbol"][0:6] == "XBTUSD":
                        #f["value"] = str(f["orderQty"] / f["price"])[0:6]
                    #else:
                        #f["value"] = str(f["lastPx"] * f["orderQty"])[0:6]
                    #f["timestamp"] = get_display_time(f["timestamp"])

                #for o in order_json:
                    #if o["symbol"][0:6] == "XBTUSD":
                        #o["value"] = str(multiplier * o["orderQty"] / o["price"])[0:6]
                    #else:
                        #o["value"] = str(multiplier * o["price"] * o["orderQty"])[0:6]
                    #o["timestamp"] = get_display_time(o["timestamp"])

                    #o["cumQty"] = get_display_number(o["cumQty"] * multiplier)
                    #o["orderQty"] = get_display_number(o["orderQty"] * multiplier)
                    #o["leavesQty"] = get_display_number(o["leavesQty"] * multiplier)
                ##context['Bittex']=[
                    ##'currentUser': user,
                    ##'fills': fills_json,
                    ##'fillsDump': json.dumps(fills_json, indent=JSON_INDENT),
                    ##'positions': positions_json,
                    ##'positionsDump': json.dumps(positions_json, indent=JSON_INDENT),
                    ##'closedPositions': closed_positions_json,
                    ##'closedPositionsDump': json.dumps(closed_positions_json, indent=JSON_INDENT),
                    ##'orders': order_json,
                    ##'orderDump': json.dumps(order_json, indent=JSON_INDENT),
                    ##'stops': stop_json,
                    ##'stopsDump': json.dumps(stop_json, indent=JSON_INDENT),
                    ##'users': allUsers,
                    ##'instruments': json.dumps(instruments, indent=JSON_INDENT),
                    ##'wallet': wallet,
                    ##'walletDump': json.dumps(wallet),
                    ##'history': order_history,
                    ##'historyDump': json.dumps(order_history, indent=JSON_INDENT),
                    ##'walletHistory': json.dumps(wallet_history, indent=JSON_INDENT)
                    ##]
        print (context)
        return render(request , 'trading/dashboard.html' , context)


@require_GET
@login_required(login_url = 'login')
def profile(request , id):
    context = {}
    user = get_object_or_404(MyUser , id = request.user.id)
    try:
        platform_api = Trading_Platform.objects.filter(user= request.user.id)
    except:
        platform_api = Trading_Platform()
    context['user'] = user
    context['platform_api'] = platform_api
    return render(request, 'trading/profile.html' , context)

@require_http_methods(['GET' , 'POST'])
@login_required(login_url = 'login')
def editprofile(request , id):
	context ={}
	user = get_object_or_404(MyUser, id = request.user.id)
	# context['user'] = user
	# data = {'first_name':user.first_name, 'last_name':user.last_name, 'phone':user.phone}
	if request.method == 'GET':
		context = { 'f' : EditProfileForm({'first_name': user.first_name,'email' : user.email , 'last_name':user.last_name , 'phone':user.phone})}
		return render(request, 'trading/editprofile.html', context)
	else:
		f = EditProfileForm(request.POST)
		if not f.is_valid():
			return render(request, 'trading/editprofile.html', {'f' : f})
		if user.email != f.data['email']:
			if (MyUser.objects.filter(email = f.data['email']).exists()):
				f.add_error('email','User with this email already exists.')
				return render(request, 'trading/editprofile.html', {'f' : f})
			else:
				user.email = f.data['email']
				user.first_name = f.data['first_name']
				user.last_name = f.data['last_name']
				user.phone = f.data['phone']
				user.confirmed_email = False
				user.save()
				try:
					otp = create_otp(user = user, purpose = 'CE')
					email_body_context = { 'u' : user, 'otp' : otp}
					body = loader.render_to_string('trading/confirmemail_email.txt', email_body_context)
					message = EmailMultiAlternatives("Confirm email", body, "bluerunfinancial@gmail.com", [user.email])
					message.send()
					return render(request , 'trading/confirmemail_email_sent.html' , { 'user': user })
				except ex:
					print(ex)
		else:
			user.first_name = f.data['first_name']
			user.last_name = f.data['last_name']
			user.phone = f.data['phone']
			user.save()

		return render(request, 'trading/profile.html', {'user': user})

def confirm_email(request , id , otp):
	user = get_object_or_404(MyUser, id=id)
	otp_object = get_valid_otp_object(user = user, purpose='CE', otp = otp)
	if not otp_object:
		raise Http404()
	user.confirmed_email = True
	user.save()
	otp_object.delete()
	return redirect(reverse('profile' , kwargs={'id': request.user.id}))

class APISettings(TemplateView):
    template_name = 'trading/settings.html'

    def get_context_data(self, **kwargs):
        context = super(APISettings, self).get_context_data(**kwargs)
        print (kwargs)

        try:
            trader = Trading_Platform.objects.get(user=self.request.user, trading_platform = kwargs['platform'])
            if kwargs['platform'] == trader.trading_platform:
                context['settings_form'] = Settings_APIForm(initial={'api_key': trader.api_key, 'secret': trader.secret, 'trading_platform':trader.trading_platform})
                return context
            return context
        except:
            context['settings_form'] = Settings_APIForm()
            return context

    def post(self, request):
        api_key = request.POST.get('api_key')
        secret = request.POST.get('secret')
        client_id = request.POST.get('client_id')
        trading_platform = request.POST.get('trading_platform')
        user = get_object_or_404(MyUser, email = request.user.email)
        try:
            trader = Trading_Platform.objects.get(user=request.user, trading_platform = trading_platform)
            trader.api_key = api_key
            trader.secret = secret
            if trader.client_id != u'':
                trader.client_id = int(client_id)
            trader.save()
        except:
            if client_id != u'':
                client_id = int(client_id)
            else:
                client_id = 0


            trader = Trading_Platform.objects.create(trading_platform = trading_platform,
                    api_key = api_key,
                    secret = secret,
                    user = user,
                    client_id = client_id)


        return HttpResponseRedirect('/')
