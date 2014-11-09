from django.contrib.auth.models import Group
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.test import TestCase, RequestFactory

from connect_config.factories import SiteConfigFactory

from accounts.factories import UserFactory
from accounts.utils import (create_inactive_user, get_user,
                            invite_user_to_reactivate_account)


class AccountUtilsTest(TestCase):
    fixtures = ['group_perms']

    def setUp(self):
        self.standard_user = UserFactory(email='myuser@test.test')
        self.factory = RequestFactory()
        self.site = get_current_site(self.client.request)
        self.site.config = SiteConfigFactory(site=self.site)
        self.closed_user = UserFactory(
            first_name='Closed',
            email='closed.user@test.test',
            is_closed=True,
        )

    def test_create_inactive_user(self):
        user = create_inactive_user('test@test.test', 'first', 'last')
        moderators = Group.objects.get(name='moderators')

        self.assertEqual(user.email, 'test@test.test')
        self.assertEqual(user.first_name, 'first')
        self.assertEqual(user.last_name, 'last')
        self.assertEqual(user.is_active, False)
        self.assertEqual(user.is_moderator, False)
        self.assertNotIn(moderators, user.groups.all())

    def test_reactivated_account_token_is_reset(self):
        initial_token = self.standard_user.auth_token
        request = self.factory.get(reverse('accounts:request-invitation'))
        user = invite_user_to_reactivate_account(self.standard_user, request)

        self.assertNotEqual(initial_token, user.auth_token)
        self.assertFalse(user.auth_token_is_used)

    def test_reactivation_email_sent_to_user(self):
        request = self.factory.get('/')
        invite_user_to_reactivate_account(self.closed_user, request)

        expected_subject = 'Reactivate your {} account'.format(self.site.name)
        expected_intro = 'Hi {},'.format(self.closed_user.first_name)
        expected_content = '{} using this email address.'.format(self.site.name)
        expected_url = 'http://testserver/accounts/activate/{}'.format(
            self.closed_user.auth_token
        )
        email = mail.outbox[0]

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(email.subject, expected_subject)
        self.assertIn(expected_intro, email.body)
        self.assertIn(expected_content, email.body)
        self.assertIn(expected_url, email.body)

    def test_get_user(self):
        user = get_user('myuser@test.test')

        self.assertEqual(user, self.standard_user)