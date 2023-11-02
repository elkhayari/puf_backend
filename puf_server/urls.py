from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register('tests', views.TestViewSet, basename="tests")
router.register('testOp', views.TestViewOperationsSet, basename="testOp")
router.register('experiment', views.ExperimentsSet, basename="experiment")

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
    # path('getEvaluationsTest/', views.EvaluationSet),
    path('progress/', views.progress, name='progress'),
    # path('uploadMeasurments/', views.uploadMeasurments)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
