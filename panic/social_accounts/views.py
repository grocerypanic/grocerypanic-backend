"""Views for the social_accounts app."""

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings


class FacebookLogin(SocialLoginView):
  """Facebook login view."""

  authentication_classes = ()
  permission_classes = ()
  adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
  """Google login view."""

  adapter_class = GoogleOAuth2Adapter
  authentication_classes = ()
  callback_url = settings.GOOGLE_CALLBACK_URL
  client_class = OAuth2Client
