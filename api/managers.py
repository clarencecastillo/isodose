import os
import sys
from multiprocessing import Process
import dose

from django.db.models import Manager

from . import models

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
                simulation = simulation,
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
    def __simulation_woker__(parameters):

        class simulation_functions(dose.dose_functions):

            def organism_movement(self, Populations, pop_name, World):
                pass

            def organism_location(self, Populations, pop_name, World):
                pass

            def ecoregulate(self, World):
                pass

            def update_ecology(self, World, x, y, z):
                pass

            def update_local(self, World, x, y, z):
                pass

            def report(self, World):
                pass

            def fitness(self, Populations, pop_name):
                pass

            def mutation_scheme(self, organism):
                organism.genome[0].rmutate(parameters["mutation_type"],
                                           parameters["additional_mutation"])

            def prepopulation_control(self, Populations, pop_name):
                pass

            def mating(self, Populations, pop_name):
                pass

            def postpopulation_control(self, Populations, pop_name):
                pass

            def generation_events(self, Populations, pop_name):
                pass

            def population_report(self, Populations, pop_name):
                sequences = [''.join(org.genome[0].sequence) for org in Populations[pop_name].agents]
                identities = [org.status['identity'] for org in Populations[pop_name].agents]
                locations = [str(org.status['location']) for org in Populations[pop_name].agents]
                demes = [org.status['deme'] for org in Populations[pop_name].agents]
                return '\n'.join(sequences)

            def database_report(self, con, cur, start_time,
                                Populations, World, generation_count):
                try:
                    dose.database_report_populations(con, cur, start_time,
                                                     Populations, generation_count)
                except:
                    pass
                try:
                    dose.database_report_world(con, cur, start_time,
                                               World, generation_count)
                except:
                    pass

            def deployment_scheme(self, Populations, pop_name, World):
                pass

        if not os.path.exists('logs'): os.makedirs('logs')
        sys.stdout = open("logs/" + str(os.getpid()) + ".log", "w")
        dose.simulate(parameters, simulation_functions)
        return

    @staticmethod
    def parse_simulation(sim):

        return {
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

    @staticmethod
    def run_simulation(simulation):
        parameters = SimulationManager.parse_simulation(simulation)
        simulation = Process(target=SimulationManager.__simulation_woker__, args=(parameters,))
        simulation.start()