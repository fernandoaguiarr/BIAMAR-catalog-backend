# third-party
from rest_framework import routers
from rest_framework.authtoken import views

# Django
from django.urls import path

# local Django
from api.views import (
    ItemViewSet, GroupViewSet, PhotoViewSet, SkuViewSet, ItemTypeViewSet, BrandViewSet, SeasonViewSet
)

router = routers.DefaultRouter()
router.register(r'skus', SkuViewSet, basename="sku-viewset")
router.register(r'items', ItemViewSet, basename="item-viewset")
router.register(r'groups', GroupViewSet, basename="group-viewset")
router.register(r'photos', PhotoViewSet, basename="photo-viewset")
router.register(r'brands', BrandViewSet, basename="brand-viewset")
router.register(r'seasons', SeasonViewSet, basename="season-viewset")
router.register(r'item-types', ItemTypeViewSet, basename="item-type-viewset")

urlpatterns = [
    path('authentication/', views.obtain_auth_token),
]

urlpatterns += router.urls