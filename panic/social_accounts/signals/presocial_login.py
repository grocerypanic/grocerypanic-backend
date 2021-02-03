"""Pre Social Login Signal Handler"""

from allauth.account.models import EmailAddress
from allauth.socialaccount.signals import pre_social_login
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.dispatch import receiver


# pylint: disable=unused-argument
@receiver(pre_social_login)
def pre_social_login_handler(request, sociallogin, **kwargs):
  """Responds the Django Allauth pre_social_login signal"""
  process_social_connect(request, sociallogin)


def process_social_connect(request, sociallogin):
  """Searches for unconnected existing users, and attempts to match
  them to the social login being used.

  :param request: A restframework request object
  :type request: :class:`rest_framework.request.Request`
  :param sociallogin: A django allauth sociallogin object
  :type sociallogin: :class:`allauth.socialaccount.models.SocialLogin`

  :returns: None
  :rtype: None
  """
  pre_social_connector = PreSocialConnector(sociallogin)
  user = pre_social_connector.get_user_for_connection()

  if user:
    sociallogin.connect(request, user)


class PreSocialConnector:
  """Finds existing users, for connecting to social accounts."""

  def __init__(self, sociallogin):
    self.sociallogin = sociallogin
    querymanager = EmailAddressQuery()
    self.query = querymanager.query

  def search_for_user(self):
    """Iterates through attached email addresses and queries for existing users.

    :returns: A django user object, or None
    :rtype: :class:`django.contrib.auth.models.User`, None
    """
    for email_address_object in self.sociallogin.email_addresses:
      result = self.query(email_address_object)
      if result:
        return result
    return None

  def get_user_for_connection(self):
    """Determines if a connectable user is present, and returns the user if so.

    :returns: A django user object, or None
    :rtype: :class:`django.contrib.auth.models.User`, None
    """
    if self.sociallogin.is_existing:
      return None
    if not self.sociallogin.email_addresses:
      return None
    return self.search_for_user()


class EmailAddressQuery:
  """Provides an common interface to multiple user queries."""

  def __init__(self):
    if settings.SOCIALACCOUNT_EMAIL_VERIFICATION:
      self.query = self.__verified_user_query
    else:
      self.query = self.__unverified_user_query

  @staticmethod
  def __unverified_user_query(email_address_object):
    """Performs a query over all allauth email addresses to find matching users.

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
    """Performs a query over verified allauth email addresses to find matching
    users.

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
