from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include
handler404 = 'highrise_admin.views.error_404_view'

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('app/', include('highrise_app.urls')),
    path('', include('highrise_admin.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)