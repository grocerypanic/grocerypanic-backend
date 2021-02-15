"""Test the OpenApi documentation support tools."""

from django.test import TestCase

from ..swagger import openapi_ready


class TestOpenApiReady(TestCase):
  """Test openapi_ready function."""

  def setUp(self):

    class MockParent:

      def method(self):
        return "parent was called"

    class MockChild(MockParent):

      def __init__(self):
        self.swagger_fake_view = False

      @openapi_ready
      def method(self):
        return "child was called"

    self.parent = MockParent()
    self.child = MockChild()

  def tearDown(self):
    pass

  def test_with_swagger_fake_view_false(self):
    self.assertEqual(self.child.method(), "child was called")

  def test_with_swagger_fake_view_true(self):
    self.child.swagger_fake_view = True
    self.assertEqual(self.child.method(), "parent was called")
