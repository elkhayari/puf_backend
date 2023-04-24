from django.urls import path, include

from . import views
from .views import TestViewSet, TestViewOperationsSet, ExperimentsSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tests', TestViewSet, basename="tests")
router.register('testOp', TestViewOperationsSet, basename="testOp")
router.register('experiment', ExperimentsSet, basename="experiment")

urlpatterns = [
    path('', include(router.urls)),

    path('', views.getRoutes, name="routes"),
    path('errorPage/', views.errorPage),
    path('getDevice/', views.getDevice),
    path('wrfram/', views.writeReadToMem),
    path('getStmState/', views.returnState),
    path('getImage/<str:file_name>', views.getImage),
    path('getHeatmap/', views.getHeatmap),
    path('getMetrics/', views.getMetrics),
    path('getEvaluationsTest/', views.EvaluationSet)


    #path('getStmTest/<int:id>', views.test),
    #path('tests/', views.getTests, name="tests"),
    #path('test/<int:pk>', views.testDetails)
    #path('test/<str:pk>/', views.getTest, name="test")

]
