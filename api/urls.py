from django.urls import path
from .views import SimulationViewSet

urlpatterns = [
    path('simulations', SimulationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('simulations/<pk>', SimulationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('simulations/<pk>/run', SimulationViewSet.as_view({
        'get': 'run'
    })),
]