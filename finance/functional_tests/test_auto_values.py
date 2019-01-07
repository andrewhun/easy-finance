from finance.models import Autovalue
from finance.helpers import wait_for
from .base import BaseFunctionalTestCase
from selenium.webdriver.support.ui import Select

class AutoValuesCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the form that adds
	recurring entries from the user's point of view. This includes
	testing if the form fields are required, and testing adding recurring entries. '''

	def setUp(self):

		super().setUp()
		super().add_recurring_entries()
		super().log_test_user_in()

	def tearDown(self):

		super().tearDown()

	# test that all fields are required 
	def test_auto_values_required_fields(self):

		auto_type_input = self.driver.find_element_by_id("auto_type")
		wait_for(lambda: self.assertTrue(auto_type_input.get_attribute("required")))

		auto_title_input = self.driver.find_element_by_id("auto_title")
		wait_for(lambda: self.assertTrue(auto_title_input.get_attribute("required")))

		auto_amount_input = self.driver.find_element_by_id("auto_amount")
		wait_for(lambda: self.assertTrue(auto_amount_input.get_attribute("required")))

		# test that the user can't enter negative values as amount
		wait_for(lambda: self.assertEqual('0', auto_amount_input.get_attribute("min")))

		frequency_input = self.driver.find_element_by_id("frequency")
		wait_for(lambda: self.assertTrue(frequency_input.get_attribute("required")))

	# test that users can add recurring entries
	def test_auto_values_add_recurring_entry(self):
		
		frequency_select = Select(self.driver.find_element_by_id("frequency"))
		frequency_select.select_by_visible_text("Daily")

		auto_type_select = Select(self.driver.find_element_by_id("auto_type"))
		auto_type_select.select_by_visible_text("Expense")

		auto_title_input = self.driver.find_element_by_id("auto_title")
		auto_title_input.send_keys("Smoking")

		auto_amount_input = self.driver.find_element_by_id("auto_amount")
		auto_amount_input.send_keys("5")

		auto_values_form = self.driver.find_element_by_id("auto_values")
		auto_values_form.submit()

		number_of_recurring_entries = super().count_recurring_entries()
		wait_for(lambda: self.assertEqual(4, number_of_recurring_entries))

		new_recurring_entry = Autovalue.objects.get(title = "Smoking")
		wait_for(lambda: self.assertEqual("test1: Expense of 5.00 USD recurring at Daily frequency",
		 str(new_recurring_entry)))