"""ModelAdmin form for the Item model."""

from django import forms

from ..models.item import Item


class ItemAdminForm(forms.ModelForm):
  """ModelAdmin form for the Item model."""

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
