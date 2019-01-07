from finance.helpers import wait_for
from .base import BaseFunctionalTestCase

class LoggedOutNavBarCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the navigation bar 
	which users can access when they are logged out. This version
	of should have three elements: the register and login
	links and the site logo, which should also redirect users to the
	login page. '''

	# set up for the tests
	def setUp(self):

		super().setUp()

	# close the browser after the tests run
	def tearDown(self):

		super().tearDown()

	# test that clicking the register link takes users to the register page
	def test_navbar_register_link(self):
		super().navigate_to_register()

		wait_for(lambda: self.assertIn("Registration", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/register/"), self.driver.current_url))

	# test that clicking the login link takes users to the login page
	def test_navbar_login_link(self):

		super().navigate_to_login()

		wait_for(lambda: self.assertIn("Log In", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/login/"), self.driver.current_url))

	# test that clicking the logo takes users to the login page too
	def test_navbar_logo_login(self):

		super().click_on_logo()

		wait_for(lambda: self.assertIn("Log In", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/login/"), self.driver.current_url))