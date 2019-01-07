import json
from finance.views import quote
from .base import BaseUnitTestCase
from django.urls import reverse, resolve

class QuoteCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of quoting stock prices.
	This includes testing the /quote/ url and the quote view. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_quote_url(self):

		self.assertEqual(resolve(reverse("quote")).func, quote)

	# test that GET requests sent to the view result in an error message
	def test_quote_get(self):

		response = self.client.get(reverse("quote"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that incomplete input results in an error message
	def test_quote_invalid_input(self):

		response = self.client.post(reverse("quote"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that submitting an invalid stock symbol results in an error message
	def test_quote_invalid_stock_symbol(self):

		response = self.client.post(reverse("quote"), {"symbol": "asdjhsajdh"})

		self.assertIn(json.dumps({"error": "1"}), str(response.content))

	# test that the view returns the requested data if the input is valid
	def test_quote_valid_input(self):

		response = self.client.post(reverse("quote"), {"symbol": "AAPL"})

		self.assertIn("AAPL", str(response.content))
		self.assertIn("Apple Inc.", str(response.content))