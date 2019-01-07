from .base import BaseFunctionalTestCase
from finance.helpers import wait_for, allow_time_to_load

class DeleteAllHistCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of reseting
	the user's account, from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().add_statement_entry()
		super().add_stocks_to_portfolio()
		super().add_transactions_to_history()
		super().log_test_user_in()
		super().navigate_to_history()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that users can reset their accounts by pressing the "delete all" button and confirming their decision
	def test_delete_all_statement_entries(self):

		delete_all_hist_button = self.driver.find_element_by_id("delete_all_hist")
		delete_all_hist_button.click()

		alert = self.driver.switch_to.alert
		alert.accept()

		# wait for the page to reload
		allow_time_to_load()

		# test that the user's financial statement was emptied (aside from the starting balance statement)
		number_of_statement_entries = super().count_statement_entries()
		wait_for(lambda: self.assertEqual(1, number_of_statement_entries))

		# test that the user's stock portfolio was emptied
		number_of_stocks_in_portfolio = super().count_stocks_in_portfolio()
		wait_for(lambda: self.assertEqual(0, number_of_stocks_in_portfolio))

		# test that the user's transaction history was emptied
		number_of_transactions = super().count_transaction_entries()
		wait_for(lambda: self.assertEqual(0, number_of_transactions))

		# test that the user's starting balance was reset to the default value
		current_user_balance = super().get_current_user_balance()
		wait_for(lambda: self.assertEqual(10000.00, current_user_balance))

		# test that the user's starting balance statement contains the correct amount
		starting_balance_statement = super().get_starting_balance_statement()
		wait_for(lambda: self.assertEqual(10000.00, starting_balance_statement.amount))