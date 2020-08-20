from rest_framework.routers import DefaultRouter

from core.views import VirtualAgeTokenViewSet

router = DefaultRouter()
router.register(r'virtual-age', VirtualAgeTokenViewSet, basename='token_virtual_age')
urlpatterns = router.urls
