"""A django admin command to rebuild/reset item quantities from inventory."""

from django.core.management.base import BaseCommand

from ...models.item import Item
from .utils.confirmation import AdminConfirmation

MESSAGE_REBUILDING = "Rebuilding Item quantities from Inventory Table..."
MESSAGE_SUCCESS = "Item quantities have been rebuilt!"


class Confirmation(AdminConfirmation):
  """Confirmation dialogue."""

  confirm_message = (
      "This command will rewrite all Item quantities with values calculated "
      "from the Inventory table.\n"
      "As such, it should only be attempted during a "
      "scheduled maintenance window.\n"
      "Are you absolutely sure you wish to proceed [Y/n] ? "
  )
  confirm_yes = "Y"


class Command(BaseCommand):
  """Django command that rewrites all item quantity values from inventory."""

  help = 'Rewrite all item quantities based on values from the inventory table.'

  def handle(self, *args, **options):
    """Command implementation."""

    confirm = Confirmation()

    if not confirm.are_you_sure():
      return

    self.stdout.write(MESSAGE_REBUILDING)
    Item.objects.rebuild_quantities_from_inventory(confirm=True)

    self.stdout.write(self.style.SUCCESS(MESSAGE_SUCCESS))
