"""Django Related Fixtures"""


class MockRequest:

  def __init__(self, data=None):
    self._request = self
    if data is None:
      self.data = {}
    else:
      self.data = data
