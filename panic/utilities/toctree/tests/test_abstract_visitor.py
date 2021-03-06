"""Test the abstract writer."""

from unittest import TestCase

from ...tests.fixtures.abc import concretor
from ..bases import AbstractVisitor


class AbstractVisitorTest(TestCase):
  """Test the AbstractVisitor class."""

  def setUp(self):
    self.visitor = concretor(AbstractVisitor)()

  def test_accept(self):
    self.visitor.accept(None)
