"""Generate a Django superuser."""

from django.contrib.auth import get_user_model
from django.db import Error

User = get_user_model()

ERROR_MESSAGE = 'The admin user already exists.'


def create_superuser(username="admin", password="admin"):  # nosec
  """Create a django superuser, with the specified name and password.

  :param username: The username to create
  :type username: str
  :param password: The password to create
  :type password: str

  :returns: The user object, or None
  :rtype: :class:`django.contrib.auth.base_user.AbstractBaseUser`, None
  """

  exists = User.objects.all().filter(username=username).count()
  if exists:
    raise Error(ERROR_MESSAGE)  # pylint: disable=broad-exception-raised

  user = User(
      username=username,
      email="test@example.com",
      is_superuser=True,
      is_staff=True,
  )
  user.set_password(password)
  user.save()

  return user
