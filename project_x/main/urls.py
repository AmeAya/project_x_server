from django.contrib import admin
from django.urls import path, include
from .yasg import urlpatterns as doc_urls


api_patterns = [
    path('', include('project.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]

urlpatterns += doc_urls