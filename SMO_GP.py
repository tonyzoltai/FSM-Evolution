#!/usr/bin/env python
'''
SMO_GP - An implementation of the SMO-GP algorithm from "Computational Complexity Analysis of Multi-Objective Genetic Programming" by F Neumann 2021.

Classes:

    Dominance - enumeration of the outcomes of comparing two sets of N-dimensional score vectors.
    SMO_GP - a class implementing the SMO-GP algorithm, which over enough iterations approaches a population that is the Pareto front for the solution space.
    Test_SMO_GP - used for unit testing, via the standard unittest module.

Functions:

    Default_Dominance_Compare - given two score vectors assumed to have the same length, returns a Dominance value based on the usual comparison operators.
'''

import numpy as np
import logging
from enum import IntEnum, auto

class Dominance(IntEnum):
    '''Enum type that expresses whether either of two compared vectors dominates the other, or they are equal, or not comparable.'''
    NOT_COMPARABLE = auto()
    LEFT = auto()
    EQUAL = auto()
    RIGHT = auto()

def Default_Dominance_Compare(vector_a, vector_b):
    '''Default and sample dominance comparator - vector_a and vector_b are both vectors of things that can be compared by normal operators.'''
    left_win = False
    right_win = False
    for i, a in enumerate(vector_a):
        if a > vector_b[i]:
            left_win = True
        elif a < vector_b[i]:
            right_win = True
    if left_win:
        if right_win:
            return Dominance.NOT_COMPARABLE
        else:
            return Dominance.LEFT
    else:
        if right_win:
            return Dominance.RIGHT
        else:
            return Dominance.EQUAL
        

class SMO_GP:
    '''The SMO-GP algorithm, packaged as an iterator over generations.
    Each generation may add one mutant, which is added, and all individuals whose scores it dominates are deleted.
    Before the mutation is dont, the dynamic_change mutator is called in each generation - if it returns true, the environment has chaned and
    the scores of the population are recomputed.'''

    def __init__(self, initial_individuals, mutator, objectives, dominance_compare=Default_Dominance_Compare,
                dynamic_change=None) -> None:
        self._mutator = mutator
        self._objectives = objectives
        self._dominance_compare = dominance_compare
        self._dynamic_change = dynamic_change
        # Create the initial population as a list of pairs of individuals and tuples of their scores on objective fuctions
        self._population = [(i, (*(obj(i) for obj in self._objectives),)) for i in initial_individuals]


    def populations(self):
        '''Iterator that yields populations, as a list of pairs of (individual, score_vector).  Individuals can be any type, score vectors are iterables whose members can be compared.'''

        def adjust_population(candidate, candidates_scores):
            # Find out if any individual strongly dominates the candidate; and collect those weakly dominated by it
            dominated_set = set()
            for index, (_, individuals_scores) in enumerate(self._population):
                dominance = self._dominance_compare(individuals_scores, candidates_scores)
                if dominance == Dominance.LEFT:
                    # An individual in the existing population dominates the candidate; drop the candidate
                    break
                elif dominance == Dominance.EQUAL or dominance == Dominance.RIGHT:
                    # Add individual's index to the list to be deleted, if we don't BREAK out of the loop
                    dominated_set.add(index)
            else:
                # If we get here, no individual in the population dominates the candidate
                # construct the new population by first of all dropping anything that was dominated by the candidate
                new_population = [self._population[i] for i in range(len(self._population)) if i not in dominated_set]

                # now add the candidate and its scores
                new_population.append((candidate, candidates_scores))
                self._population = new_population


        # Yield generation "zero"
        yield self._population

        while True:
            # Call the dynamic change function if there is one.
            while not(self._dynamic_change is None) and next(self._dynamic_change):
                # Recompute the scores of the whole population, and eliminate weakly dominated individuals.
                self._population = [(i[0], (*(obj(i[0]) for obj in self._objectives),)) for i in self._population]
                logging.debug("Recomputed : " + str(self._population))

            # Choose a random individual from the population, ignore its scores
            #parent = random.choice(self._population)[0]
            parent = self._population[np.random.choice(len(self._population))][0]
            # Copy and mutate it into a new individual Y
            # This assumes that the mutator function makes a deep copy if necessary
            candidate = self._mutator(parent)
            candidates_scores = *(obj(candidate) for obj in self._objectives),

            # print("Candidate")
            # print(candidate)
            # print(candidates_scores)

            adjust_population(candidate, candidates_scores)
            
            yield self._population


# Unit testing code.
# Create a subclass of unittest.Testcase, with each test being a method named beginning with "test_".
# At the end, as the "main" executable code of the module, check if the name of the cu

import unittest as ut


class Test_SMO_GP(ut.TestCase):
    def test_SMO_GP(self):
        np.random.seed(0)
        op = SMO_GP({(0 ,0, 0)},
            (lambda t: ((t[0]+np.random.randint(0,4))%4, (t[1]+np.random.randint(0,4))%4, (t[2]+np.random.randint(0,4))%4)),
            ((lambda v: v[0]),(lambda v: v[1]),(lambda v: v[2])))
        for i, gen in enumerate(op.populations()):
            if i>=100:
                break
        self.assertEqual(gen, [((3, 3, 3), (3, 3, 3))])

    def test_SMO_GP_dynamic(self):
        self.counter = 0

        def simple_objective(_):
            return self.counter

        def simple_dynamic():
            while True:
                self.counter += 1
                print("counter", self.counter)
                #yield true to indicate resetting the scores
                yield self.counter % 3 == 0

        op = SMO_GP(
            initial_individuals={(0,0)},
            mutator=(lambda t: (t[0]+1, t[1]+1)),
            objectives=(simple_objective, simple_objective),
            dominance_compare=Default_Dominance_Compare,
            dynamic_change=simple_dynamic())

        for i, gen in enumerate(op.populations()):
            print(i, gen)
            if i>=100:
                break
        self.assertEqual(gen, [((100,100),(149,149))])




if __name__ == '__main__':
    ut.main()