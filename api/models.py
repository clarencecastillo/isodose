from django.db import models
from django.core.exceptions import ValidationError
from django.core import validators

from .managers import SimulationManager
from ragaraja import ragaraja

class Simulation(models.Model):

    objects = SimulationManager()

    def validate_chromose(value):
        if len(set(value)) != len(value):
            raise ValidationError(
                _('%(value)s contains repeated characters'),
                params={'value': value},
        )

    # Mutation Types
    POINT = 'point'
    INSERT = 'insert'
    DELETE = 'delete'
    INVERT = 'invert'
    DUPLICATE= 'duplicate'
    TRANSLOCATE= 'translocate'
    MUTATION_TYPES = (
        (POINT, 'Point'),
        (INSERT, 'Insert'),
        (DELETE, 'Delete'),
        (INVERT, 'Invert'),
        (DUPLICATE, 'Duplicate'),
        (TRANSLOCATE, 'Translocate')
    )

    name = models.CharField(null=False, blank=False, max_length=240)
    notes = models.CharField(null=False, default="", max_length=960)
    date_created = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    deployment_code = models.IntegerField(null=False, blank=False, default=1,
                                          validators=[validators.MinValueValidator(0),
                                                      validators.MaxValueValidator(4)])
    chromosome_bases = models.CharField(null=False, blank=False, default="01", validators=[validate_chromose], max_length=240)
    background_mutation = models.DecimalField(null=False, blank=False, default=0.1, max_digits=5, decimal_places=3)
    additional_mutation = models.DecimalField(null=False, blank=False, default=0.0, max_digits=5, decimal_places=3)
    chromosome_size = models.IntegerField(null=False, blank=False, default=30)
    genome_size = models.IntegerField(null=False, blank=False, default=1)
    max_tape_length = models.IntegerField(null=False, blank=False, default=50)
    clean_cell = models.BooleanField(null=False, blank=False, default=True)
    interpret_chromosome = models.BooleanField(null=False, blank=False, default=True)
    max_codon = models.IntegerField(null=False, blank=False, default=2000)
    population_size = models.IntegerField(null=False, blank=False, default=100)
    eco_cell_capacity = models.IntegerField(null=False, blank=False, default=100)
    world_x = models.IntegerField(null=False, blank=False, default=5)
    world_y = models.IntegerField(null=False, blank=False, default=5)
    world_z = models.IntegerField(null=False, blank=False, default=5)
    goal = models.IntegerField(null=False, blank=False, default=0)
    maximum_generations = models.IntegerField(null=False, blank=False, default=100)
    fossilized_ratio = models.DecimalField(null=False, blank=False, default=0.01, max_digits=5, decimal_places=3)
    fossilized_frequency = models.IntegerField(null=False, blank=False, default=20)
    print_frequency = models.IntegerField(null=False, blank=False, default=10)
    ragaraja_version = models.IntegerField(null=False, blank=False, default=0)
    eco_buried_frequency = models.IntegerField(null=False, blank=False, default=100)
    database_file = models.CharField(null=False, blank=False, default="simulation.db",
                                     validators=[validators.FileExtensionValidator(['.db', '.sqlite', '.sqlite3'])], max_length=240)
    database_logging_frequency = models.IntegerField(null=False, blank=False, default=1)
    mutation_type = models.CharField(
        max_length=2,
        choices=MUTATION_TYPES,
        default=POINT
    )

class Population(models.Model):

    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='populations')
    name = models.CharField(max_length=240)

class RagarajaInstruction(models.Model):

    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, related_name='ragaraja_instructions')
    instruction = models.CharField(
        max_length=3,
        choices=[(inst, inst) for inst in list(ragaraja)]
    )

class Location(models.Model):

    population = models.ForeignKey(Population, on_delete=models.CASCADE, related_name='locations')
    x = models.IntegerField()
    y = models.IntegerField()
    z = models.IntegerField()

class Trial(models.Model):

    # Status
    IDLE = 'idle'
    RUNNING = 'running'
    DONE = 'done'
    STATUSES = (
        (IDLE, 'Idle'),
        (RUNNING, 'Running'),
        (DONE, 'Done')
    )

    simulation = models.ForeignKey(Simulation, on_delete=models.CASCADE, null=True, related_name='trials')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=1,
        choices=STATUSES,
        default=IDLE
    )