"""Custom RestFramework Permissions"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
  """Allow only owners of an object to access it.

  Assumes any object with a user field should match the logged in user.
  """

  def has_object_permission(self, request, view, obj):
    if hasattr(obj, "user"):
      return obj.user == request.user
    return True
