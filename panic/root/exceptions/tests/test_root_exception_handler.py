"""Test the root_exception_handler function."""

from unittest.mock import Mock, patch

from ... import exceptions as exceptions_module
from ...tests.fixtures.fixtures_exception_handler import HandlerTestHarness
from .. import root_exception_handler

EXCEPTIONS_MODULE = exceptions_module.__name__


@patch(f'{EXCEPTIONS_MODULE}.views.exception_handler')
@patch(f'{EXCEPTIONS_MODULE}.ValidationExceptionHandler')
class TestRootExceptionHandler(HandlerTestHarness):
  """Test the root_exception_handler function."""

  def setUp(self):
    super().setUp()
    self.mock_validation_instance = Mock()
    self.mock_validation_instance.response = self.response

  def test_regular_exception(self, m_validation_handler, m_handler):
    m_handler.return_value = self.response
    m_validation_handler.return_value = self.mock_validation_instance

    response = root_exception_handler(self.base_exception, {})

    self.assertEqual(response.status_code, self.response.status_code)
    m_validation_handler.assert_called_with(self.base_exception, response)
    self.mock_validation_instance.process.assert_called()

  def test_regular_exception_none(self, m_validation_handler, m_handler):
    m_handler.return_value = None

    response = root_exception_handler(self.base_exception, {})

    self.assertIsNone(response)
    m_validation_handler.assert_not_called()
