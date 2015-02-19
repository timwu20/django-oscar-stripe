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

	return charge


def refund( charge_id, amount=None, refund_application_fee=False, reason=None, metadata={} ):

	charge = stripe.Charge.retrieve(charge_id)
	refund = charge.refunds.create( amount=amount, refund_application_fee=refund_application_fee, reason=reason, metadata=metadata )

	return refund
