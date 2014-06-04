#!/usr/bin/python2.7
"""
Let a population of random strings coverge to `target`.
"""
import random
import string
import sys
import gene

def main():
    pyg = gene.pyg(StringGene)
    while pyg.top.score < len(StringGene.target):
        pyg.iterate()
        # Print top performer from each generation.
        out = ''.join(pyg.top.genotype)
        sys.stdout.write('\r' + out + ' ' * 5)
        sys.stdout.flush()

    print ''
    print 'winner', '=>', pyg.top.genotype
    print pyg.iterations, 'iterations'

class StringGene(gene.Chromosome):
    """Generates a random string and scores it by closeness
    to `target`."""

    target = "genetic algorithms"
    @staticmethod
    def generate():
        return [random.choice(string.printable)
                for _ in range(len(StringGene.target))]

    @staticmethod
    def fitness(genotype):
        return sum([a == b for a, b in
                    zip(StringGene.target, genotype)])


if __name__ == '__main__':
    main()
