from rest_framework.routers import DefaultRouter
#
from .views import PhotoViewSet, ItemViewSet, SeasonViewSet, TypeViewSet, BrandViewSet, TypePhotoViewSet, SkuViewSet, \
    GroupViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet, basename='items')
router.register(r'groups', GroupViewSet, basename='groups')
router.register(r'skus', SkuViewSet, basename='skus')
router.register(r'photos', PhotoViewSet, basename='photos')
router.register(r'type-photos', TypePhotoViewSet, basename='type_photos')
router.register(r'brands', BrandViewSet, basename='brands')
router.register(r'seasons', SeasonViewSet, basename='season')
router.register(r'types', TypeViewSet, basename='types')
urlpatterns = router.urls
