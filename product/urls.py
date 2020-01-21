from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('photos/', views.photo_list),
    path('<int:id>', views.item_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)
