## pyg

#### Usage:
Create a file ``simulation.py`` and override the ``Chromosome`` class. 


## Genetic Algorithms

#### The Chromosome

A chromosome stores its **fitness** and a **genotype**. The genotype could be a list of integers, a string--any data
structure. Fitness is a value from a fitness function. Here we use ``simulate ()`` to calculate fitness. The chromosome also supplies two methods: ``mate`` and ``mutate``.

###### ``mate``:

``mate`` takes another chromosome as a parameter and returns a
child chromosome. This is the genetic operation
**recombination**.

Here's some sample code:

```python
def mate (C):
    """
    Each gene has a 50% chance of being passed on.
    """
    child = list ()
    for i in range (num_param):
        if random.random () < 0.5:
            child.append (C.genotype[i])
        else:
            child.append (self.genotype[i])
    c = Chromosome ()
    c.genotype = child
    return c
```
        
###### ``mutate``:
``mutate`` picks a gene in the genotype and alters it. This could be bit flipping, scaling, seeding a new value... 

```python
def mutate ():
    """
    Mutates a random gene.
    """
    gene = random.choice (range(num_param))
    self.genotype[gene] *= random.lognormvariate (0, 1)
```

#### The Algorithm

###### ``selection``:
We select chromosomes for the next generation with probabilities in proportion to their fitness. This is called [roulette-wheel selection](https://en.wikipedia.org/wiki/Roulette_wheel_selection). We will also implement [stochastic universal sampling](http://en.wikipedia.org/wiki/Stochastic_universal_sampling). This is to counter a bias for very high-performing chromosomes. 

```python
def selection ():
    """
    Picks new population based on fitness.
    """
    # Use total fitness to normalize values.
    total_fitness = sum ([c.fitness for c in self.population])
    population = list()
    while len (population) < POP_SIZE:
        # Add chromosome when random number falls in its bin.
        cum = 0.0
        c = random.random ()
        for c in self.population:
            # Bin size is proportional to fitness.
            cum += c.fitness / total_fitness
            if r < cum:
                population.append (c)
                break
        # Sample chrosomes at intervals around bin.
        pointers = [-0.4, -0.2, +0.2, +0.4]
        pointers = [x % 1.0 for x in [r + y for y in pointers]]
        for p in pointers:
            # Find which bin pointer falls in. 
            cum = 0.0
            for c in self.population:
                cum += c.fitness / total_fitness
                if p < cum:
                    population.append (c)
                    break
        # Trim population if pointers cause overflow.
        population = population [:POP_SIZE]
        self.population = population
```

###### ``crossover``:
We must put our chromosome methods in a wrapper. 
Here is an operation for recombination:

```python
def crossover ():
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
```
        
        
