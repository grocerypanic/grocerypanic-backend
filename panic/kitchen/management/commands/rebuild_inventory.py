"""A management command to rebuild the inventory table."""

from django.core.management.base import BaseCommand

from ...models.transaction import Transaction
from utilities.management.shared.confirmation import ManagementConfirmation

MESSAGE_REBUILDING = "Rebuilding for Inventory Table..."
MESSAGE_SUCCESS = "Inventory table has been rebuilt!"


class Command(BaseCommand):
  """Management command that rebuilds the inventory table."""

  help = 'Rebuilds the inventory table from transactions, wiping it first.'

  def handle(self, *args, **options):
    """Command implementation."""

    confirm = Confirmation()

    if not confirm.are_you_sure():
      return

    self.stdout.write(MESSAGE_REBUILDING)
    Transaction.objects.rebuild_inventory_table(confirm=True)

    self.stdout.write(self.style.SUCCESS(MESSAGE_SUCCESS))


class Confirmation(ManagementConfirmation):
  """Confirmation dialogue."""

  confirm_message = (
      "This command will erase and rebuild the entire Inventory table from "
      "Transaction data.\n"
      "As such, it should only be attempted during a "
      "scheduled maintenance window.\n"
      "Are you absolutely sure you wish to proceed [Y/n] ? "
  )
  confirm_yes = "Y"
