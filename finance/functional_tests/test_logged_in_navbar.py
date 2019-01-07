from finance.helpers import wait_for
from .base import BaseFunctionalTestCase

class LoggedInNavBarCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the navigation bar 
	which users can access when they are logged in. This version
	should have five elements: the site logo, the stocks link,
	the history link, the change password link and the logout link.  '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().log_test_user_in()

	# close the browser after the tests run
	def tearDown(self):

		super().tearDown()

	# test that clicking the stocks link takes users to the stocks page
	def test_navbar_stocks_link(self):

		super().navigate_to_stocks()

		wait_for(lambda: self.assertIn("Stocks", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/stocks/"), self.driver.current_url))

	# test that clicking the history link takes users to the history page
	def test_navbar_history_link(self):

		super().navigate_to_history()

		wait_for(lambda: self.assertIn("Transaction history", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/history/"), self.driver.current_url))

	# test that clicking the change password link takes users to the change password page
	def test_navbar_change_pw_link(self):

		super().navigate_to_change_pw()

		wait_for(lambda: self.assertIn("Changing password", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/change_pw/"), self.driver.current_url))

	# test that clicking the logout link logs users out
	def test_navbar_logout_link(self):

		logout_link = self.driver.find_element_by_link_text("Log Out")
		logout_link.click()

		wait_for(lambda: self.assertIn("Log In", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/login/"), self.driver.current_url))

		# test that users can't access the main page after logging out
		self.driver.get(self.live_server_url)

		wait_for(lambda: self.assertIn("Log In", self.driver.title))
		wait_for(lambda: self.assertEqual((self.live_server_url + "/login/"), self.driver.current_url))

	# test that clicking the logo takes users to the main page
	def test_navbar_logo_main_page(self):
		
		# make sure the login process is complete
		wait_for(lambda: self.assertIn("Main page", self.driver.title))

		super().click_on_logo()

		wait_for(lambda: self.assertEqual(self.live_server_url + "/", self.driver.current_url))