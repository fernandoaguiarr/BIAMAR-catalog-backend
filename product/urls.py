from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from .views import PhotoViewSet, ItemViewSet, FilterViewSet

router = DefaultRouter()
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'products', ItemViewSet, basename='product')
router.register(r'filters', FilterViewSet, basename='filter')
urlpatterns = router.urls
# urlpatterns = format_suffix_patterns(urlpatterns)
