"""Admin models for the user app."""

from django.contrib import admin

from ..models.user import User
from .user_modeladmin import UserModelAdmin

admin.site.register(User, UserModelAdmin)
