# Django
from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Biamar Malhas Administration"
admin.site.index_title = "Item Manager"
admin.site.site_url = None
admin.site.site_title = "Biamar Malhas"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
