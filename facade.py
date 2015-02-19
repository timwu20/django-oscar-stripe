from django_oscar_stripe import gateway
import stripe
from oscar.apps.payment.exceptions import UnableToTakePayment, PaymentError
from django.utils.translation import ugettext as _

import sys

import logging
logger = logging.getLogger('vapeeuphoria.apps.checkout')

def charge(order_number, total, bankcard):
    try:
        metadata = {
            'order_number': order_number,
        }
        card_info = {
            'number': bankcard.number, 
            'exp_month': bankcard.expiry_date.month, 
            'exp_year': bankcard.expiry_date.year, 
            'cvc': bankcard.ccv,
        }
        total_in_cents = int(total.incl_tax * 100)
        charge = gateway.charge( total_in_cents, card_info=card_info, metadata=metadata )


    except gateway.CardInfoError, e:
        raise UnableToTakePayment( e )

    except (stripe.error.CardError, stripe.error.InvalidRequestError) as e:
        body = e.json_body
        err  = body['error']
        raise UnableToTakePayment( err['message'] )

    except (stripe.error.AuthenticationError, stripe.error.APIConnectionError, stripe.error.StripeError) as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        logger.error('Stripe Error:', exc_info=sys.exc_info())
        raise PaymentError()
        

    except Exception, e:
        # Something else happened, completely unrelated to Stripe
        logger.error('Stripe Error:', exc_info=sys.exc_info())
        raise PaymentError()

    return charge