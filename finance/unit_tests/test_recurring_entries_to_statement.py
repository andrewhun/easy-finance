from .base import BaseUnitTestCase
from finance.helpers import add_daily_entries_to_statements, add_weekly_entries_to_statements, add_monthly_entries_to_statements

class RecurringEntryToStatementCase(BaseUnitTestCase):
	''' This class is responsible for testing the background functions that 
	add new entries to the financial statement table, based on the recurring
	entries. '''

	# set up the database and the client for the tests
	def setUp(self):

		super().setUp()
		super().add_second_user()
		super().add_recurring_entries_for_first_user()
		super().add_recurring_entries_for_second_user()

	# test that the daily entries are added to the statements table
	def test_daily_entries_to_statement(self):

		add_daily_entries_to_statements.now()

		first_user_statements_count = super().count_statements_for_first_user()
		self.assertEqual(2, first_user_statements_count)

		second_user_statements_count = super().count_statements_for_second_user()
		self.assertEqual(1, second_user_statements_count)

		# test that the user's balance is adjusted
		first_user_balance = super().get_balance_for_first_user()
		self.assertEqual(5050.00, first_user_balance)

		second_user_balance = super().get_balance_for_second_user()
		self.assertEqual(10000.00, second_user_balance)

	# test that the weekly entries are added to the statements table
	def test_weekly_entries_to_statement(self):

		add_weekly_entries_to_statements.now()

		first_user_statements_count = super().count_statements_for_first_user()
		self.assertEqual(2, first_user_statements_count)

		second_user_statements_count = super().count_statements_for_second_user()
		self.assertEqual(2, second_user_statements_count)

		# test that the user's balance is adjusted
		first_user_balance = super().get_balance_for_first_user()
		self.assertEqual(4925.00, first_user_balance)

		second_user_balance = super().get_balance_for_second_user()
		self.assertEqual(9975.00, second_user_balance)

	# test that the monthly entries are added to the statements table
	def test_monthly_entries_to_statement(self):

		add_monthly_entries_to_statements.now()

		first_user_statements_count = super().count_statements_for_first_user()
		self.assertEqual(1, first_user_statements_count)

		second_user_statements_count = super().count_statements_for_second_user()
		self.assertEqual(2, second_user_statements_count)

		# test that the user's balance is adjusted
		first_user_balance = super().get_balance_for_first_user()
		self.assertEqual(5000.00, first_user_balance)

		second_user_balance = super().get_balance_for_second_user()
		self.assertEqual(11000.00, second_user_balance)
