"""Kitchen App Urls"""

from django.urls import include, path
from rest_framework import routers

from .views import item, shelf, store, suggested, transaction

app_name = "kitchen"

router = routers.SimpleRouter()

router.register("items", item.ItemViewSet, basename="items")
router.register("items", item.ItemListCreateViewSet, basename="items")

router.register("shelves", shelf.ShelfViewSet, basename="shelves")
router.register("shelves", shelf.ShelfListCreateViewSet, basename="shelves")

router.register("stores", store.StoreViewSet, basename="stores")
router.register("stores", store.StoreListCreateViewSet, basename="stores")

router.register(
    "suggestions",
    suggested.SuggestedItemListViewSet,
    basename="suggestions",
)

router.register(
    "transactions",
    transaction.TransactionViewSet,
    basename="transactions",
)
router.register(
    "transaction-consumption-history",
    transaction.TransactionConsumptionHistoryViewSet,
    basename="transaction-consumption-history",
)

urlpatterns = [
    path("", include(router.urls)),
]
