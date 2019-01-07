from finance.models import Statement
from .base import BaseFunctionalTestCase
from selenium.webdriver.support.ui import Select
from finance.helpers import wait_for, allow_time_to_load

class EditHistCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of editing
	entries in the financial statement table, from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().add_statement_entry()
		super().log_test_user_in()
		super().navigate_to_history()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

		# test that all fields in the edit entry form are optional
	def test_edit_hist_fields_are_optional(self):

		edit_hist_type = self.driver.find_element_by_id("edit_hist_type")
		wait_for(lambda: self.assertFalse(edit_hist_type.get_attribute("required")))

		edit_hist_amount = self.driver.find_element_by_id("edit_hist_amount")
		wait_for(lambda: self.assertFalse(edit_hist_amount.get_attribute("required")))
		# test that users can't enter negative amounts
		wait_for(lambda: self.assertEqual("0", edit_hist_amount.get_attribute("min")))

		edit_hist_title = self.driver.find_element_by_id("edit_hist_title")
		wait_for(lambda: self.assertFalse(edit_hist_title.get_attribute("required")))

	# test that clicking an "edit" button brings allows brings up the edit entry form,
	# and allows you to edit the entry that is associated with it
	def test_edit_hist_button(self):

		edit_hist_buttons = self.driver.find_elements_by_class_name("edit_hist")
		edit_hist_buttons[0]. click()

		edit_entry_form = self.driver.find_element_by_id("edit_hist")
		wait_for(lambda: self.assertTrue(edit_entry_form.is_displayed()))

		selected_entry = Statement.objects.get(statement_type = "Income")
		edit_hist_id = self.driver.find_element_by_id("edit_hist_id")
		wait_for(lambda: self.assertIn(str(selected_entry.id), edit_hist_id.text))

	# test that users can change the selected entry by submitting the edit entry form
	def test_edit_entry(self):

		edit_hist_buttons = self.driver.find_elements_by_class_name("edit_hist")
		edit_hist_buttons[0]. click()

		edit_hist_type = Select(self.driver.find_element_by_id("edit_hist_type"))
		edit_hist_type.select_by_visible_text("Expense")

		edit_hist_amount = self.driver.find_element_by_id("edit_hist_amount")
		edit_hist_amount.send_keys("300")

		edit_hist_title = self.driver.find_element_by_id("edit_hist_title")
		edit_hist_title.send_keys("Rent")

		edit_entry_form = self.driver.find_element_by_id("edit_hist")
		edit_entry_form.submit()

		# wait for the page to reload
		allow_time_to_load()

		edited_entry = Statement.objects.get(statement_type = "Expense")
		wait_for(lambda: self.assertEqual("test1: Expense of 300.00 USD", str(edited_entry)))

		# test that the user's balance has been adjusted according to the change
		current_user_balance = super().get_current_user_balance()
		wait_for(lambda: self.assertEqual(3700.00, current_user_balance))