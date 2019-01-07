from finance.views import stocks
from finance.helpers import lookup
from .base import BaseUnitTestCase
from finance.models import Portfolio
from django.urls import reverse, resolve

class StocksCase(BaseUnitTestCase):
	''' This class is responsible for testing the stocks page.
	This includes testing the /stocks/ url, the stocks view,
	the Portfolio model and stocks.html. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_second_user()
		super().add_stocks_for_first_user()
		super().add_stocks_for_second_user()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_stocks_url(self):

		self.assertEqual(resolve(reverse("stocks")).func, stocks)

	# test the Portfolio model
	def test_portfolio_model(self):

		stocks_count = len(Portfolio.objects.all())
		self.assertEqual(stocks_count, 4)

		netflix = Portfolio.objects.get(user = self.test1, stock = "NFLX")

		self.assertEqual("test1: 5 shares of NFLX stock worth 1300.00", str(netflix))

	# test that POST requests sent to the view result in an error message
	def test_stocks_post(self):

		response = self.client.post(reverse("stocks"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view handles GET requests
	def test_stocks_get(self):

		# test that the correct data is passed on to the client
		response = self.client.get(reverse("stocks"))

		self.assertEqual(response.status_code, 200)

		first_user_balance = super().get_balance_for_first_user()
		self.assertEqual(first_user_balance, response.context["user_cash"])

		apple_stock = Portfolio.objects.get(user = self.test1, stock = "AAPL")
		apple_price = apple_stock.current_price
		apple_value = apple_stock.value

		netflix_value = Portfolio.objects.get(user = self.test1, stock = "NFLX").value

		grand_total = first_user_balance + apple_value + netflix_value

		self.assertEqual(grand_total, response.context["grand_total"])

		# test that the Portfolio table is present and has the correct data
		self.assertIn("<th>AAPL</th>", str(response.content))
		self.assertIn("<td>0</td>", str(response.content))
		self.assertIn(str(apple_price), str(response.content))
		self.assertIn(str(float(apple_value)), str(response.content))
		self.assertIn(str(first_user_balance), str(response.content))
		self.assertIn(str(grand_total), str(response.content))

		# test that the quote form is present
		self.assertIn("Get a quote</h2>", str(response.content))
		# test that the buy form is present
		self.assertIn("Buying shares</h2>", str(response.content))
		# test that the sell form is present
		self.assertIn("Selling shares</h2>", str(response.content))

	# test that users can see only their own data
	def test_stocks_separate_data(self):

		super().log_current_user_out()
		super().login_as_second_user()

		response = self.client.get(reverse("stocks"))

		second_user_balance = super().get_balance_for_second_user()
		self.assertEqual(second_user_balance, response.context["user_cash"])

		ge_stock = Portfolio.objects.get(user = self.test2, stock = "GE")
		ge_price = ge_stock.current_price
		ge_value = ge_stock.value

		amd_value = Portfolio.objects.get(user = self.test2, stock = "AMD").value

		grand_total = second_user_balance + ge_value + amd_value

		self.assertEqual(grand_total, response.context["grand_total"])

		self.assertNotIn("<th>AAPL</th>", str(response.content))
		self.assertNotIn("<td>10</td>", str(response.content))
		self.assertNotIn(str(lookup("AAPL")["price"]), str(response.content))
	
		self.assertIn("<th>GE</th>", str(response.content))
		self.assertIn("<td>100</td>", str(response.content))
		self.assertIn(str(ge_price), str(response.content))
		self.assertIn(str(float(ge_value)), str(response.content))
		self.assertIn(str(second_user_balance), str(response.content))
		self.assertIn(str(grand_total), str(response.content))