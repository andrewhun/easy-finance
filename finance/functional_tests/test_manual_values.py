from finance.models import Statement
from finance.helpers import wait_for
from .base import BaseFunctionalTestCase
from selenium.webdriver.support.ui import Select

class ManualValuesCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of adding entries
	 to the financial statement table, from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().add_statement_entry()
		super().log_test_user_in()
		super().navigate_to_history()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that all fields are required in the add recurring entries form
	def test_manual_values_form_fields_are_required(self):

		manual_type_input = self.driver.find_element_by_id("manual_type")
		wait_for(lambda: self.assertTrue(manual_type_input.get_attribute("required")))

		manual_amount_input = self.driver.find_element_by_id("manual_amount")
		wait_for(lambda: self.assertTrue(manual_amount_input.get_attribute("required")))
		# test that users can't enter negative amounts
		wait_for(lambda: self.assertEqual("0", manual_amount_input.get_attribute("min")))

		manual_title_input = self.driver.find_element_by_id("manual_title")
		wait_for(lambda: self.assertTrue(manual_title_input.get_attribute("required")))

	# test that users can add new entries to the financial statement table using the form
	def test_add_statement_entry(self):

		manual_type_select = Select(self.driver.find_element_by_id("manual_type"))
		manual_type_select.select_by_visible_text("Expense")

		manual_amount_input = self.driver.find_element_by_id("manual_amount")
		manual_amount_input.send_keys("25")

		manual_title_input = self.driver.find_element_by_id("manual_title")
		manual_title_input.send_keys("Groceries")

		add_entry_form = self.driver.find_element_by_id("manual_values")
		add_entry_form.submit()

		# wait for the page to reload
		wait_for(lambda: self.assertIn("Transaction history", self.driver.title))

		# test that the new entry was added successfully
		number_of_statement_entries = super().count_statement_entries()
		wait_for(lambda: self.assertEqual(3, number_of_statement_entries))

		new_statement_entry = Statement.objects.get(title = "Groceries")
		wait_for(lambda: self.assertEqual("test1: Expense of 25.00 USD", str(new_statement_entry)))

		# test that the user's balance was adjusted
		current_user_balance = super().get_current_user_balance()
		wait_for(lambda: self.assertEqual(4975.00, current_user_balance))