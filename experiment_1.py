#!/usr/bin/env python

'''
experiment_1 - Compute the Pareto front on best prediction and smallest size in states, for FSM solution evolving to recognise a randomised small language.

Classes:
    None.

Functions:
    dict_score - given a dictionary of keys and values to be computed from them, runs a given function on each key, and counts the values that the function gets right.
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
MAX_STRING_LENGTH = 6
INPUT_ALPHABET_SIZE = 2
GENERATIONS = 100000
LOG_GENERATIONS = 1000

def dict_score(dictionary, function):
    '''dict_score - compute how well a function does in computing the values from the keys of a dictionary.'''
    sum(1 for k, v in dictionary.items() if function(k) == v)

from copy import deepcopy
import itertools
import random
import numpy
from numpy.random import poisson
import logging
import optparse

import countable
import automata
import FSMScorer
import SMO_GP


def mutator(mm_parent: automata.CanonicalMooreMachine):

    # First, make a copy of the given parent object
    m = deepcopy(mm_parent)

    source_state = random.randrange(m.state_count())
    input = random.randrange(m.input_count())
    target_state = random.randrange(m.state_count() + 1)

    if target_state == m.state_count():
        m.add_state()

    m.set_arc(source_state, input, target_state)

    # Change the output of a random state to a random value
    state_to_change = random.choice(list(m.states()))
    new_output = random.choice(list(m.outputs()))
    m.set_output(state_to_change, new_output)

    return m

def repeated_application(f, k):
    '''Return a function to apply a function to its input k times.'''
    def fun(x):
        r = x
        for _ in range(k):
            r = f(r)
        return r
    
    return fun


def create_scorer():
    scoring_strings = list(itertools.chain.from_iterable(countable.ND(it,INPUT_ALPHABET_SIZE) for it in range(MAX_STRING_LENGTH + 1)))
    max_score = len(scoring_strings)
    logging.info("Maximal score: " +str(max_score))
    # create randomised reference dictionary
    rd = dict()
    for s in scoring_strings:
        rd[s] = random.randint(0, 1)
    
    return FSMScorer.FSMScorer.from_reference_dict(rd)

def complexity_scorer(moore_machine: automata.MooreMachine):
    '''Returns an integer score for the complexity of a given Moore machine.  The lower the number of states, the higher the score.'''
    return -moore_machine.state_count()


def main(options, args):

    #for now, seed both the standard Python and NumPy random generators.  We may go fully NumPy later.
    random.seed(options.SEED)
    numpy.random.seed(options.SEED)

    logging.basicConfig(level=getattr(logging, options.LOGLEVEL.upper()),
                        format="%(asctime)s %(levelname)s: %(message)s")
    logging.info("Start of run")


    # Setup
    primitive = automata.CanonicalMooreMachine(input_count=2)

    fitness_scorer = create_scorer()

    # Run the SMO-GP algorithm for N cycles
    for i, g in enumerate(SMO_GP.SMO_GP({primitive}, repeated_application(mutator, 1 + poisson(1,1)[0]),(fitness_scorer.score, complexity_scorer)).populations()):
        if options.INFOGENS >0 and i % options.INFOGENS == 0:
            logging.info("Generation " + str(i))
        if i >= options.GENERATIONS:
            break

    # Print the resulting estimate of the Pareto front
    for individual, scores in g:
        logging.info("The following automaton scored %d with %d states:\n%s", scores[0], -scores[1] ,str(individual))
        print(-scores[1], scores[0], sep=",")

    logging.info("End of run")



if __name__ == "__main__":

    parser = optparse.OptionParser(("Usage: %prog [OPTION]...\n"
                                    "Evolve FSMs to recognise a randomised language, using SMO-GP, output pairs of recognition score and FSM size."))
    parser.add_option("-l", "--log", choices = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
                    action="store", dest="LOGLEVEL", default="DEBUG",
                    help="set minimum logging level to LOGLEVEL; one of DEBUG, INFO, WARNING, ERROR or CRITICAL (default: %default)")
    parser.add_option("-g", "--generations", type="int", action="store", dest="GENERATIONS", default=1000,
                    help="specify the number of generations to run for (default: %default)")
    parser.add_option("-i", "--inform", type="int", action="store", dest="INFOGENS", default=0,
                    help="if not zero, produce a message as a sign of life every INFOGENS generations; ignored if logging level is higher than INFO (default: %default)")
    parser.add_option("-s", "--seed", type="int", action="store", dest="SEED", default=0,
                    help="specifies the starting seed of the random number generator, so runs are repeatable (default: %default)")

    (options, args) = parser.parse_args()

    main(options, args)
