"""Functional test base classes."""

import pytz
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APILiveServerTestCase, RequestsClient

USER_AUTH_CSRF = reverse('spa_security:csrf')
USER_LOGIN = reverse('rest_login')
USER_LOGOUT = reverse('rest_logout')

User = get_user_model()


class AuthenticationRegistrationTestHarness(APILiveServerTestCase):
  """Test harness for Authentication/Registration integration testing."""

  client_class = RequestsClient

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.password = "string12345"
    cls.timezone = "America/Toronto"
    cls.language_code = "ko"
    cls.user_base_data = {
        'username': 'test1',
        'email': 'test@testingniall.com',
    }
    cls.user_registration_data = dict(cls.user_base_data)
    cls.user_registration_data.update({
        'password1': cls.password,
        'password2': cls.password,
    })
    cls.user_login_data = dict(cls.user_base_data)
    cls.user_login_data.update({
        'password': cls.password,
    })
    cls.objects = []
    cls.generator = default_token_generator

  def setUp(self):
    self.client = RequestsClient()

  def tearDown(self):
    for obj in self.objects:
      if obj.id:
        obj.delete()

  def _build_url(self, endpoint):
    return f"{self.live_server_url}{endpoint}"

  def _login(self, expected_status=status.HTTP_200_OK):
    url = self._build_url(USER_LOGIN)
    response = self.client.post(url, self.user_login_data)
    self.assertEqual(response.status_code, expected_status)
    return response

  def _logout(self):
    url = self._build_url(USER_LOGOUT)
    response = self.client.post(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    return response

  def _data_generate_user(
      self,
      has_profile_initialized=False,
      verified=False,
      active=True,
  ):
    user_data = dict(self.user_login_data)
    user_data.update({
        "timezone": self.timezone,
        "language_code": self.language_code,
    })

    user = User.objects.create_user(**user_data, is_active=active)
    user.has_profile_initialized = has_profile_initialized
    user.save()

    email = EmailAddress(user=user, email=user.email, verified=verified)
    email.save()

    self.objects += [user, email]
    return user, email

  def _query_for_user(self):
    user = User.objects.get(username=self.user_registration_data['username'])
    self.objects.append(user)
    return user

  @staticmethod
  def _query_for_email(user):
    return EmailAddress.objects.get(user=user)


class APICrudTestHarness(APILiveServerTestCase):
  """Test harness for API integration testing."""

  client_class = RequestsClient
  test_view: str

  @classmethod
  def setUpClass(cls):

    super().setUpClass()
    cls.password = "string12345"
    cls.timezone = "America/Toronto"
    cls.language_code = "ko"
    cls.user_base_data = {
        'username': 'test1',
        'email': 'test@testingniall.com',
    }
    cls.user_registration_data = dict(cls.user_base_data)
    cls.user_registration_data.update({
        'password1': cls.password,
        'password2': cls.password,
    })
    cls.user_login_data = dict(cls.user_base_data)
    cls.user_login_data.update({
        'password': cls.password,
    })
    cls.objects = []
    cls.generator = default_token_generator
    cls.user = None
    cls.email = None
    cls.view = cls.get_test_view()

  @classmethod
  def get_test_view(cls):
    if cls.test_view.endswith("-pk"):
      actual_view = cls.test_view[:-3]

      def pk_reverse(_, pk):
        return reverse(actual_view, args=[pk])

      return pk_reverse
    return reverse(cls.test_view)

  @classmethod
  def tearDownClass(cls):
    super().tearDownClass()
    for obj in cls.objects:
      if obj.id:
        obj.delete()

  def _api_create(self, create_data, view):
    url = self._build_url(view)
    return self.client.post(url, create_data)

  def _api_delete(self, object_pk, view):
    url = self._build_url(view)
    return self.client.delete(url + str(object_pk) + "/")

  def _api_detail(self, object_pk, view):
    url = self._build_url(view)
    return self.client.get(url + str(object_pk) + "/")

  def _api_list(self, view):
    url = self._build_url(view)
    return self.client.get(url)

  def _api_patch(self, object_pk, patch_data, view):
    url = self._build_url(view)
    return self.client.patch(url + str(object_pk) + "/", patch_data)

  def _api_put(self, object_pk, put_data, view):
    url = self._build_url(view)
    return self.client.patch(url + str(object_pk) + "/", put_data)

  def _authorize(self):
    self._data_create_user(verified=True, has_profile_initialized=True)
    self._authorize_login()
    self._authorize_csrf()

  def _authorize_csrf(self):
    url = self._build_url(USER_AUTH_CSRF)
    response = self.client.get(url)
    csrf_token = response.json()['token']
    self.client.headers.update({'X-CSRFToken': csrf_token})
    return response

  def _authorize_login(self):
    url = self._build_url(USER_LOGIN)
    response = self.client.post(url, self.user_login_data)
    return response

  def _build_url(self, endpoint):
    return f"{self.live_server_url}{endpoint}"

  @staticmethod
  def _convert_datetime_to_drf_str(date_time):
    return date_time.astimezone(pytz.utc).isoformat().replace("+00:00", "Z")

  def _data_create_user(self, has_profile_initialized=False, verified=False):
    user_data = dict(self.user_login_data)
    user_data.update({
        "timezone": self.timezone,
        "language_code": self.language_code,
    })

    self.user = User.objects.create_user(**user_data)
    self.user.has_profile_initialized = has_profile_initialized
    self.user.save()

    self.email = EmailAddress(
        user=self.user,
        email=self.user.email,
        verified=verified,
    )
    self.email.save()

    self.objects += [self.user, self.email]
    return self.user, self.email


class APICrudTestHarnessUnauthorized(APICrudTestHarness):
  """Test harness for API integration testing authorized endpoints."""

  __test__ = False
  __non_pk_checks__ = True
  __pk_checks__ = True

  methods = {
      'get': status.HTTP_401_UNAUTHORIZED,
      'put': status.HTTP_401_UNAUTHORIZED,
      'patch': status.HTTP_401_UNAUTHORIZED,
      'post': status.HTTP_401_UNAUTHORIZED,
      'options': status.HTTP_401_UNAUTHORIZED,
  }
  methods_with_pk = {
      'get': status.HTTP_401_UNAUTHORIZED,
      'put': status.HTTP_401_UNAUTHORIZED,
      'patch': status.HTTP_401_UNAUTHORIZED,
      'post': status.HTTP_401_UNAUTHORIZED,
      'options': status.HTTP_401_UNAUTHORIZED,
  }

  def _security_methods(self):

    for method, expected_status_code in self.methods.items():
      with self.subTest(
          method=method, expected_status_code=expected_status_code
      ):
        client_method = getattr(self.client, method)
        response = client_method(self._build_url(self.view), data={})

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'}
        )

  def _security_methods_with_pk(self):

    for method, expected_status_code in self.methods_with_pk.items():
      with self.subTest(
          method=method, expected_status_code=expected_status_code
      ):
        client_method = getattr(self.client, method)
        response = client_method(self._get_url_from_view(), data={})

        self.assertEqual(response.status_code, expected_status_code)
        self.assertEqual(
            response.json(),
            {'detail': 'Authentication credentials were not provided.'}
        )

  def _get_url_from_view(self):
    if callable(self.view):
      return self._build_url(self.view(1))
    return self._build_url(self.view) + '1/'

  def test_http_methods(self):
    if self.__non_pk_checks__:
      self._security_methods()

  def test_http_methods_with_pk(self):
    if self.__pk_checks__:
      self._security_methods_with_pk()
