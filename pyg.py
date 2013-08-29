# gene.py - Runs genetic simulation.
import random
import string
import math
import threading
import multiprocessing
import sys
import time

# GA parameters
POP_SIZE    = 1000
COPY_RATE   = 0.10
MUTATE_RATE = 0.10
TARGET = """print "Hello, world!" """

# Fitness function.
def f (s, target=TARGET):
    # Assumes s and target are same length.
    return sum ([(s[i]==target[i]) for i in range (len (s))])


def main ():
    g = Gene()
    g.iterate()
    i = 0
    while max (g.population, key=lambda l: f(l.genotype)).fitness != len (TARGET):
        i += 1
        c = sorted (g.population, key=lambda l: f(l.genotype), reverse=True)[0]
        print "'{}' -> {} {}".format (c.genotype, f(c.genotype), i)
        g.iterate ()

def mass_main ():
    start = time.time()
    # Gene is genetic algorithm class.
    g = Gene()
    num_iter = 10
    for i in range (num_iter + 1):
        # Print progress bar to estimate simulation time.
        # e.g. [==================  ] 91%  21 sec 
        sys.stdout.write('\r') # Go to beginning of line.
        # n is number of '='s to fill in.
        n = int (math.floor (i / (num_iter / 20.0)))
        sys.stdout.write("[%-20s] %d%% %f sec" % ('='*n, float(i)/num_iter*100, time.time() - start))
        sys.stdout.flush()
        # Let the bar go to 100%. 
        if i < num_iter:
            g.iterate ()
    print ""
    print '\n'.join (map (str, g.history))


class Chromosome:
    def __init__ (self, genotype=None):
        # Parameters are: K_xy, K_xz, K_yz
        if genotype is None:
            self.genotype = "".join ([random.choice (string.printable) for i in range (len (TARGET))])
        else:
            self.genotype = genotype
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
        chromosome.genotype = "".join(child)
        return chromosome

    def set_fitness (self, fitness):
        self.fitness = fitness

    def mutate (self):
        # Mutates a random gene by flipping bits.
        gene = random.choice (range (self.num_param))
        g = list (self.genotype)
        g[gene] = random.choice (string.printable)
        self.genotype = "".join (g)

class MP_Simulation(multiprocessing.Process):
    # For when multiple cores are available. 
    def __init__ (self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        # Delegates to each process through a queue. 
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run (self):
        while True:
            c = self.task_queue.get()
            fitness = 0
            if c is None:
                break
            try:
                fitness = f (c.genotype)
            except:
                pass
            c.fitness = fitness
            self.result_queue.put (c)
            

class SimulationThread(threading.Thread):
    # Performance decreases with number of threads.
    def __init__ (self, population, starti, endi):
        threading.Thread.__init__(self)
        self.population = population
        self.starti = starti
        self.endi = endi

    def run (self):
        # Only simulate a portion of chromosome list. 
        starti = self.starti
        endi = self.endi
        num_iter = len (self.population) / 2
        for i in range (starti, endi):
            c = self.population [i]
            fitness = 0
            try:
                fitness = f (c.genotype)
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
        self.unthreaded_simulation ()

    def simulate_multicore (self):
        # Runs simulation on all cores.
        tasks = multiprocessing.Queue()
        results = multiprocessing.Queue()
        num_consumers = multiprocessing.cpu_count() * 2
        # Consumers do the crunching.
        consumers = [ MP_Simulation (tasks, results)
                      for i in xrange (num_consumers) ]
        for w in consumers:
            w.start()
        # Put population in queue.
        num_chrom = POP_SIZE
        for i in xrange (num_chrom):
            tasks.put (self.population [i])

        # Stops calculating when it receives a None. 
        for i in xrange (num_consumers):
            tasks.put (None)
        population = list()
        while num_chrom:
            C = results.get()
            population.append (C)
            num_chrom -= 1
        # Save results.
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

    def unthreaded_simulation (self):
        # Run population through simulation.
        for c in self.population:
            c.set_fitness (f (c.genotype))

        #for c in sorted(self.population, key= lambda c: c.fitness):
        #    print "{: <12} {}".format (c.genotype, c.fitness)

    def best_fitness (self):
        return min ([c.fitness for c in self.population])

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
        # Trim population
        new_pop = new_pop[:POP_SIZE]
        self.population = new_pop

        
if __name__ == "__main__":
    main()
