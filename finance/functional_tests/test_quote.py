from .base import BaseFunctionalTestCase
from finance.helpers import wait_for, allow_time_to_load

class QuoteCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of
	getting stock price quotes from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().log_test_user_in()
		super().navigate_to_stocks()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that the form field is required
	def test_quote_field_is_required(self):

		quote_symbol_input = self.driver.find_element_by_id("quote_symbol")
		wait_for(lambda: self.assertTrue(quote_symbol_input.get_attribute("required")))

	# test that the user is notified if the stock symbol they typed in is not recognized
	def test_quote_invalid_stock_symbol(self):

		quote_symbol_input = self.driver.find_element_by_id("quote_symbol")
		quote_symbol_input.send_keys("asdfasd")

		quote_form = self.driver.find_element_by_id("quote")
		quote_form.submit()

		quote_error_div = self.driver.find_element_by_id("quotesymbol")
		wait_for(lambda: self.assertEqual("Invalid stock symbol", quote_error_div.text))

	# test that users receive stock quotes if they enter a valid stock symbol
	def test_get_quote_for_stock(self):

		quote_symbol_input = self.driver.find_element_by_id("quote_symbol")
		quote_symbol_input.send_keys("NFLX")

		quote_form = self.driver.find_element_by_id("quote")
		quote_form.submit()

		allow_time_to_load()

		alert = self.driver.switch_to.alert
		wait_for(lambda: self.assertIn("The price of a Netflix Inc. stock is", alert.text))