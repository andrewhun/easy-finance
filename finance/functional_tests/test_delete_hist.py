from .base import BaseFunctionalTestCase
from finance.helpers import wait_for, allow_time_to_load

class DeleteHistCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the process of deleting 
	entries from the financial statement table, from the user's viewpoint. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().add_statement_entry()
		super().log_test_user_in()
		super().navigate_to_history()

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that users can delete an entry by clicking the "delete" button associated with it
	def test_delete_statement_entry(self):

		delete_buttons = self.driver.find_elements_by_class_name("delete_hist")
		delete_buttons[0].click()

		# wait for the page to reload
		allow_time_to_load()

		number_of_statement_entries = super().count_statement_entries()
		wait_for(lambda: self.assertEqual(1, number_of_statement_entries))

		# test that the user's cash was adjusted
		current_user_balance = super().get_current_user_balance()
		wait_for(lambda: self.assertEqual(4000.00, current_user_balance))