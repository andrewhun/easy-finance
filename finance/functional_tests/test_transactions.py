from finance.helpers import wait_for
from .base import BaseFunctionalTestCase

class TransactionCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the functions of
	the transaction history table, from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().add_transactions_to_history()
		super().log_test_user_in()
		super().navigate_to_history()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that the "hide transaction history" / "show transaction history" buttons work
	def test_transaction_history_buttons(self):

		# hide the transaction history
		hide_transactions_button = self.driver.find_element_by_id("hidetransactions")
		hide_transactions_button.click()

		# test that the "hide" button is hidden
		wait_for(lambda: self.assertFalse(hide_transactions_button.is_displayed()))

		# test that the table is hidden
		transactions_table = self.driver.find_element_by_id("transactions")
		wait_for(lambda: self.assertFalse(transactions_table.is_displayed()))

		# test that the "show" button is displayed
		show_transactions_button = self.driver.find_element_by_id("showtransactions")
		wait_for(lambda: self.assertTrue(show_transactions_button.is_displayed()))

		# display the transaction history
		show_transactions_button.click()

		# test that the "show" button is hidden
		wait_for(lambda: self.assertFalse(show_transactions_button.is_displayed()))

		# test that the table is displayed
		wait_for(lambda: self.assertTrue(transactions_table.is_displayed()))

		# test that the "hide" button is displayed
		wait_for(lambda: self.assertTrue(hide_transactions_button.is_displayed()))