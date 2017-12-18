from django.urls import path
from .views import SimulationViewSet, TrialViewSet

urlpatterns = [
    path('simulations', SimulationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('simulations/<int:simId>', SimulationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('simulations/<int:simId>/run', SimulationViewSet.as_view({
        'get': 'run'
    })),
    path('simulations/<int:simId>/trials', TrialViewSet.as_view({
        'get': 'list',
    })),
    path('simulations/<int:simId>/trials/<int:trialId>', TrialViewSet.as_view({
        'get': 'retrieve'
    }))
]