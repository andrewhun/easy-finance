from finance.models import Portfolio
from .base import BaseFunctionalTestCase
from finance.helpers import wait_for, allow_time_to_load

class BuyCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of
	buying shares from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().add_stocks_to_portfolio()
		super().log_test_user_in()
		super().navigate_to_stocks()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that all fields in the buy form are required
	def test_buy_form_fields_are_required(self):

		buy_symbol_input = self.driver.find_element_by_id("buy_symbol")
		wait_for(lambda: self.assertTrue(buy_symbol_input.get_attribute("required")))

		buy_shares_input = self.driver.find_element_by_id("buy_shares")
		wait_for(lambda: self.assertTrue(buy_shares_input.get_attribute("required")))
		wait_for(lambda: self.assertEqual("1", buy_shares_input.get_attribute("min")))

	# test that users are notified if they enter a stock symbol that is not recognized
	def test_buy_invalid_symbol(self):

		buy_symbol_input = self.driver.find_element_by_id("buy_symbol")
		buy_symbol_input.send_keys("asdfasd")

		buy_shares_input = self.driver.find_element_by_id("buy_shares")
		buy_shares_input.send_keys("5")

		buy_form = self.driver.find_element_by_id("buy")
		buy_form.submit()

		buy_invalid_symbol_div = self.driver.find_element_by_id("buysymbol")
		wait_for(lambda: self.assertEqual("Invalid stock symbol", buy_invalid_symbol_div.text))

	# test that users are notified if they have insufficient funds for the transactions
	def test_buy_insufficient_funds(self):

		buy_symbol_input = self.driver.find_element_by_id("buy_symbol")
		buy_symbol_input.send_keys("NFLX")

		buy_shares_input = self.driver.find_element_by_id("buy_shares")
		buy_shares_input.send_keys("10000000")

		buy_form = self.driver.find_element_by_id("buy")
		buy_form.submit()

		buy_insufficient_funds_div = self.driver.find_element_by_id("buyshares")
		wait_for(lambda: self.assertEqual("Insufficient funds", buy_insufficient_funds_div.text))

	# test that users can buy shares if they enter the correct details
	def test_buy_shares(self):

		buy_symbol_input = self.driver.find_element_by_id("buy_symbol")
		buy_symbol_input.send_keys("NFLX")

		buy_shares_input = self.driver.find_element_by_id("buy_shares")
		buy_shares_input.send_keys("5")

		buy_form = self.driver.find_element_by_id("buy")
		buy_form.submit()

		# wait for the page to reload
		allow_time_to_load()

		number_of_stocks_in_portfolio = super().count_stocks_in_portfolio()
		wait_for(lambda: self.assertEqual(3, number_of_stocks_in_portfolio))

		new_stock = Portfolio.objects.get(stock = "NFLX")
		wait_for(lambda: self.assertIn("test1: 5 shares of NFLX stock worth", str(new_stock)))