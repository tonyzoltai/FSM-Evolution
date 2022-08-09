#!/usr/bin/env python

'''
experiment_4 - Compute a quasi-Pareto front on best prediction and smallest size in states, for FSM solutions evolving to
                recognise a changing random subset of a constant regular language.
                Different from "experiment_3" by using a regular language rather than ever-changing white noise as the global environment,
                of which the active subset is applied in selection.

Classes:
    None.

Functions:
    mutator - mutation operator for Moore Machines.  May add a new state, and will set a random transition arc, and will change the ouput of a random state to a random value.

'''

__author__ = "Gabor 'Tony' Zoltai"
__copyright__ = "Copyright 2022, Gabor Zoltai"
__credits__ = ["Gabor Zoltai"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Tony Zoltai"
__email__ = "tony.zoltai@gmail.com"
__status__ = "Prototype"


# Parameters
INPUT_ALPHABET_SIZE = 2



from experiment_3 import *

from copy import deepcopy
import itertools
import random
import numpy
from numpy.random import poisson
import logging
import optparse

import NaidooRefLanguages
import countable
import automata
import FSMScorer
import SMO_GP


class E4Scorer(FSMScorer.FSMScorer):
    '''A scorer for FSMs that uses a reference dictionary based on a changing subset of a regular language.'''
    def __init__(self, n, cmm) -> None:
        '''Create an FSMScorer of n strings that are branches of a binary tree from the empty string, being positive or negative examples of the language of the Canonical Moore Machine cmm.'''
        super().__init__()
        self.keylist = [()]
        self.mr = automata.MooreMachineRun(cmm)
        self.mr.multistep(self.keylist[0])
        self.reference_dict = {self.keylist[0]: self.mr.output()}
        for _ in range(n-1):
            self.extend()
    
    def extend(self):
        while True:
            parent = self.keylist[numpy.random.choice(len(self.keylist))]
            child = parent + (numpy.random.choice(2),)
            if not(child in self.keylist):
                break
        self.keylist.append(child)

        self.mr.reset()
        self.mr.multistep(child)
        self.reference_dict[child] = self.mr.output()

    def reduce(self):
        index = numpy.random.choice(len(self.keylist))
        key = self.keylist[index]
        self.keylist.pop(index)
        self.reference_dict.pop(key)

def create_scorer(table_size, cmm):

    logging.info("Maximal score: " + str(table_size))

    return E4Scorer(table_size, cmm)



def main(options, args):

    #for now, seed both the standard Python and NumPy random generators.  We may go fully NumPy later.
    random.seed(options.SEED)
    numpy.random.seed(options.SEED)

    logging.basicConfig(level=getattr(logging, options.LOGLEVEL.upper()),
                        format="%(asctime)s %(levelname)s: %(message)s")
    logging.info("Start of run")


    # Setup
    primitive = automata.CanonicalMooreMachine(input_count=2)

    fitness_scorer = create_scorer(options.DICTSIZE, automata.CanonicalMooreMachine.from_string(NaidooRefLanguages.L3))
    logging.info("Longest scoring string: " + str(max([len(s) for s in fitness_scorer.keylist])))

    change_per_gen = options.CHANGE / 100 * fitness_scorer.table_size()

    # Run the SMO-GP algorithm for N cycles
    change = 0
    for i, g in enumerate(SMO_GP.SMO_GP(
                    initial_individuals={primitive},
                    mutator=poisson_repeat(complexophile_mutator, 1.0),
                    objectives=(fitness_scorer.score, complexity_scorer),
                    dynamic_change=dynamic_change(fitness_scorer, change_per_gen)
                ).populations()):

        if options.INFOGENS >0 and i % options.INFOGENS == 0:
            logging.info("Generation " + str(i))
        if i >= options.GENERATIONS:
            break

    # Print the scoring dictionary
    logging.debug("Scoring table:")
    longest = max([len(s) for s in fitness_scorer.keylist])
    for length in range(longest + 1):
        for s in [ x for x in fitness_scorer.keylist if len(x) == length]:
                logging.debug("%s %s", s, fitness_scorer.reference_dict[s])

    # Print the resulting estimate of the Pareto front
    for individual, scores in g:
        logging.info("The following automaton scored %d with %d states:\n%s", scores[0], -scores[1] ,str(individual))
        print(-scores[1], scores[0], sep=",")

    logging.info("End of run")


# Self-test, to be executed for option -t
# Can't use unittest the way I want to, so writing it myself

def myAssertEqual(a,b):
    if a == b:
        print("Test case successful.")
    else:
        print("Test case failed.")
        print("a:")
        print(a)
        print("b:")
        print(b)

def selfTest():
        e = E3Scorer(15)
        myAssertEqual(15, len(e.keylist))
        myAssertEqual(15, len(e.reference_dict.keys()))
        e.reduce()
        e.reduce()
        myAssertEqual(13, len(e.reference_dict.keys()))


if __name__ == "__main__":

    parser = optparse.OptionParser(("Usage: %prog [OPTION]...\n"
                                    "Evolve FSMs to recognise a randomised language, using SMO-GP, output pairs of recognition score and FSM size."))
    parser.add_option("-l", "--log", choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
                    action="store", dest="LOGLEVEL", default="DEBUG",
                    help="set minimum logging level to LOGLEVEL; one of DEBUG, INFO, WARNING, ERROR or CRITICAL (default: %default)")
    parser.add_option("-g", "--generations", type="int", action="store", dest="GENERATIONS", default=1000,
                    help="specify the number of generations to run for (default: %default)")
    parser.add_option("-i", "--inform", type="int", action="store", dest="INFOGENS", default=10,
                    help="if not zero, produce a message as a sign of life every INFOGENS generations; ignored if logging level is higher than INFO (default: %default)")
    parser.add_option("-s", "--seed", type="int", action="store", dest="SEED", default=0,
                    help="specifies the starting seed of the random number generator, so runs are repeatable (default: %default)")
    parser.add_option("-d", "--dict", type="int", action="store", dest="DICTSIZE", default=6,
                    help="set the size of the dictionary of samples in the randomised language (default: %default)")
    parser.add_option("-c", "--change", type = "float", action="store", dest="CHANGE", default=0.0,
                    help="percentage of fitness reference table to change per generation (default: %default)")
    parser.add_option("-t", "--test", action="store_true", dest="SELFTEST",
                    help="executes a self test")

    (options, args) = parser.parse_args()

    if hasattr(options, "SELFTEST") and options.SELFTEST:
        selfTest()
    else:
        main(options, args)
