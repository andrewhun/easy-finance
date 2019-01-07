from finance.models import Autovalue
from finance.helpers import wait_for
from .base import BaseFunctionalTestCase
from selenium.webdriver.support.ui import Select

class EditAutoCase(BaseFunctionalTestCase):
	''' This class is responsible for testing editing recurring entries from
	the user's point of view. This includes testing if the form's fields are
	required and testing the process of editing recurring entries. '''

	def setUp(self):

		super().setUp()
		super().add_recurring_entries()
		super().log_test_user_in()

	def tearDown(self):

		super().tearDown()

	# test that clicking an edit button brings up the edit recurring entries form
	def test_edit_auto_show_form(self):

		edit_buttons = self.driver.find_elements_by_class_name("edit_auto")

		edit_buttons[0].click()

		# test that the correct entry ID is displayed
		edit_id_div = self.driver.find_element_by_id("edit_id")
		income_entry = Autovalue.objects.get(title = "Work")
		wait_for(lambda: self.assertIn(str(income_entry.id), edit_id_div.text))

		edit_form = self.driver.find_element_by_id("edit_auto")
		wait_for(lambda: self.assertTrue(edit_form.is_displayed()))
	# test that all fields in the edit recurring entry form are optional
	def test_edit_auto_form_fields_are_optional(self):

		edit_type_input = self.driver.find_element_by_id("edit_type")
		wait_for(lambda: self.assertFalse(edit_type_input.get_attribute("required")))

		edit_title_input = self.driver.find_element_by_id("edit_title")
		wait_for(lambda: self.assertFalse(edit_title_input.get_attribute("required")))

		edit_amount_input = self.driver.find_element_by_id("edit_amount")
		wait_for(lambda: self.assertFalse(edit_amount_input.get_attribute("required")))

		# test that users can't enter negative values as amount
		wait_for(lambda: self.assertEqual('0', edit_amount_input.get_attribute("min")))

		edit_frequency_input = self.driver.find_element_by_id("edit_frequency")
		wait_for(lambda: self.assertFalse(edit_frequency_input.get_attribute("required")))

	# test that users can change any attribute they want
	def test_edit_recurring_entry(self):

		edit_buttons = self.driver.find_elements_by_class_name("edit_auto")

		edit_buttons[0].click()

		edit_type_select = Select(self.driver.find_element_by_id("edit_type"))
		edit_type_select.select_by_visible_text("Expense")

		edit_title_input = self.driver.find_element_by_id("edit_title")
		edit_title_input.send_keys("Gambling")

		edit_amount_input = self.driver.find_element_by_id("edit_amount")
		edit_amount_input.send_keys("35")

		edit_frequency_select = Select(self.driver.find_element_by_id("edit_frequency"))
		edit_frequency_select.select_by_visible_text("Weekly")

		edit_form = self.driver.find_element_by_id("edit_auto")
		edit_form.submit()

		# test that the old values are no longer visible
		wait_for(lambda: self.assertNotIn("<td>Income</td>", self.driver.page_source))
		wait_for(lambda: self.assertNotIn("<td>Work</td>", self.driver.page_source))
		wait_for(lambda: self.assertNotIn("<td>50.00</td>", self.driver.page_source))
		wait_for(lambda: self.assertNotIn("<td>Daily</td>", self.driver.page_source))

		# test that the entry has been edited correctly
		edited_recurring_entry = Autovalue.objects.get(title = "Gambling")
		wait_for(lambda: self.assertEqual("test1: Expense of 35.00 USD recurring at Weekly frequency", 
			str(edited_recurring_entry)))