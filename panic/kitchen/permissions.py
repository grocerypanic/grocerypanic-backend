"""Kitchen custom rest_framework permissions."""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
  """Ensure the user making the request is authorized to access the object."""

  def has_object_permission(self, request, view, obj):
    """Determine if the current request user owns the object in questions.

    Compares the 'user' property of `obj`, (if it exists) and compare it to
    the current `request` user.

    :param request: A rest_framework request
    :type request: :class:`rest_framework.request.Request`
    :param request: A rest_framework view
    :type request: :class:`rest_framework.views.View`
    :param request: A rest_framework model object
    :type request: :class:`django.db.models.Model`

    :returns: A boolean indicating if the user has permission
    :rtype: bool
    """

    if hasattr(obj, "user"):
      return obj.user == request.user
    return True
