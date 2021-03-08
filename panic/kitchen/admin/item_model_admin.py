"""ModelAdmin for the Item model."""

from django.contrib import admin

from .item_model_admin_form import ItemAdminForm


class ItemAdmin(admin.ModelAdmin):
  """ModelAdmin for the Item model."""

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
    """Retrieve `expired` value, regardless of instance state."""
    return 0 if not instance.id else instance.expired

  def next_expiry_datetime(self, instance):
    """Retrieve `next_expiry_datetime` value."""
    return instance.next_expiry_datetime

  def next_expiry_quantity(self, instance):
    """Retrieve `next_expiry_quantity` value, regardless of instance state."""
    return 0 if not instance.id else instance.next_expiry_quantity
