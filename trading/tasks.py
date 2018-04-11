from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
#from bluerun import celery_app

#@celery_app.task(bind=True)

@periodic_task(run_every=crontab(minute='1'))
def Collect_Gain_Report():
	print ("started billing")
	from account.models import Trading_Platform, MyUser
	import ccxt  # noqa: E402
	for user in MyUser.objects.all():
		context = {}
		for exchange in ['Quadrigacx', 'Quoine', 'Kraken', 'Bitfinex']:
			try:
				api_credentials = Trading_Platform.objects.get( user = user, trading_platform=exchange)
			except:
				api_credentials = 404

			if exchange == "Quadrigacx" and api_credentials!=404:
				context['Quadrigacx_data'] = ccxt.quadrigacx({
				"uid":str(api_credentials.client_id),
				"apiKey": api_credentials.api_key,
				"secret": api_credentials.secret
				})
				context['Quadrigacx_transactions'], context['Quadrigacx_data'] = context['Quadrigacx_data'].privatePostUserTransactions(), dir(context['Quadrigacx_data'])
			elif exchange == "Quoine" and api_credentials!=404:
				context['Quoinex_data'] = ccxt.quoinex({"apiKey": api_credentials.api_key,
				"secret": api_credentials.secret})
				context['Quoinex_transactions'], context['Quoinex_data']  = context['Quoinex_data'].privateGetTrades(), dir(context['Quoinex_data'])
			elif exchange == "Kraken" and api_credentials!=404:
				context['Kraken_data'] = ccxt.kraken({"apiKey": api_credentials.api_key,
				"secret": api_credentials.secret})
				context['Kraken_transactions'] = context['Kraken_data'].privatePostTradesHistory()
			elif exchange == "Bitfinex" and api_credentials!=404:
				context['Bitfinex_data'] = ccxt.bitfinex({"apiKey": api_credentials.api_key,
				"secret": api_credentials.secret})
				context['Bitfinex_transactions'] = context['Bitfinex_data'].privatePostMytrades()
		print (context)


