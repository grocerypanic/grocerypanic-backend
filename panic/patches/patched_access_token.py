"""PatchedAccessToken class."""

from rest_framework_simplejwt.tokens import (
    AccessToken,
    AuthUser,
    Token,
    TokenError,
)


class PatchedAccessToken(AccessToken):
  """Patch CVE-2024-22513."""

  @classmethod
  def for_user(cls, user: AuthUser) -> "Token":
    """Return an authorization token for the given user.

    :param user: A django user object
    :type user: :class:`user.models.user.User`
    """

    if user and user.is_active:
      return super().for_user(user)
    raise TokenError("Token is invalid or expired")
