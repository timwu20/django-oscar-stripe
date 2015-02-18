import stripe
from django.conf import settings

if not hasattr(settings, 'STRIPE_STATEMENT_DESCRIPTOR'):
	STRIPE_STATEMENT_DESCRIPTOR = None
else:
	STRIPE_STATEMENT_DESCRIPTOR = settings.STRIPE_STATEMENT_DESCRIPTOR

if not hasattr(settings, 'STRIPE_API_KEY'):
	raise Exception('STRIPE_API_KEY setting hasn\'t been set')
else:
	stripe.api_key = settings.STRIPE_API_KEY


class CardInfoError(Exception):
	pass

def _check_card_info( info={} ):
		
	if not info.has_key('number'):
		raise CardInfoError('"number" attribute required')

	if not info.has_key('exp_month'):
		raise CardInfoError('"exp_month" attribute required')

	if not info.has_key('exp_year'):
		raise CardInfoError('"exp_year" attribute required')

	if not info.has_key('cvc'):
		raise CardInfoError('"cvc" attribute required')

	return True


def charge( amount, currency='cad', card_info={}, description=None, metadata={}, statement_descriptor=STRIPE_STATEMENT_DESCRIPTOR, shipping={} ):
		
	try:

		_check_card_info( card_info )

		charge = stripe.Charge.create(
				amount=amount,
				currency=currency,
				card=card_info,
				description=description,
				metadata=metadata,
				statement_descriptor=statement_descriptor,
				shipping=shipping,
		)

	except CardInfoError, e:
		return False, e

	except stripe.error.CardError, e:
		# Since it's a decline, stripe.error.CardError will be caught
		body = e.json_body
		err  = body['error']

		'''
		print err

		print "Status is: %s" % e.http_status
		print "Type is: %s" % err['type']
		print "Code is: %s" % err['code']
		# param is '' in this case
		print "Message is: %s" % err['message']
		'''

		return False, e

	except stripe.error.InvalidRequestError, e:
		# Invalid parameters were supplied to Stripe's API
		return False, e

	except stripe.error.AuthenticationError, e:
		# Authentication with Stripe's API failed
		# (maybe you changed API keys recently)
		return False, e

	except stripe.error.APIConnectionError, e:
		# Network communication with Stripe failed
		return False, e

	except stripe.error.StripeError, e:
		# Display a very generic error to the user, and maybe send
		# yourself an email
		return False, e

	except Exception, e:
		# Something else happened, completely unrelated to Stripe
		return False, e

	return True, charge


def refund( charge_id, amount=None, refund_application_fee=False, reason=None, metadata={} ):

	try:
		charge = stripe.Charge.retrieve(charge_id)
		refund = charge.refunds.create( amount=amount, refund_application_fee=refund_application_fee, reason=reason, metadata=metadata )

	except stripe.error.InvalidRequestError, e:
		# Invalid parameters were supplied to Stripe's API
		return False, e

	except stripe.error.AuthenticationError, e:
		# Authentication with Stripe's API failed
		# (maybe you changed API keys recently)
		return False, e

	except stripe.error.APIConnectionError, e:
		# Network communication with Stripe failed
		return False, e

	except stripe.error.StripeError, e:
		# Display a very generic error to the user, and maybe send
		# yourself an email
		return False, e

	except Exception, e:
		# Something else happened, completely unrelated to Stripe
		return False, e

	return True, refund
