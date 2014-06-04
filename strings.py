#!/usr/bin/python2.7
import random
import string
import sys
import gene

def main():
    pyg = gene.Pyg(StringGene)
    while pyg.top.score < len(StringGene.target):
        pyg.iterate()
        out = ''.join(pyg.top.genotype)
        sys.stdout.write('\r' + out + ' ' * 5)
        sys.stdout.flush()
    print ''
    print 'winner', '=>', pyg.top.genotype
    print pyg.iterations, 'iterations'

class StringGene(gene.Chromosome):
    target = "alex stachowiak"
    
    @staticmethod
    def generate():
        return [random.choice(string.printable)
                for i in range(len(StringGene.target))]

    @staticmethod
    def fitness(genotype):
        return sum([a == b for a, b in
                   zip(StringGene.target, genotype)])


if __name__ == '__main__':
    main()
