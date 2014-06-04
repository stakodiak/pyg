#!/usr/bin/python2.7
"""
Simple genetic algorithm implementation.
"""
import random


class Chromosome(object):
    """`pyg` works with these objects."""
    def __init__(self, genotype=None):
        if genotype:
            assert type(genotype) is list
            self.genotype = genotype
        else:
            self.genotype = self.generate()
        self.score = 0

    @staticmethod
    def generate():
        raise NotImplementedError

    @staticmethod
    def fitness(member):
        raise NotImplementedError

    def recombine(self, other):
        chromosome = type(self)
        genotype = []
        for i in range(len(self.genotype)):
            choice = random.choice([self, other])
            genotype.append(choice.genotype[i])
        child = chromosome(genotype=genotype)
        return child

    def mutate(self):
        """Returns copy of mutated genotype.

        Genotypes are always lists, but the type of each element
        is arbitrary. Default is to create a new instance and
        replace a random paramater with a value from the new
        genome.
        """
        replacement = self.generate()
        choice = random.randrange(len(self.genotype))
        self.genotype[choice] = replacement[choice]
        return self

class pyg(object):
    POP_SIZE = 1000
    MUTATION_RATE = 0.05
    COPY_RATE = 0.10

    def __init__(self, chromosome):
        """Creates genetic algorithm handler.

        Args -
            chromosome: A reference to a `Chromosome`
            implementation.
        """
        self.chromosome = chromosome
        self.population = [self.chromosome() for _ in range(self.POP_SIZE)]
        self.iterations = 0

    def iterate(self):
        self.simulate()
        self.selection()
        self.crossover()
        self.iterations += 1

    def simulate(self):
        for member in self.population:
            score = self.chromosome.fitness(member.genotype)
            member.score = float(score)

    def selection(self):
        total_fitness = sum(ch.score for ch in self.population)
        population = []

        while len(population) < self.POP_SIZE:
            cumulative = 0.0
            threshold = random.random()
            # Pick new chromosomes with probabilities
            # proportional to total fitness.
            for member in self.population:
                cumulative += member.score / total_fitness
                if cumulative > threshold:  # like roulette
                    population.append(member)
                    break

            # Also sample offspring universally to counter biases
            # for members with a large fitness.
            intervals = [-0.4, -0.2, +0.2, +0.4]
            pointers = [x % 1.0 for x in [threshold + i for i in intervals]]
            for pointer in pointers:
                cumulative = 0.0
                for member in self.population:
                    cumulative += member.score / total_fitness
                    if cumulative > pointer:
                        population.append(member)
                        break

        # Trim extras from population.
        for i in range(len(population) - self.POP_SIZE):
            population.pop()
        self.population = population

    def crossover(self):
        offspring = []
        while len(offspring) < self.POP_SIZE:
            # Pick two parents.
            first = random.choice(self.population)
            second = random.choice(self.population)
            # Try to copy chromosome.
            if random.random() < self.COPY_RATE:
                child = first
            else:
                child = first.recombine(second)
            # Try to mutate genome.
            if random.random() < self.MUTATION_RATE:
                child = child.mutate()
            offspring.append(child)
        self.population = offspring

    @property
    def top(self):
        return max(self.population, key=lambda ch: ch.score)
