#!/usr/bin/env python3
'''
FSMScorer - A class to assign scores to FSMs based on how well they classify strings through their output.

    Classes:
        FSMScorer - scores 

'''

import automata

class FSMScorer(object):
    '''A class to score FSMs based on their outputs against a reference set of strings.'''

    def __init__(self) -> None:
        self.reference_dict = dict()
        # initialise the cache
        self.cache = dict()


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

    def table_size(self):
        '''Returns the number of reference strings.'''
        return len(self.reference_dict)
    
    def ref_and_output(self, n):
        '''Return the n-th reference string and its output.'''
        k = list(self.reference_dict.keys())[n]
        return (k, self.reference_dict[k])

    def set_output(self, s, out):
        '''Set the expected output for string s to out.'''
        self.reference_dict[s] = out
        # This has modified at least one string/output pair, therefore reset the cache
        self.cache = dict()

    def score(self, automaton):
        '''Returns the number of correct results.'''
        #First, check if the automaton's score is cached
        h = str(automaton)
        if h in self.cache:
            return self.cache[h]
        else:
            # not cached, compute value, cache it and return it
            count = 0
            run = automata.MooreMachineRun(automaton)
            for w in self.reference_dict.keys():
                run.multistep(w)
                output = run.output()

                if output == self.reference_dict[w]:
                    count += 1
            # cache before returning
            self.cache[h] = count
            return count

# Unit testing code.


import unittest as ut

class TestCSA(ut.TestCase):

    def test_creation(self):
        f = FSMScorer()
        f.reference_dict[()] = []

        self.assertEqual(f.table_size(),1)
        self.assertEqual(len(f.cache), 0)

        a = automata.CanonicalMooreMachine.from_string(
            "0 0 1 2\n"
            "0 0 1 2\n"
            "1 8 1 2")
        s = f.score(a)

        self.assertEqual(s, 0)
        self.assertTrue(str(a) in f.cache)
        self.assertFalse("" in f.cache)

    
    def test_from_reference_dict(self):
        f = FSMScorer.from_reference_dict({():0, (2,):1})
        a = automata.CanonicalMooreMachine.from_string(
            "0 0 1 2\n"
            "0 0 1 2\n"
            "1 8 1 2")
        s = f.score(a)
        self.assertEqual(f.table_size(), 2)
        self.assertEqual(s, 2)
        a = automata.CanonicalMooreMachine.from_string(
            "0 1 1 2\n"
            "0 0 1 2\n"
            "1 8 1 2")
        s = f.score(a)
        self.assertEqual(len(f.cache), 2)

    def test_direct_access(self):
        f = FSMScorer.from_reference_dict({():0, (2,):1})
        p = f.ref_and_output(1)
        self.assertEqual(p, ((2,),1))

        f.set_output(p[0],2)
        _,s = f.ref_and_output(1)
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
        a = automata.CanonicalMooreMachine.from_string(
            "1 2 1\n"
            "0 0 2\n"
            "0 2 2")

        s = f.score(a)
        self.assertEqual(len(f.reference_dict), 3)
        self.assertEqual(s, 2)
        self.assertEqual(len(f.cache), 1)
        self.assertTrue(str(a) in f.cache)


if __name__ == '__main__':
    ut.main()