#!/usr/bin/env python
'''uniwitness - Moore Machines based on the "U" stream (series) of regular languages and corresponding DFAs (the "universal witness" languages) described in:
    Brzozowski, J. (2012). In Search of Most Complex Regular Languages.
    In: Moreira, N., Reis, R. (eds) Implementation and Application of Automata. CIAA 2012.
    Lecture Notes in Computer Science, vol 7381. Springer, Berlin, Heidelberg.
    https://doi.org/10.1007/978-3-642-31606-7_2


Classes:

        UniWitness - implements any of the "U(n)" languages described by Brzozowski.

Functions:

    None.
'''

from automata import CanonicalMooreMachine, MooreMachineRun

class UniWitness(CanonicalMooreMachine):
    '''UniWitness - implements any of the "U(n)" languages described by Brzozowski.'''

    def __init__(self, state_count) -> None:
        '''Create a DFA for U(n) as a Moore Machine.  Comments from "Definition 5" of the Brzozowski paper.'''
        # let Un(a,b,c) = (Q,Σ,δ,q0,F), where Q = {0,...,n−1} is the set of states, Σ = {a,b,c} is the alphabet,
        super().__init__(state_count, 3, 2)

        # δ(q,a) = q+1 (mod n)
        for q in self.states():
            self.set_arc(q, 0, (q + 1) % state_count)
        
        # δ(0,b) = 1
        self.set_arc(0, 1, 1)

        # δ(1, b) = 0
        self.set_arc(1, 1, 0)

        # δ(q,b) = q for q ∈ {2,3,...,n − 1}
        for q in self.states():
            if q > 1:
                self.set_arc(q, 1, q)
        
        # δ(n − 1,c) = 0
        self.set_arc(state_count - 1, 2, 0)

        # δ(q,c) = q for q ∈ {0,1,...,n − 2}
        for q in self.states():
            if q < state_count - 1:
                self.set_arc(q, 2, q)
        
        # F = {n−1} is the set of final states
        self.set_output(state_count - 1, 1)


# Unit testing code

import unittest as ut

class TestUniWitness(ut.TestCase):

    def test_uniwitness(self):
        u = UniWitness(5)
        r = MooreMachineRun(u)
        self.assertEqual(r.output(), 0)
        r.multistep((0, 1, 1, 2, 0, 1, 2, 0, 2, 1, 0, 1))
        self.assertEqual(r.output(), 1)
        r.multistep((2, 1, 0, 0, 0))
        self.assertEqual(r.output(), 1)
        r.multistep((0, 2, 2, 0, 0, 0, 0, 0))
        self.assertEqual(r.output(), 0)
        self.assertEqual(r.state(), 0)

if __name__ == "__main__":
    ut.main()
