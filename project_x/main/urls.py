from django.contrib import admin
from django.urls import path, include
from .yasg import urlpatterns as doc_urls
from django.conf import settings
from django.conf.urls.static import static


api_patterns = [
    path('', include('project.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += doc_urls
