"""Test the django allauth signup receivers for `user_signed_up`."""

from unittest.mock import patch

from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_signals import SignalTestHarness
from .. import signup


class TestSignedUpSignalHandler(SignalTestHarness):
  """Test the django allauth signal handler for `user_signed_up`."""

  @patch(signup.__name__ + ".user_signed_up_event")
  def test_signal_received(self, m_event):
    request = MockRequest()
    self.trigger(request)
    m_event.assert_called_with(request, self.user)
