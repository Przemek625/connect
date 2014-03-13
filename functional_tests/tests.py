from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from django.contrib.auth.models import User

# test what happens from the users' points of view
# ================================================

class MemberVisitTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def test_can_login_via_login_page(self):

        sam = User.objects.create_user(username="sam",
                                       email="sam@example.com",
                                       password="pass")

        # Sam visits the connect homepage and sees that she needs to login
        self.browser.get(self.live_server_url)
        self.assertIn('Login', self.browser.title)

        # There she sees a login form with username and password fields
        input_username = self.browser.find_element_by_id('id_username')
        input_password = self.browser.find_element_by_id('id_password')

        # Sam enters her username and an incorrect password
        input_username.send_keys('sam')
        input_password.send_keys('wrongpass')
        input_password.send_keys(Keys.ENTER)

        # But is told that the username and password do not match
        header_content = self.browser.find_element_by_tag_name('header').text
        self.assertIn("Your username and password didn't match", header_content)

        # She tries again, this time with the correct password
        input_password = self.browser.find_element_by_id('id_password')

        input_password.send_keys('pass')
        input_password.send_keys(Keys.ENTER)

        # Success! She is redirected to the connect dashboard
        self.assertIn('Dashboard', self.browser.title)


# There she sees:

# A card for each member registered on the site, with:
# Member name
# Member gravatar (if they have one)
# Member connect preferences
# Member skills (and their proficiency)
# Member bio
# Member links

# Sam notices a form on the page where she can 'Refine' her search

## SKILLS/INTERESTS

# When she selects 'Django' and clicks on 'submit', she notices that
# the members she sees all have the skill 'Django'

# When she selects 'Django' and 'Game Development' she sees all of
# the members with the skills 'Django' OR 'Game Development'

## CONNECT PREFERENCES

# Sam also notices that she can filter results by their connect preferences.
# She selects 'Mentor' to see all of the members who have the preference 'mentor'.
# Likewise, when she selects 'Mentor' and 'Mentee' she sees all of the members
# with the preferences 'Mentor' OR 'Game Development'

# Sam notices that she can filter members by BOTH skill/interest & connect preference.
# She is looking for a Django mentor, so selects 'Django' and 'Mentor'
# All of the members listed in the results have the skill 'Django' and the
# preference 'Mentor'.

# Sam is also making a Python game and is looking for members to join her.
# She selects 'Game Development' and 'Coding Buddy', but there is nobody in
# the system who matches this search, so she sees a 'no results' message.
