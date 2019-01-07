from finance.models import Autovalue
from finance.helpers import wait_for
from .base import BaseFunctionalTestCase

class DeleteAutoCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process
	of deleting recurring entries from the user's viewpoint. '''

	def setUp(self):

		super().setUp()
		super().add_recurring_entries()
		super().log_test_user_in()

	def tearDown(self):

		super().tearDown()

	# test that pressing a delete button deletes the recurring entry associated with it
	def test_delete_recurring_entry(self):

		delete_buttons = self.driver.find_elements_by_class_name("delete_auto")
		delete_buttons[0].click()

		wait_for(lambda: self.assertNotIn("<td>Income</td>", self.driver.page_source))
		wait_for(lambda: self.assertNotIn("<td>Work</td>", self.driver.page_source))
		wait_for(lambda: self.assertNotIn("<td>50.00</td>", self.driver.page_source))
		wait_for(lambda: self.assertNotIn("<td>Daily</td>", self.driver.page_source))

		number_of_recurring_entries = super().count_recurring_entries()
		wait_for(lambda: self.assertEqual(2, number_of_recurring_entries))