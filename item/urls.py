from rest_framework.routers import DefaultRouter
#
from .views import PhotoViewSet, ItemViewSet, SeasonViewSet, TypeViewSet, BrandViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='items')
router.register(r'photos', PhotoViewSet, basename='photos')
router.register(r'type-photos', PhotoViewSet, basename='type-photos')
router.register(r'brands', BrandViewSet, basename='brands')
router.register(r'seasons', SeasonViewSet, basename='season')
router.register(r'types', TypeViewSet, basename='types')
urlpatterns = router.urls
