"""Kitchen V1 urls."""

from django.urls import include, path
from rest_framework import routers

from ..views import item, shelf, store, suggested, transaction

v1_router = routers.SimpleRouter()
v1_router.register(
    "items",
    item.ItemViewSet,
    basename="items",
)
v1_router.register(
    "items",
    item.ItemListCreateViewSet,
    basename="items-supplementary",
)
v1_router.register(
    "shelves",
    shelf.ShelfViewSet,
    basename="shelves",
)
v1_router.register(
    "shelves",
    shelf.ShelfListCreateViewSet,
    basename="shelves-supplementary",
)
v1_router.register(
    "stores",
    store.StoreViewSet,
    basename="stores",
)
v1_router.register(
    "stores",
    store.StoreListCreateViewSet,
    basename="stores-supplementary",
)
v1_router.register(
    "suggestions",
    suggested.SuggestedItemListViewSet,
    basename="suggestions",
)
v1_router.register(
    "transactions",
    transaction.TransactionViewSet,
    basename="transactions",
)

app_name = "kitchen"
urlpatterns = [
    path("v1/", include(v1_router.urls)),
]
