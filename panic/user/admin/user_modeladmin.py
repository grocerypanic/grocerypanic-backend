"""ModelAdmin for the User model."""

from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


class UserModelAdmin(UserAdmin):
  """ModelAdmin for the User model."""

  list_display = [
      "email",
      "username",
      "timezone",
      "language_code",
      "is_staff",
  ]
  fieldsets = (
      (
          None,
          {
              'fields': (
                  'username',
                  'password',
              )
          }
      ),
      (
          _('Personal info'),
          {
              'fields': (
                  'first_name',
                  'last_name',
                  'email',
                  'timezone',
                  'language_code',
              ),
          },
      ),
      (
          _('Permissions'),
          {
              'fields': (
                  'is_active',
                  'is_staff',
                  'is_superuser',
                  'groups',
                  'user_permissions',
              ),
          },
      ),
      (
          _('Important dates'),
          {
              'fields': (
                  'last_login',
                  'date_joined',
              ),
          },
      ),
  )
  add_fieldsets = ((
      None,
      {
          'classes': ('wide',),
          'fields': (
              'username',
              'email',
              'password1',
              'password2',
              'timezone',
              'language_code',
          )
      },
  ),)
