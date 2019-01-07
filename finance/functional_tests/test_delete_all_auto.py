from finance.models import Autovalue
from finance.helpers import wait_for
from .base import BaseFunctionalTestCase

class DeleteAllAutoCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process
	of emptying the recurring entries table from the user's viewpoint. '''

	def setUp(self):

		super().setUp()
		super().add_recurring_entries()
		super().log_test_user_in()

	def tearDown(self):

		super().tearDown()

	# test that the delete all entries button empties the recurring entries table
	def test_empty_recurring_entries_table(self):

		delete_all_button = self.driver.find_element_by_id("delete_all_auto")
		delete_all_button.click()

		# confirm deleting all recurring entries
		alert = self.driver.switch_to.alert
		alert.accept()

		# allow time for the page to reload
		wait_for(lambda: self.assertIn("Main page", self.driver.title))
		
		number_of_recurring_entries = super().count_recurring_entries()
		wait_for(lambda: self.assertEqual(0, number_of_recurring_entries))
