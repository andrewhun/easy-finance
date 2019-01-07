from finance.helpers import wait_for
from .base import BaseFunctionalTestCase

class EditBalanceCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of
	changing the user's starting balance, from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().log_test_user_in()
		super().navigate_to_history()

	# close the browser after running each tests
	def tearDown(self):
		
		super().tearDown()

	# test that clicking on the "change starting balance" button displays the form
	def test_edit_balance_show_form(self):

		change_balance_button = self.driver.find_element_by_id("editbalance")
		change_balance_button.click()

		edit_balance_form = self.driver.find_element_by_id("edit_balance")
		wait_for(lambda: self.assertTrue(edit_balance_form.is_displayed()))

	# test that the edit balance form's field is required
	def test_edit_balance_form_field_is_required(self):

		edit_balance_amount = self.driver.find_element_by_id("edit_balance_amount")
		wait_for(lambda: self.assertTrue(edit_balance_amount.get_attribute("required")))

		# test that users can't enter negative values
		wait_for(lambda: self.assertEqual("0", edit_balance_amount.get_attribute("min")))

	# test that users can change their starting balance using the form
	def test_change_starting_balance(self):

		change_balance_button = self.driver.find_element_by_id("editbalance")
		change_balance_button.click()

		edit_balance_amount = self.driver.find_element_by_id("edit_balance_amount")
		edit_balance_amount.send_keys("2500")

		edit_balance_form = self.driver.find_element_by_id("edit_balance")
		edit_balance_form.submit()

		# wait for the page to reload
		wait_for(lambda: self.assertIn("Transaction history", self.driver.title))

		current_user_balance = super().get_current_user_balance()
		wait_for(lambda: self.assertEqual(2500.00, current_user_balance))

		starting_balance_statement = super().get_starting_balance_statement()
		wait_for(lambda: self.assertEqual("test1: Balance of 2500.00 USD", str(starting_balance_statement)))