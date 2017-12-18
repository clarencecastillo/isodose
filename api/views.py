from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from .models import Simulation, Trial
from .serializers import SimulationSerializer, TrialListSerializer, TrialSerializer
from .managers import SimulationManager

class SimulationViewSet(ModelViewSet):
    """
    retrieve:
    Returns the given simulation.

    list:
    Return a list of all the existing simulations.

    create:
    Create a new simulation.

    update:
    Updates the existing given simulation.

    run:
    Runs the given simulation.
    """

    serializer_class = SimulationSerializer
    queryset = Simulation.objects.all()
    lookup_url_kwarg = 'simId'

    # def retrieve(self, request, *args, **kwargs):
    #     return super().retrieve(request, pk=kwargs['simId'])
    #
    # def update(self, request, *args, **kwargs):
    #     return super().update(request, pk=kwargs['simId'])

    @detail_route(methods=['get'])
    def run(self, request, *args, **kwargs):
        simulation = Simulation.objects.get(pk=kwargs['simId'])
        SimulationManager.run_simulation(simulation)
        return Response('started!')

class TrialViewSet(ModelViewSet):
    """
    retrieve:
    Returns the given trial.

    list:
    Return a list of all the simulation's trials.
    """

    queryset = Trial.objects.all()
    lookup_url_kwarg = 'trialId'

    def get_serializer_class(self):
        if self.action == 'list':
            return TrialListSerializer
        return TrialSerializer
