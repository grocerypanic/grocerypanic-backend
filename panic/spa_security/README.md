# Single Page Application Security App

This Django app provides some helpful content for protecting a DRF backed with a SPA frontend implementation.

## Pre-requisites

This was tested with the following libraries and versions:

```requirements.txt
django>=3.0.4,<3.1.0
djangorestframework>=3.11.0,<3.12.0
djangorestframework_simplejwt>=4.6.0,<4.7.0
django-bleach>=0.6.1,<0.7.0
dj-rest-auth>=1.0.0,<1.1.0
```

This can surely work with a broader range of versions, YMMV.  Test!

## Features:

1. **Bleached Char Fields for Models:**
    - protects char fields from javascript injection, has standard char field properties and validators
    - `spa_security.fields.BlondeCharField`
    - provides the `BLEACH_RESTORE_LIST` Django setting, as a dictionary of key, value pairs that allow restoring specific bleached values (for example, ampersand)
2. **CSRF Cookie Protection View Mixin:**
    - add this mixin to the leftmost baseclass of your view to ensure it performs CSRF validation
    - `spa_security.mixins.csrf.CSRFMixin`
3. **CSRF Token Generation View:**
    - presents an authenticated view which returns a CSRF token as a JSON response
    - `spa_security.views.csrf_token.CSRFTokenView`

## Configuration / Example Usage

You must add 'spa_security' to your INSTALLED_APPS:
```python
INSTALLED_APPS = [
    "...",
    "spa_security",
    "...",
]
```

### 1. Bleached Char Fields

```python
from django.db import models

from spa_security.fields import BlondeCharField

class ItemList(models.Model):
  name = BlondeCharField(max_length=255, unique=True)

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)
```

### 2. View CSRF Cookie Protection

In your settings file add:
```python
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = True
CSRF_TRUSTED_ORIGINS = ['localhost']
CSRF_FAILURE_VIEW = "spa_security.views.csrf_error.csrf_error_view"
```

Then construct your views like this:
```python
from rest_framework import mixins, viewsets

from spa_security.mixins.csrf import CSRFMixin
from kitchen.models.item import Item
from kitchen.serializers.item import ItemSerializer

class ListItemsViewSet(
    CSRFMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  serializer_class = ItemSerializer
  queryset = Item.objects.all()

  def get_queryset(self):
    return self.queryset.order_by("-name")
```

On a CSRF validation error, the csrf_error view will return a JSON message telling you such, with a 403 error.

### 3. CSRF Token Generation View

Add this to your root urls file:
```python
from django.urls import include, path

urlpatterns = [
    "...",
    path("api/v1/auth/", include("spa_security.urls")),
    "...",
]
```

Authenticated requests to this endpoint will also be sent a cookie containing the CSRF value.
Ensure you are configuring the cookie [name](https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-CSRF_COOKIE_NAME) to what you really want.

You can use the cookie value, or JSON response, to create a `X-CSRFToken` header in your client's REST requests, so that CSRF validation is performed.  On a CSRF error, your client can simply request a new token and retry the request.
For more information please read [this documentation](https://docs.djangoproject.com/en/3.0/ref/csrf/#ajax).
