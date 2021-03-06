"""Management command confirmation dialogues."""

import sys


class ManagementConfirmation:
  """Confirmation dialogues for django management commands."""

  confirm_message: str
  confirm_yes: str

  def are_you_sure(self):
    """Provide a simple confirmation prompt.

    :returns: A boolean indicating if the confirmation was accepted or denied.
    :rtype: bool
    """

    sys.stdout.write(self.confirm_message)
    response = input()
    if response is self.confirm_yes:
      return True
    return False
