from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from .models import Simulation
from .serializers import SimulationSerializer
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

    @detail_route(methods=['get'])
    def run(self, request, pk=None):
        simulation = Simulation.objects.get(pk=pk)
        SimulationManager.run_simulation(simulation)
        return Response('started!')