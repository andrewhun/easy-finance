from .base import BaseUnitTestCase
from finance.views import logout_view
from django.urls import reverse, resolve

class LogoutCase(BaseUnitTestCase):
	'''This class is responsible for testing the logout process.
	This includes testing the /logout/ url and logout_view.'''

	# set up the test database
	def setUp(self):

		super().setUp()

	# test that the url and logout_view are connected
	def test_logout_url(self):

		self.assertEqual(resolve(reverse("logout")).func, logout_view)
	
	# test that the view logs users out when the url is accessed
	def test_logout_request(self):

		# log the client in
		super().login_as_first_user()

		# navigate to the main page
		response = self.client.get(reverse("index"))
		
		# main page should load because the client is logged in
		self.assertEqual(response.status_code, 200)
		
		# navigate to the logout route
		response2 = self.client.get(reverse("logout"))
		
		# client should be logged out and redirected to the login page
		self.assertEqual(response2.status_code, 302)
		self.assertEqual(response2.url, "/login/")
		
		# navigate to the main page again
		response3 = self.client.get(reverse("index"))
		
		# client should be redirected to the login page because it has been logged out
		self.assertEqual(response3.status_code, 302)
		self.assertEqual(response3.url, "/login/")