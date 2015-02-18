from django.test import SimpleTestCase
from django_oscar_stripe import gateway
from stripe.error import CardError, InvalidRequestError
from stripe.resource import Charge

class ChargeTestCase(SimpleTestCase):

	def test_successful_charge(self):
		card_info = {'number': '5555555555554444', 'exp_month': 12, 'exp_year': 2017, 'cvc': 544,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( success, True)
		self.assertEqual( obj['amount'], 4000)
		self.assertEqual( obj['captured'], True)

	def test_card_declined_charge(self):
		card_info = {'number': '4000000000000002', 'exp_month': 12, 'exp_year': 2017, 'cvc': 544,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( obj.http_status, 402 )
		self.assertEqual( type(obj), CardError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['code'], u'card_declined' )

	def test_incorrect_cvc_charge(self):
		card_info = {'number': '4000000000000127', 'exp_month': 12, 'exp_year': 2017, 'cvc': 544,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( obj.http_status, 402 )
		self.assertEqual( type(obj), CardError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['code'], u'incorrect_cvc' )

	def test_expired_card_charge(self):
		card_info = {'number': '4000000000000119', 'exp_month': 12, 'exp_year': 2017, 'cvc': 544,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( obj.http_status, 402 )
		self.assertEqual( type(obj), CardError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['code'], u'processing_error' )

	def test_invalid_expiry_month(self):
		card_info = {'number': '5555555555554444', 'exp_month': 13, 'exp_year': 2017, 'cvc': 544,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( obj.http_status, 402 )
		self.assertEqual( type(obj), CardError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['code'], u'invalid_expiry_month' )

	def test_invalid_expiry_year(self):
		card_info = {'number': '5555555555554444', 'exp_month': 12, 'exp_year': 1970, 'cvc': 544,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( obj.http_status, 402 )
		self.assertEqual( type(obj), CardError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['code'], u'invalid_expiry_year' )

	def test_invalid_cvc(self):
		card_info = {'number': '5555555555554444', 'exp_month': 12, 'exp_year': 2020, 'cvc': 54,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( obj.http_status, 402 )
		self.assertEqual( type(obj), CardError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['code'], u'invalid_cvc' )

	def test_invalid_cardinfo(self):
		#missing card info
		card_info = {'exp_month': 12, 'exp_year': 2020, 'cvc': 54,}
		success, obj = gateway.charge(4000, card_info=card_info)

		self.assertEqual( type(obj), gateway.CardInfoError )

class RefundTestCase(SimpleTestCase):

	charge = None

	def setUp(self):
		card_info = {'number': '5555555555554444', 'exp_month': 12, 'exp_year': 2017, 'cvc': 544,}
		success, obj = gateway.charge(4000, card_info=card_info)

		if success:
			self.charge = obj
		else:
			self.charge = None

	def test_charge_created(self):
		self.assertEqual( type(self.charge), Charge )

	def test_full_refund(self):
		self.assertEqual( type(self.charge), Charge )

		charge_id = self.charge['id']
		success, refund = gateway.refund( charge_id=charge_id )

		self.assertEqual( True, success )
		self.assertEqual( refund['object'], 'refund' )
		self.assertEqual( refund['amount'], 4000 )

	def test_partial_refund(self):
		self.assertEqual( type(self.charge), Charge )

		charge_id = self.charge['id']
		success, refund = gateway.refund( amount=2000, charge_id=charge_id )

		self.assertEqual( True, success )
		self.assertEqual( refund['object'], 'refund' )

	def test_refund_amount_too_large(self):
		self.assertEqual( type(self.charge), Charge )

		charge_id = self.charge['id']
		success, obj = gateway.refund( amount=5000, charge_id=charge_id )

		self.assertEqual( obj.http_status, 400 )
		self.assertEqual( type(obj), InvalidRequestError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['type'], u'invalid_request_error' )

	def test_refund_balance_too_low(self):
		self.assertEqual( type(self.charge), Charge )

		charge_id = self.charge['id']
		success, obj = gateway.refund( amount=3000, charge_id=charge_id )
		success, obj = gateway.refund( amount=3000, charge_id=charge_id )

		self.assertEqual( obj.http_status, 400 )
		self.assertEqual( type(obj), InvalidRequestError )

		body = obj.json_body
		err  = body['error']

		self.assertEqual( err['type'], u'invalid_request_error' )

	def test_invalid_amount(self):
		self.assertEqual( type(self.charge), Charge )

		charge_id = self.charge['id']
		success, obj = gateway.refund( amount="f00", charge_id=charge_id )

		self.assertEqual( obj.http_status, 400 )
		self.assertEqual( type(obj), InvalidRequestError )

		body = obj.json_body
		err  = body['error']

		print err

		self.assertEqual( err['type'], u'invalid_request_error' )






