"""ModelAdmin formset for the PreferredStore model."""

from django import forms

WRONG_USER_ERROR_MESSAGE = "This Store does not belong to the Item's Manager."
DUPLICATE_ERROR_MESSAGE = "This Store has already been added."


class PreferredStoreAdminFormSet(forms.BaseInlineFormSet):
  """ModelAdmin formset for the Item model."""

  def clean(self):
    """Validate data before saving model."""
    super().clean()
    preferred_stores = set()

    for form in self.forms:
      item = form.cleaned_data.get('item')
      store = form.cleaned_data.get('store')
      delete = form.cleaned_data.get('DELETE', False)
      if not delete and store is not None:
        self._validate_related_user(form, item, store)
        self._validate_duplicates(form, preferred_stores, store)

  @staticmethod
  def _validate_duplicates(form, preferred_stores, store):
    if store not in preferred_stores:
      preferred_stores.add(store)
      return

    form.add_error(
        "store",
        DUPLICATE_ERROR_MESSAGE,
    )

  @staticmethod
  def _validate_related_user(form, model1, model2):
    model1_user = getattr(model1, 'user', None)
    model2_user = getattr(model2, 'user', None)

    if model1_user != model2_user:
      form.add_error(
          "store",
          WRONG_USER_ERROR_MESSAGE,
      )
