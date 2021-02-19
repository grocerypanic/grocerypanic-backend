"""Sign Up Signal Handler"""

from allauth.account.signals import user_signed_up
from django.dispatch import receiver


# pylint: disable=unused-argument
@receiver(user_signed_up)
def user_signed_up_handler(request, user, **kwargs):
  """Receive the `user_signed_up` signal from django all auth.

  :param request: A rest_framework request object
  :type request: :class:`rest_framework.request.Request`
  :param user: A django allauth sociallogin object
  :type user: :class:`user.models.user.User`
  """
  user_signed_up_event(request, user)


# pylint: disable=unused-argument
def user_signed_up_event(request, user):
  """Process a `user_signed_up` signal from django all auth.

  :param request: A rest_framework request object
  :type request: :class:`rest_framework.request.Request`
  :param user: A django allauth sociallogin object
  :type user: :class:`user.models.user.User`
  """
