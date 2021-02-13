"""A django admin command to create a default admin user."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
  """Bootstrap the django admin, by creating a user with a set of credentials.

  - Generate Admin Account::

    ./manage.py autoadmin

  - Credentials:
    Username: admin
    Password: admin
  """

  help = 'Adds a default admin user without user interaction.'

  def handle(self, *args, **options):
    """Command implementation."""
    query = User.objects.all().filter(username="admin").count()
    if query > 0:
      self.stdout.write(self.style.ERROR('The admin user already exists.'))

    else:
      user = User(username='admin')
      user.email = "test@example.com"
      user.set_password('admin')
      user.is_superuser = True
      user.is_staff = True
      user.save()

      self.stdout.write(self.style.SUCCESS('Successfully created admin user.'))
