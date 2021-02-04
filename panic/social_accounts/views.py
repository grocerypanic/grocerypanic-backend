"""Social Views for the Social Accounts App"""

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView


class FacebookLogin(SocialLoginView):
  """Facebook Login Adapter"""
  authentication_classes = ()
  permission_classes = ()
  adapter_class = FacebookOAuth2Adapter


class GoogleLogin(SocialLoginView):
  """Google Login Adapter"""
  authentication_classes = ()
  permission_classes = ()
  adapter_class = GoogleOAuth2Adapter
