"""ModelAdmin Form for the Item model."""

from django import forms

from ..models.item import Item
from ..models.validators.m2m import ManyToManyValidator


class ItemAdminForm(forms.ModelForm):
  """ModelAdmin Form for the Item model."""

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
