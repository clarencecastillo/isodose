from django.urls import path
from .views import SimulationViewSet, TrialViewSet

urlpatterns = [
    path('simulations', SimulationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('simulations/<uuid:simId>', SimulationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update'
    })),
    path('simulations/<uuid:simId>/run', SimulationViewSet.as_view({
        'get': 'run'
    })),
    path('simulations/<uuid:simId>/trials', TrialViewSet.as_view({
        'get': 'list',
    })),
    path('simulations/<uuid:simId>/trials/<uuid:trialId>', TrialViewSet.as_view({
        'get': 'retrieve'
    }))
]