#!/usr/bin/env python3
'''
FSMScorer - A class to assign scores to FSMs based on how well they classify strings through their output.
'''

import semiautomata

class FSMScorer(object):
    '''A class to score FSMs based on their outputs against a reference set of strings.'''

    def __init__(self) -> None:
        self.reference_dict = dict()


    @classmethod
    def from_reference_dict(cls, rd):
        r = cls()
        r.reference_dict = rd
        return r

    @classmethod
    def from_function(cls, f, reference_strings):
        '''Constructor from a function and reference strings.'''
        r = cls()
        for s in reference_strings:
            r.reference_dict[s] = f(s)

        return r

    def score(self, automaton):
        '''Returns a pair of the number of correct results and the number of reference cases.'''
        count = 0
        run = semiautomata.Run(automaton)
        for w in self.reference_dict.keys():
            output = run.runstring(w)

            if output == self.reference_dict[w]:
                count += 1
        return (count, len(self.reference_dict))

# Unit testing code.


import unittest as ut

class TestCSA(ut.TestCase):

    def test_creation(self):
        f = FSMScorer()
        f.reference_dict[()] = []

        a = semiautomata.CanonicalMooreMachine.from_string(
            "0 0 0 1 2\n"
            "1 0 0 1 2\n"
            "2 1 8 1 2")
        s,t = f.score(a)
        self.assertEqual(t,1)
        self.assertEqual(s, 0)

    
    def test_from_reference_dict(self):
        f = FSMScorer.from_reference_dict({():0, (2,):1})
        a = semiautomata.CanonicalMooreMachine.from_string(
            "0 0 0 1 2\n"
            "1 0 0 1 2\n"
            "2 1 8 1 2")
        s,t = f.score(a)
        self.assertEqual(t, 2)
        self.assertEqual(s, 2)


    def test_from_function(self):
        def Kleene_of(repeated, s):
            if len(s) == 0:
                return True
            elif s[0:len(repeated)] == repeated:
                return Kleene_of(repeated, s[len(repeated):])
            else:
                return False

        def recognise_ab_star(w):
            '''Return 1 if the input is a member of the language (ab)*, else 0.'''
            return 1 if Kleene_of((0, 1), w) else 0

        f = FSMScorer.from_function(recognise_ab_star,((), (0, 1), (0, 1, 1) ))
        a = semiautomata.CanonicalMooreMachine.from_string(
            "0 1 2 1\n"
            "1 0 0 2\n"
            "2 0 2 2")

        s,t = f.score(a)
        self.assertEqual(t, 3)
        self.assertEqual(s, 2)


if __name__ == '__main__':
    ut.main()