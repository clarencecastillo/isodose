from rest_framework import serializers
from .models import Simulation, Population, Location, RagarajaInstruction

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['x', 'y', 'z']

class RagarajaInstructionSerializer(serializers.ModelSerializer):

    class Meta:
        model = RagarajaInstruction
        fields = ['instruction']

class PopulationSerializer(serializers.ModelSerializer):

    locations = LocationSerializer(many=True, required=True)

    class Meta:
        model = Population
        fields = ['name', 'locations']

class SimulationSerializer(serializers.ModelSerializer):

    populations = PopulationSerializer(many=True, required=True)
    ragaraja_instructions = RagarajaInstructionSerializer(many=True, required=False)

    class Meta:
        model = Simulation
        fields = '__all__'

    def create(self, validated_data):
        simulation = Simulation.objects.create(**validated_data)
        return simulation

    def update(self, instance, validated_data):
        simulation = Simulation.objects.update(instance, **validated_data)
        return simulation