from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r'person', views.PersonViewSet, basename='person')
router.register(r'filter-person', views.FilterPersonViewSet, basename='filter-person')

urlpatterns = [
    path('', include(router.urls))
]