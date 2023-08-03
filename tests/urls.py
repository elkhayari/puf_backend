
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from tests import views

router = routers.DefaultRouter()
# router.register(r'devices', views.DeviceView, 'device')
router.register('tests', views.TestViewSet, basename="tests")

urlpatterns = [
    path('', include(router.urls)),
    path('measurmentsStatus/', views.getRunningTests),
    path('getEvaluationsTest/', views.EvaluationSet),
]
