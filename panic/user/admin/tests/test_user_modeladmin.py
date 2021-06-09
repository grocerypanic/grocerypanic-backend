"""Test for the user modeladmin."""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase

from ...tests.fixtures.fixtures_django import MockRequest
from ..user_modeladmin import UserModelAdmin

User = get_user_model()


class ModelAdminTests(TestCase):
  """Test for the user model admin."""

  @classmethod
  def setUpTestData(cls):
    cls.user = User.objects.create_user(
        username="test_user",
        email="test@test.com",
        password="test123",
    )

  def setUp(self):
    self.site = AdminSite()
    self.request = MockRequest()
    self.model_admin = UserModelAdmin(User, self.site)

  def test_base_fields(self):
    self.assertListEqual(
        list(self.model_admin.get_form(self.request).base_fields), [
            'username',
            'email',
            'password1',
            'password2',
            'timezone',
            'language_code',
        ]
    )
    self.assertListEqual(
        list(self.model_admin.get_fields(self.request)), [
            'username',
            'password1',
            'password2',
        ]
    )

  def test_included_fields(self):
    self.assertEqual(
        list(self.model_admin.get_fields(self.request, self.user)), [
            'password',
            'last_login',
            'is_superuser',
            'groups',
            'user_permissions',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_active',
            'date_joined',
            'language_code',
            'has_profile_initialized',
            'timezone',
        ]
    )

  def test_excluded_fields(self):
    self.assertIsNone(self.model_admin.get_exclude(self.request, self.user))

  def test_added_fieldsets(self):
    self.assertEqual(
        self.model_admin.get_fieldsets(self.request), ((
            None, {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'email',
                    'password1',
                    'password2',
                    'timezone',
                    'language_code',
                )
            }
        ),)
    )

  def test_fieldsets(self):
    self.assertEqual(
        self.model_admin.get_fieldsets(self.request, self.user), ((
            None,
            {
                'fields': ('username', 'password')
            },
        ), (
            'Personal info', {
                'fields': (
                    'first_name',
                    'last_name',
                    'email',
                    'timezone',
                    'language_code',
                )
            }
        ), (
            'Permissions', {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'has_profile_initialized',
                    'groups',
                    'user_permissions',
                )
            }
        ), (
            'Important dates',
            {
                'fields': (
                    'last_login',
                    'date_joined',
                )
            },
        ))
    )
