from rest_framework.routers import DefaultRouter

from .views import PhotoViewSet, ItemViewSet, FilterViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='items')
router.register(r'photos', PhotoViewSet, basename='photos')
router.register(r'filters', FilterViewSet, basename='filters')

urlpatterns = router.urls
