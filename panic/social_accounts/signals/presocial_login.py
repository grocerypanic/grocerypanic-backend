"""Handles the `pre_social_login` signal from django-allauth."""

from allauth.account.models import EmailAddress
from allauth.socialaccount.signals import pre_social_login
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver


# pylint: disable=unused-argument
@receiver(pre_social_login)
def pre_social_login_handler(request, sociallogin, **kwargs):
  """Receive the django-allauth `pre_social_login` signal.

  :param request: A rest_framework request object
  :type request: :class:`rest_framework.request.Request`
  :param sociallogin: A django allauth sociallogin object
  :type sociallogin: :class:`allauth.socialaccount.models.SocialLogin`
  """

  process_social_connect(request, sociallogin)


def process_social_connect(request, sociallogin):
  """Connect am existing social account to a new provider, if prudent.

  :param request: A rest_framework request object
  :type request: :class:`rest_framework.request.Request`
  :param sociallogin: A django allauth sociallogin object
  :type sociallogin: :class:`allauth.socialaccount.models.SocialLogin`
  """
  pre_social_connector = PreSocialConnector(sociallogin)
  user = pre_social_connector.get_user_for_connection()

  if user:
    sociallogin.connect(request, user)


class PreSocialConnector:
  """Connection between social logins and existing django user accounts."""

  def __init__(self, sociallogin):
    self.sociallogin = sociallogin
    query_manager = EmailAddressQuery()
    self.query = query_manager.query

  def search_for_user(self):
    """Iterate through attached email addresses and query for existing users.

    :returns: A django user object, or None
    :rtype: :class:`django.contrib.auth.models.User`, None
    """
    for email_address_object in self.sociallogin.email_addresses:
      result = self.query(email_address_object)
      if result:
        return result
    return None

  def get_user_for_connection(self):
    """Determine if a connectable user is present, and returns the user if so.

    :returns: A django user object, or None
    :rtype: :class:`django.contrib.auth.models.User`, None
    """
    if self.sociallogin.is_existing:
      return None
    if not self.sociallogin.email_addresses:
      return None
    return self.search_for_user()


class EmailAddressQuery:
  """Provide an common interface to multiple user queries."""

  def __init__(self):
    if settings.SOCIALACCOUNT_EMAIL_VERIFICATION:
      self.query = self.__verified_user_query
    else:
      self.query = self.__unverified_user_query

  @staticmethod
  def __unverified_user_query(email_address_object):
    """Perform a query over all django-allauth email addresses to find matching
    django users.

    :param email_address_object: The allauth email address object to search for
    :type email_address_object: :class:`allauth.account.models.EmailAddress`

    :returns: A django user object, or None
    :rtype: :class:`django.contrib.auth.models.User`, None
    """
    email = email_address_object.email
    try:
      return EmailAddress.objects.get(email__iexact=email).user
    except ObjectDoesNotExist:
      return None

  @staticmethod
  def __verified_user_query(email_address_object):
    """Perform a query over all verified django-allauth email addresses to find
    matching django users.

    :param email_address_object: The allauth email address object to search for
    :type email_address_object: :class:`allauth.account.models.EmailAddress`

    :returns: A django user object, or None
    :rtype: :class:`django.contrib.auth.models.User`, None
    """
    email = email_address_object.email
    try:
      return EmailAddress.objects.get(
          email__iexact=email,
          verified=True,
      ).user
    except ObjectDoesNotExist:
      return None
