from finance.models import Portfolio
from .base import BaseFunctionalTestCase
from finance.helpers import wait_for, allow_time_to_load

class SellCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of
	selling shares from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().add_stocks_to_portfolio()
		super().log_test_user_in()
		super().navigate_to_stocks()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that all fields are required in the sell form
	def test_sell_form_fields_are_required(self):

		sell_symbol_input = self.driver.find_element_by_id("sell_symbol")
		wait_for(lambda: self.assertTrue(sell_symbol_input.get_attribute("required")))

		sell_shares_input = self.driver.find_element_by_id("sell_shares")
		wait_for(lambda: self.assertTrue(sell_shares_input.get_attribute("required")))
		wait_for(lambda: self.assertEqual("1", sell_shares_input.get_attribute("min")))

	# test that users can sell stocks if they enter the correct details
	def test_sell_shares(self):

		sell_symbol_input = self.driver.find_element_by_id("sell_symbol")
		sell_symbol_input.send_keys("AAPL")

		sell_shares_input = self.driver.find_element_by_id("sell_shares")
		sell_shares_input.send_keys("5")

		sell_form = self.driver.find_element_by_id("sell")
		sell_form.submit()

		allow_time_to_load()

		apple_shares = Portfolio.objects.get(stock = "AAPL").shares
		wait_for(lambda: self.assertEqual(5, apple_shares))

	# test that users are notified if they try to sell shares of a stock they don't own
	def test_sell_no_shares(self):

		sell_symbol_input = self.driver.find_element_by_id("sell_symbol")
		sell_symbol_input.send_keys("GE")

		sell_shares_input = self.driver.find_element_by_id("sell_shares")
		sell_shares_input.send_keys("5")

		sell_form = self.driver.find_element_by_id("sell")
		sell_form.submit()

		sell_no_shares_div = self.driver.find_element_by_id("sellsymbol")
		wait_for(lambda: self.assertEqual("You don't own any shares of this stock", sell_no_shares_div.text))

	# test that users are notified if they are trying to sell more shares than they have
	def test_sell_not_enough_shares(self):

		sell_symbol_input = self.driver.find_element_by_id("sell_symbol")
		sell_symbol_input.send_keys("AAPL")

		sell_shares_input = self.driver.find_element_by_id("sell_shares")
		sell_shares_input.send_keys("11")

		sell_form = self.driver.find_element_by_id("sell")
		sell_form.submit()

		sell_not_enough_shares_div = self.driver.find_element_by_id("sellshares")
		wait_for(lambda: self.assertEqual("You don't own enough shares for this transaction", 
			sell_not_enough_shares_div.text))