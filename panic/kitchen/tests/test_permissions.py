"""Test Custom Permissions"""

from django.test import TestCase

from ..permissions import IsOwner


class IsOwnerTest(TestCase):
  """Test the isOwner"""

  def setUp(self) -> None:

    class MockRequest:

      def __init__(self, user):
        self.user = user

    class MockObject:
      pass

    self.user = "username"

    self.request_with_user = MockRequest(self.user)
    self.request_without_user = MockRequest(None)
    self.permission = IsOwner()

    self.object_correct_user = MockObject()
    self.object_correct_user.user = self.user

    self.object_wrong_user = MockObject()
    self.object_wrong_user.user = "another_user"

    self.object_no_user = MockObject()

  def test_permission_succeeds(self):

    result = self.permission.has_object_permission(
        self.request_with_user, None, self.object_correct_user
    )

    self.assertTrue(result)

  def test_permission_fails(self):

    result = self.permission.has_object_permission(
        self.request_with_user, None, self.object_wrong_user
    )

    self.assertFalse(result)

  def test_permission_succeeds_no_owner(self):

    result = self.permission.has_object_permission(
        self.request_with_user, None, self.object_no_user
    )

    self.assertTrue(result)

  def test_permission_fails_no_owner(self):

    result = self.permission.has_object_permission(
        self.request_without_user, None, self.object_correct_user
    )

    self.assertFalse(result)
