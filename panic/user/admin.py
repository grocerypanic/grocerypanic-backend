"""Custom user admin integration."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models.user import User


class UserAdmin(DjangoUserAdmin):
  """Custom user admin integration."""

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


admin.site.register(User, UserAdmin)
