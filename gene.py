# gene.py - Runs genetic simulation.
import random
import math
import Queue
import threading
import multiprocessing
import sys
import time
from simulate import simulate_model, get_time 

# GA parameters
POP_SIZE    = 100
COPY_RATE   = 0.10
MUTATE_RATE = 0.01

def main ():
    
    avg_fitness = list()
    g = Gene()
    num_iter = 10
    print "Expected:", (POP_SIZE * num_iter) * get_time()
    start = time.time() 
    for i in range (num_iter + 1):
        # Go to beginning of line.
        sys.stdout.write('\r')
        n = int (math.floor (i / (num_iter / 20.0)))
        sys.stdout.write("[%-20s] %d%% %f sec" % ('='*n, float(i)/num_iter*100, time.time() - start))
        sys.stdout.flush()
        if i < num_iter:
            g.iterate ()
    print ""
    print '\n'.join (map (str, g.history))

class Chromosome:
    def __init__ (self):
        # Parameters are: K_xy, K_xz, K_yz
        self.genotype = [random.randint (0, 15) for i in range (3)]
        self.num_param = len (self.genotype)
        self.fitness = 0
     
    def recombine (self, C):
        # Returns new set of parameters where each parameter has 50% of being
        # from a parent.
        child = list()
        for i in range (self.num_param):
            if random.random () > 0.50:
                child.append (self.genotype[i])
            else:
                child.append (C.genotype[i])
        chromosome = Chromosome()
        chromosome.fitness = 0
        chromosome.genotype = child
        return chromosome

    def set_fitness (self, fitness):
        self.fitness = fitness

    def mutate (self):
        # Mutates a random gene by log-normal scaling.
        gene = random.choice (range (self.num_param))
        self.genotype[gene] *= random.lognormvariate (0, 1)

class MP_Simulation(multiprocessing.Process):
    def __init__ (self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run (self):
        while True:
            c = self.task_queue.get()
            fitness = 0
            if c is None:
                break
            try:
                fitness = simulate_model (c.genotype)
            except:
                pass
            c.fitness = fitness
            self.result_queue.put (c)

            
class SimulationThread(threading.Thread):
    def __init__ (self, population, starti, endi):
        threading.Thread.__init__(self)
        self.population = population
        self.starti = starti
        self.endi = endi

    def run (self):
        starti = self.starti
        endi = self.endi
        num_iter = len (self.population) / 2
        for i in range (starti, endi):
            c = self.population [i]
            fitness = 0
            try:
                fitness = simulate_model (c.genotype)
            except:
                pass
            self.population [i].fitness = fitness


class Gene:
    def __init__ (self):
        self.population = [Chromosome() for i in range (POP_SIZE)]
        self.history = list()
    
    def iterate (self):
        # Set fitness for all chromosomes.
        self.simulate()
        # Select new chromosomes with SUS and FPS.
        self.selection()
        total = sum ([c.fitness  for c in self.population])
        self.history.append (total)
        # Recombine chromosomes.
        self.crossover()

    def crossover (self):
        population = list()
        while len (population) < POP_SIZE:
            # Pick two parents.
            x = random.choice (self.population)
            y = random.choice (self.population)
            # Try to copy chromosome.
            if random.random() < COPY_RATE:
                c = x
            # Otherwise, let them mate. 
            else:
                c = x.recombine (y)
            # Mutate child.
            if random.random() < MUTATE_RATE:
                c.mutate()
            # Add it to next generation.
            population.append (c)
        self.population = population

    def simulate (self):
        tasks = multiprocessing.Queue()
        results = multiprocessing.Queue()
        num_consumers = multiprocessing.cpu_count() * 2
        consumers = [ MP_Simulation (tasks, results)
                      for i in xrange (num_consumers) ]
        for w in consumers:
            w.start()

        num_chrom = POP_SIZE
        for i in xrange (num_chrom):
            tasks.put (self.population [i])
        for i in xrange (num_consumers):
            tasks.put (None)
        population = list()
        while num_chrom:
            C = results.get()
            population.append (C)
            num_chrom -= 1
        self.population = list(population)
            
    def simulate_thread (self):
        # Split simulation into two threads 
        half = int (POP_SIZE / 2)
        t1 = SimulationThread (self.population, 0, half)
        t2 = SimulationThread (self.population, half, POP_SIZE)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        # Merge the results.
        print [c.fitness for c in t1.population]
        self.population = list(t1.population)

    def threaded_simulate (self, thread):
        
        half = int (POP_SIZE / 2)
        start = 0 if thread == 1 else half
        end = start + half
        population = self.population [start:end]
        for c in population:
            c.fitness = simulate_model (c.genotype)
        self.population[start:end] = population

    def unthreaded_simulate (self):
        # Run population through simulation.
        for c in self.population:
            c.set_fitness (simulate_model (c.genotype))

        #for c in sorted(self.population, key= lambda c: c.fitness):
        #    print "{: <12} {}".format (c.genotype, c.fitness)
        print ""

        
    def selection (self):
        # Pick chromosomes with probability proportional to fitness.
        total_fitness = sum ([c.fitness for c in self.population])
        total_fitness = float (total_fitness)
        new_pop = list()
        while len (new_pop) < POP_SIZE:
            cum = 0.0
            r = random.random()
            for c in self.population:
                cum += c.fitness / total_fitness 
                if r < cum:
                    new_pop.append (c)
                    break
            # Use stochastic universal sampling
            pointers = [-0.4, -0.2, +0.2, +0.4]
            pointers = [x % 1.0 for x in [r + y for y in pointers]]
            for p in pointers:
                cum = 0.0
                for c in self.population:
                    cum += c.fitness / total_fitness
                    if p < cum:
                        new_pop.append (c)
                        break
        new_pop = new_pop[:POP_SIZE]
        #for c in sorted(new_pop, key= lambda c: c.fitness):
        #    print "{: <12} {}".format (c.genotype, c.fitness)
        self.population = new_pop




        
if __name__ == "__main__":
    main()
