"""Admin customizations for the Item model."""

from django import forms
from django.contrib import admin

from ..models.item import Item
from ..models.validators.m2m import ManyToManyValidator


class ItemAdminForm(forms.ModelForm):
  """Custom admin form for the Item model."""

  expired = forms.IntegerField(required=False)
  quantity = forms.IntegerField(required=False)
  next_expiry_datetime = forms.DateTimeField(required=False)
  next_expiry_quantity = forms.IntegerField(required=False)

  class Meta:
    model = Item
    fields = '__all__'

  def clean_user(self):
    """Set instance.user, so related field checks work."""
    self.instance.user = self.cleaned_data.get('user')
    return self.cleaned_data.get('user')

  def clean(self):
    """Validate data before saving model."""
    super().clean()
    self._validate_related_m2m()
    return self.cleaned_data

  def _validate_related_m2m(self):
    preferred_stores_value = self.cleaned_data.get('preferred_stores', ())

    m2m_validator = ManyToManyValidator(
        related_field='preferred_stores',
        match_field='user',
    )
    m2m_validator.validate(
        self.instance,
        {store.id for store in preferred_stores_value},
    )


class ItemAdmin(admin.ModelAdmin):
  """Custom model admin for the Item model."""

  form = ItemAdminForm
  fieldsets = (('Manager', {
      'fields': ('user',)
  }), (
      'Basic Information', {
          'fields': (
              'name',
              'shelf',
              'shelf_life',
              'has_partial_quantities',
          )
      }
  ), (
      'Status', {
          'fields': (
              'quantity',
              'expired',
              'next_expiry_quantity',
              'next_expiry_datetime',
          )
      }
  ), ('Shopping', {
      'fields': (
          'price',
          'preferred_stores',
      )
  }))
  readonly_fields = (
      'expired',
      'quantity',
      'next_expiry_datetime',
      'next_expiry_quantity',
  )

  def expired(self, instance):
    """Retrieve the expired value, regardless of instance state."""
    return 0 if not instance.id else instance.expired

  def next_expiry_datetime(self, instance):
    """Retrieve the next_expiry_datetime value."""
    return instance.next_expiry_datetime

  def next_expiry_quantity(self, instance):
    """Retrieve the next_expiry_quantity value, regardless of instance state."""
    return 0 if not instance.id else instance.next_expiry_quantity
