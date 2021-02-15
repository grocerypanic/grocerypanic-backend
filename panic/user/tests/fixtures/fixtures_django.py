"""Fixtures related to the Django framework."""


class MockRequest:
  """Test double for a request object."""

  def __init__(self, data=None):
    self._request = self
    if data is None:
      self.data = {}
    else:
      self.data = data
