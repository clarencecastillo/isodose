import os, sys
from multiprocessing import Process

import dose
import events

from django.db.models import Manager
from django.utils import timezone
from channels import Group

from . import models


def simulation_worker(parameters, eb):

    class SimulationFunctions(dose.dose_functions):

        def organism_movement(self, populations, pop_name, world):
            pass

        def organism_location(self, populations, pop_name, world):
            pass

        def ecoregulate(self, world):
            pass

        def update_ecology(self, world, x, y, z):
            pass

        def update_local(self, world, x, y, z):
            pass

        def report(self, world):
            pass

        def fitness(self, populations, pop_name):
            pass

        def mutation_scheme(self, organism):
            organism.genome[0].rmutate(parameters["mutation_type"],
                                       parameters["additional_mutation"])

        def prepopulation_control(self, populations, pop_name):
            pass

        def mating(self, populations, pop_name):
            pass

        def postpopulation_control(self, populations, pop_name):
            pass

        def generation_events(self, populations, pop_name):
            pass

        def population_report(self, populations, pop_name):
            sequences = [''.join(org.genome[0].sequence) for org in populations[pop_name].agents]
            identities = [org.status['identity'] for org in populations[pop_name].agents]
            locations = [str(org.status['location']) for org in populations[pop_name].agents]
            demes = [org.status['deme'] for org in populations[pop_name].agents]
            return '\n'.join(sequences)

        def database_report(self, con, cur, start_time,
                            populations, world, generation_count):
            try:
                dose.database_report_populations(con, cur, start_time,
                                                 populations, generation_count)
            except:
                pass
            try:
                dose.database_report_world(con, cur, start_time,
                                           world, generation_count)
            except:
                pass

        def deployment_scheme(self, populations, pop_name, world):
            pass

    if not os.path.exists('logs'):
        os.makedirs('logs')
    sys.stdout = open("logs/" + str(os.getpid()) + ".log", "w")

    dose.simulate(parameters, SimulationFunctions, eb)


def on_simulation_start(data, trial):
    trial.status = models.Trial.RUNNING
    trial.directory = data['directory']
    trial.max_generation = data['max_generation']
    trial.current_generation = data['generation']
    trial.start_time = timezone.make_aware(data['time_start'], timezone.get_current_timezone())
    trial.save(update_fields=['status', 'directory', 'max_generation', 'current_generation', 'start_time'])


def on_generation_world_update(data, trial):
    pass


def on_generation_populations_update(data, trial):
    trial.current_generation = data['generation']
    trial.save(update_fields=['current_generation'])
    Group(str(trial.id)).send({
        "text": "Current generation: " + str(trial.current_generation)
    }, immediately=True)


def on_simulation_end(data, trial):
    trial.status = models.Trial.DONE
    trial.end_time = timezone.make_aware(data['time_end'], timezone.get_current_timezone())
    trial.save(update_fields=['status', 'end_time'])


class SimulationManager(Manager):


    def create(self, **kwargs):

        populations_data = kwargs.pop('populations')
        ragaraja_instructions_data = None
        if ('ragaraja_instructions' in kwargs):
            ragaraja_instructions_data = kwargs.pop('ragaraja_instructions')

        simulation = models.Simulation(**kwargs)
        simulation.save()

        for pop_data in populations_data:
            population = models.Population(
                simulation=simulation,
                name=pop_data['name']
            )
            population.save()

            for loc in pop_data['locations']:
                location = models.Location(
                    population = population,
                    x = loc['x'],
                    y = loc['y'],
                    z = loc['z']
                )
                location.save()

        if ragaraja_instructions_data is not None:

            for ri_data in ragaraja_instructions_data:
                ragaraja_instruction = models.RagarajaInstruction(
                    simulation = simulation,
                    instruction = ri_data['instruction']
                )
                ragaraja_instruction.save()

        return simulation

    def update(self, instance, **kwargs):

        populations_data = kwargs.pop('populations')
        ragaraja_instructions_data = None
        if ('ragaraja_instructions' in kwargs):
            ragaraja_instructions_data = kwargs.pop('ragaraja_instructions')

        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save(update_fields=list(kwargs))

        for population in instance.populations.all():
            population.locations.all().delete()
            population.delete(keep_parents=True)

        for pop_data in populations_data:
            population = models.Population(
                simulation = instance,
                name = pop_data['name']
            )
            population.save()

            for loc in pop_data['locations']:
                location = models.Location(
                    population = population,
                    x = loc['x'],
                    y = loc['y'],
                    z = loc['z']
                )
                location.save()

        if ragaraja_instructions_data is not None:

            for ri_data in ragaraja_instructions_data:
                ragaraja_instruction = models.RagarajaInstruction(
                    simulation = instance,
                    instruction = ri_data['instruction']
                )
                ragaraja_instruction.save()

        return instance

    @staticmethod
    def run_simulation(sim, trial):

        eb = dose.event_broker()
        eb.subscribe(events.SIMULATION_START,
                     lambda data: on_simulation_start(data, trial))
        eb.subscribe(events.SIMULATION_END,
                     lambda data: on_simulation_end(data, trial))
        eb.subscribe(events.GENERATION_POPULATIONS_UPDATE,
                     lambda data: on_generation_populations_update(data, trial))
        eb.subscribe(events.GENERATION_WORLD_UPDATE,
                     lambda data: on_generation_world_update(data, trial))

        parameters = {
            "simulation_name": sim.name,
            "population_names": [pop.name for pop in sim.populations.all()],
            "population_locations": [[(loc.x, loc.y, loc.z) for loc in pop.locations.all()] for pop in
                                     sim.populations.all()],
            "deployment_code": sim.deployment_code,
            "chromosome_bases": list(sim.chromosome_bases),
            "background_mutation": sim.background_mutation,
            "additional_mutation": sim.additional_mutation,
            "mutation_type": sim.mutation_type,
            "chromosome_size": sim.chromosome_size,
            "genome_size": sim.genome_size,
            "max_tape_length": sim.max_tape_length,
            "clean_cell": sim.clean_cell,
            "interpret_chromosome": sim.interpret_chromosome,
            "max_codon": sim.max_codon,
            "population_size": sim.population_size,
            "eco_cell_capacity": sim.eco_cell_capacity,
            "world_x": sim.world_x,
            "world_y": sim.world_y,
            "world_z": sim.world_z,
            "goal": sim.goal,
            "maximum_generations": sim.maximum_generations,
            "fossilized_ratio": sim.fossilized_ratio,
            "fossilized_frequency": sim.fossilized_frequency,
            "print_frequency": sim.print_frequency,
            "ragaraja_version": sim.ragaraja_version,
            "ragaraja_instructions": [ri.instruction for ri in sim.ragaraja_instructions.all()],
            "eco_buried_frequency": sim.eco_buried_frequency,
            "database_file": sim.database_file,
            "database_logging_frequency": sim.database_logging_frequency
        }

        if sim.initial_chromosome is not None:
            parameters['initial_chromosome'] = list(sim.initial_chromosome)

        simulation = Process(target=simulation_worker, args=(parameters, eb,))
        simulation.start()