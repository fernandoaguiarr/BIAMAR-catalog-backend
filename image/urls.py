from django.urls import path
from rest_framework import routers

from . import views
from .views import PhotoViewSet

app_name = 'image'
router = routers.SimpleRouter()
router.register(r'images', PhotoViewSet, 'images')
urlpatterns = router.urls
