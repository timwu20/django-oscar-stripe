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

'''
try:
  # Use Stripe's bindings...
  pass
except stripe.error.CardError, e:
  # Since it's a decline, stripe.error.CardError will be caught
  body = e.json_body
  err  = body['error']

  print "Status is: %s" % e.http_status
  print "Type is: %s" % err['type']
  print "Code is: %s" % err['code']
  # param is '' in this case
  print "Param is: %s" % err['param']
  print "Message is: %s" % err['message']
except stripe.error.InvalidRequestError, e:
  # Invalid parameters were supplied to Stripe's API
  pass
except stripe.error.AuthenticationError, e:
  # Authentication with Stripe's API failed
  # (maybe you changed API keys recently)
  pass
except stripe.error.APIConnectionError, e:
  # Network communication with Stripe failed
  pass
except stripe.error.StripeError, e:
  # Display a very generic error to the user, and maybe send
  # yourself an email
  pass
except Exception, e:
  # Something else happened, completely unrelated to Stripe
  pass
'''

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
    
    #try:

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

    print charge

    #except Exception, e:
    #    print e