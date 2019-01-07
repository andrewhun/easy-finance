from finance.views import index
from .base import BaseUnitTestCase
from django.urls import reverse, resolve

class IndexCase(BaseUnitTestCase):
	''' This class is responsible for testing the main page.
	This includes testing the / url, index.html and the index view. '''

	# set up the test database
	def setUp(self):

		super().setUp()
		super().add_second_user()
		super().add_recurring_entries_for_first_user()
		super().add_statements_for_first_user()
		super().add_statements_for_second_user()
		
	# test the url
	def test_index_url(self):

		# test that logged out users are redirected to the login page
		response = self.client.get(reverse("index"))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, "/login/")

		# test that the view is connected to the url
		self.assertEqual(resolve(reverse("index")).func, index)
	
	# test that the view shows an error if it receives a POST request
	def test_index_post(self):

		super().login_as_first_user()

		response = self.client.post(reverse("index"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view presents the main page when it receives a GET request
	def test_index_get(self):

		super().login_as_first_user()

		response = self.client.get(reverse("index"))

		# test that the add recurring entry form is present
		self.assertIn("Add Recurring Entry</h2>", str(response.content))
		
		# test that the edit recurring entry form is present
		self.assertIn("Edit Recurring Entry</h2>", str(response.content))
		
		# test that the financial summary table is present and has the correct data
		self.assertIn("<h2>Financial Summary</h2>", str(response.content))
		self.assertEqual(100, response.context["income_sum"])
		self.assertEqual(25, response.context["expense_sum"])
		self.assertEqual(75, response.context["cash_flow"])

		first_user_balance = super().get_balance_for_first_user()
		self.assertEqual(first_user_balance, response.context["user_cash"])

		# test that the recurring entries table is present and has the correct data
		self.assertIn("<h2>Recurring Entries</h2>", str(response.content))
		self.assertIn("<td>1</td>", str(response.content))
		self.assertIn("<td>Income</td>", str(response.content))
		self.assertIn("<td>Work</td>", str(response.content))
		self.assertIn("<td>50.00</td>", str(response.content))
		self.assertIn("<td>Daily</td>", str(response.content))

	# test that users can only see their own data
	def test_index_separate_data(self):

		# log in as the second user
		super().login_as_second_user()

		# send a get request to the index view
		response = self.client.get(reverse("index"))
		
		# test that the first user's data is not present
		self.assertNotEqual(100, response.context["income_sum"])
		self.assertNotEqual(25, response.context["expense_sum"])
		self.assertNotEqual(75, response.context["cash_flow"])

		first_user_balance = super().get_balance_for_first_user()
		self.assertNotEqual(first_user_balance, response.context["user_cash"])

		self.assertNotIn("<td>1</td>", str(response.content))
		self.assertNotIn("<td>Income</td>", str(response.content))
		self.assertNotIn("<td>Work</td>", str(response.content))
		self.assertNotIn("<td>50.00</td>", str(response.content))
		self.assertNotIn("<td>Daily</td>", str(response.content))

		# test that the second user's data is present
		self.assertEqual(1000, response.context["income_sum"])
		self.assertEqual(325, response.context["expense_sum"])
		self.assertEqual(675, response.context["cash_flow"])

		second_user_balance = super().get_balance_for_second_user()
		self.assertEqual(second_user_balance, response.context["user_cash"])