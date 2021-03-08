"""Test the root exception handler."""

from unittest.mock import patch

from ...tests.fixtures.fixtures_exception_handler import HandlerTestHarness
from .. import ValidationPermissionError
from .. import root_exception_handler as handler_module
from ..root_exception_handler import root_exception_handler

HANDLER_MODULE = handler_module.__name__


@patch(f'{HANDLER_MODULE}.views.exception_handler')
class TestRootExceptionHandler(HandlerTestHarness):
  """Test the root_exception_handler function."""

  def test_regular_exception(self, mock_handler):
    mock_handler.return_value = self.response
    response = root_exception_handler(self.base_exception, {})

    self.assertEqual(response.status_code, self.response.status_code)

  def test_regular_exception_none(self, mock_handler):
    mock_handler.return_value = None
    response = root_exception_handler(self.base_exception, {})

    self.assertIsNone(response)

  def test_custom_validation_exception(self, mock_handler):
    custom_exception = ValidationPermissionError(detail=self.field_error,)

    mock_handler.return_value = self.response
    response = root_exception_handler(custom_exception, {})

    self.assertEqual(
        response.status_code, ValidationPermissionError.status_code
    )
