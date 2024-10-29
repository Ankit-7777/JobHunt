from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from rest_framework.routers import DefaultRouter
from JobPortal.views import (
    UserAuthAPIView,
    JobViewSet,
    ApplicationViewSet

)
router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'applications', ApplicationViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', UserAuthAPIView.as_view(), name='user-auth'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



