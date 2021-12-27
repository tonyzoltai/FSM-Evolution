#!//usr/bin/env python

'''
Tools for semiautomata, a mathematical abstration of simple computational devices.

A semiautomaton is specified by a set of states, a set of input symbols,and a
function mapping each pair of state and input to a "next state".  In this way, a
semiautomaton can be seen as a deterministic finite automaton without a specified
starting state or outputs based on state (e.g. a subset set of "accepting" states).
'''

# Internally, the representation of a semiautomaton is a canonicalised form, in
# which the states are numbered 0...n-1, and the input symbols 0...m-1, with n
# and m being the number of states and input symbols respectively.


# The to-do list refers to GitHub Issue numbers
#TODO #1
#TODO #3

import itertools as it

class CanonicalSemiAutomaton(object):
    '''A canonicalised semiautomaton, with unsigned ints for states and inputs.'''
    def __init__(self):
        '''Initially, the SA has one input and one state, which loops back to itself.'''
        self.max_state = 0
        self.max_input = 0
        self.transitions = {0:{0:0}}
        self.outputs = {0:0}
    
    def add_arc(self, state, input, next):
        '''Add an arc from state on input to next.'''
        self.max_state = max(self.max_state, state, next)
        self.max_input = max(self.max_input, input)
        if state not in self.transitions:
            self.transitions[state] = {0:0}
        t = self.transitions[state]
        t[input] = next
    
    def delta(self, state, input):
        '''Return a stored next state for the pair of state and input, or the default self-loop back to the state itself.'''
        if state in self.transitions:
            t = self.transitions[state]
            if input in t:
                return t[input]
            else:
                return state
        else:
            return state
    
    def G(self, state):
        '''Return the output of a state (named after the standard G function of a Moore Machine).'''
        if state in self.outputs:
            return self.outputs[state]
        else:
            # If not specified, the output is zero by default.
            return 0
    
    def alphabet_iterate(self, state):
        '''Iterate through the arcs leaving the given state.'''
        for input in range(self.max_input + 1):
            yield (input, self.delta(state, input))

    def __repr__(self) -> str:
        '''Return an unambiguous string representation.'''
        return "\n".join("State "+ repr(state) + " output " + repr(self.G(state)) + "\n" \
                        + "\n".join(" on " + repr(sym) + ": " + repr(self.delta(state, sym)) for sym in range(self.max_input + 1)) \
                        for state in range(self.max_state + 1))

    @classmethod
    def from_string(cls, s):
        '''Initialise from a multiline string.  Each line contains a state number, output value and next states, starting from input 0.'''
        #Create the CSA.
        CSA = cls()
        # Split the string into lines.
        for line in s.splitlines():
            a = list(map(int,line.split()))
            state = a[0]
            CSA.outputs[state] = a[1]
            for symbol, next in enumerate(a[2:]):
                CSA.add_arc(state, symbol, next)
        return CSA


# Unit testing code.
# Create a subclass of unittest.Testcase, with each test being a method named beginning with "test_".
# At the end, as the "main" executable code of the module, check if the name of the cu

import unittest as ut

class TestCSA(ut.TestCase):
    def test_creation(self):
        a = CanonicalSemiAutomaton()
        self.assertEqual(len(a.transitions), 1)
        self.assertEqual(a.delta(0, 0), 0)
        self.assertEqual(a.outputs[0], 0)

    def test_add_arc(self):
        a = CanonicalSemiAutomaton()
        a.add_arc(0, 7, 8)
        self.assertEqual(a.max_input, 7)
        self.assertEqual(a.max_state, 8)
        self.assertEqual(a.delta(0, 7), 8)

    def test_iterate(self):
        a = CanonicalSemiAutomaton()
        a.add_arc(0, 7, 8)
        a.add_arc(0, 3, 5)
        iter = dict(list(a.alphabet_iterate(0)))
        self.assertEqual(iter[0], 0)
        self.assertEqual(iter[3], 5)
        self.assertEqual(iter[7], 8)
    
    def test_fromstring(self):
        s = ("0 0 0 1 2\n"
             "1 0 0 1 2\n"
             "2 1 8 1 2")
        a = CanonicalSemiAutomaton.from_string(s)
        self.assertEqual(a.max_state, 8)
        self.assertEqual(a.max_input, 2)


if __name__ == '__main__':
    ut.main()
