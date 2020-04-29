from rest_framework.routers import DefaultRouter

from .views import PhotoViewSet, ItemViewSet

router = DefaultRouter()
router.register(r'item', ItemViewSet, basename='item')
router.register(r'photos', PhotoViewSet, basename='photos')

urlpatterns = router.urls
