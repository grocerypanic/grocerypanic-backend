"""Views for the legal app."""

from django.views.generic.base import TemplateView


class TOSView(TemplateView):
  """Terms of Service view."""

  template_name = 'tos.html'


class PrivacyPolicyView(TemplateView):
  """Privacy Policy view."""

  template_name = 'privacy.html'
