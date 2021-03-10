"""Inline ModelAdmin for the PreferredStore M2M model."""

from django.contrib import admin

from ..models.preferred_store import PreferredStore
from .preferred_store_modeladmin_form import PreferredStoreAdminFormSet


class PreferredStoreInline(admin.TabularInline):
  """TabularInline for the PreferredStore M2M model."""

  model = PreferredStore
  formset = PreferredStoreAdminFormSet
