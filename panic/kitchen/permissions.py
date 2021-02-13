"""Kitchen custom rest_framework permissions."""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
  """Ensure the user making the request is authorized to access the object."""

  def has_object_permission(self, request, view, obj):
    """Match the 'user' property of `obj`, against the `request` user."""

    if hasattr(obj, "user"):
      return obj.user == request.user
    return True
