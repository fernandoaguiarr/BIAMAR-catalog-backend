from rest_framework import routers

from .views import GroupViewSet, ItemViewSet, SkuViewSet, BrandViewSet, CategoryViewSet, SeasonViewSet

app_name = 'item'
router = routers.SimpleRouter()
router.register(r'groups', GroupViewSet, 'groups')
router.register(r'items', ItemViewSet, 'items')
router.register(r'skus', SkuViewSet, 'skus')
router.register(r'brands', BrandViewSet, 'brands')
router.register(r'categories', CategoryViewSet, 'categories')
router.register(r'seasons', SeasonViewSet, 'seasons')
router.register(r'banners', BannerViewSet, 'banners')
urlpatterns = router.urls
