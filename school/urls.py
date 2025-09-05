from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib import admin
from django.urls import path, include
from .views import gerar_documentoadvertencia_pdf

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('school.urls')),
]
app_name = 'school'

urlpatterns = [
    path('advertencia/documento/<int:documentoadvertencia_id>/pdf/', gerar_documentoadvertencia_pdf, name='gerar_documentoadvertencia_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)