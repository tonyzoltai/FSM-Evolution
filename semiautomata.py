#!//usr/bin/env python

'''
Tools for semiautomata, a mathematical abstration of simple computational devices.

A semiautomaton is specified by a set of states, a set of input symbols,and a
function mapping each pair of state and input to a "next state".  In this way, a
semiautomaton can be seen as a deterministic finite automaton without a specified
starting state or outputs based on state (e.g. a subset of "accepting" states).
'''

# TODO Rename semiautomata.py and CanonicalSemiAutomaton class
# DONE Move "outputs" to a new subclass called "MooreSemiAutomaton"
# TODO Create a superclass structure for semiautomata
#      - the highest may be a set of functions that map some state/input pair to a state (poss. infinite state space and alphabet) - a "demiautomaton"

# Internally, the representation of a semiautomaton is a canonicalised form, in
# which the states are numbered 0...n-1, and the input symbols 0...m-1, with n
# and m being the number of states and input symbols respectively.


import random
import string
import copy


#Utilities

def readable_symbol(n, alphabet = string.ascii_lowercase):
    '''Translate the an integer from 0,1,... into a,b,...,z,aa,ab,... or similar alphabets for human consumption of states and symbols.'''
    if n < len(alphabet):
        return alphabet[n]
    else:
        return readable_symbol((n // len(alphabet)) - 1, alphabet) + alphabet[n % len(alphabet)]


#The actual classes.

class CanonicalSemiAutomaton(object):
    '''A canonicalised semiautomaton, with unsigned ints for states and inputs.'''
    def __init__(self):
        '''Initially, the SA has one input and one state, which loops back to itself.'''
        self.max_state = 0
        self.max_input = 0
        self.transitions = {0:{0:0}}
    
    def deepcopy(self):
        return copy.deepcopy(self)

    def add_arc(self, state, input, next):
        '''Add an arc from state on input to next.'''
        self.max_state = max(self.max_state, state, next)
        self.max_input = max(self.max_input, input)
        if state not in self.transitions:
            self.transitions[state] = {0:0}
        t = self.transitions[state]
        t[input] = next

    def delete_state(self, state):
        '''Delete the specific state, replacing all arcs toward it with self-loops.'''
        # Actually, we replace the state with the highest-numbered one, and decrease max_state.
        d = state           # the state to be deleted
        r = self.max_state  # the state to replace it

        for s in self.all_states():
            for t in self.transitions[s]:
                



    
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
        
    def alphabet_iterate(self, state):
        '''Iterate through the arcs leaving the given state.'''
        for input in range(self.max_input + 1):
            yield (input, self.delta(state, input))

    def all_states(self):
        '''Iterate through all states of the automaton.'''
        for s in range(self.max_state + 1):
            yield s

    def __repr__(self) -> str:
        '''Return an unambiguous string representation.'''
        return "\n".join("State "+ repr(state) + "\n" \
                        + "\n".join(" on " + repr(sym) + ": " + repr(self.delta(state, sym)) for sym in range(self.max_input + 1)) \
                        for state in range(self.max_state + 1))

class Run(object):
    '''A semiautomaton in action. It has a current state, and moves through states based on input.'''

    def __init__(self, automaton, start = 0):
        '''Initialise a run with an automaton and a start state.'''
        super().__init__()
        self.automaton = automaton
        self.restart(start)

    def __repr__(self) -> str:
        return "Current State: " + repr(self.state) + " (automaton object id: " + str(id(self.automaton)) + ")"

    def step(self, input):
        '''Process a single input item.'''
        self.state = self.automaton.delta(self.state, input)

    def multistep(self, inputs):
        '''Process a sequence of inputs.'''
        for i in inputs:
            self.step(i)
    
    def runstring(self, inputs):
        '''Process the input from the starting state, return the final output.'''
        self.restart()
        self.multistep(inputs)
        return self.automaton.G(self.state)
    
    def restart(self, start = 0):
        self.state = start


class CanonicalMooreMachine(CanonicalSemiAutomaton):
    '''Moore machines are automata with finite states, and each state having an output symbol from an output alphabet.
        This class also has a "mutate" method, which needs pre-set in- and output alphabets.'''

    # Default alphabets are binary, i.e. the max canonical value of in- and output are 1.
    def __init__(self, max_input = 1, max_output = 1):
        '''Initialise the Moore machine as a one-state semiautomaton, with zero as the output.'''

        # Start with the parent class initialisation
        super().__init__()

        # The maximum inputs and outputs (i.e. size of alphabet - 1) needs to be set for the "mutate" method.
        self.max_input = max_input
        self.max_output = max_output

        # Initialise the bits of data we carry over and above the parent class.
        self.start = 0
        self.outputs = dict()
        self.set_output(0,0)



    def __repr__(self) -> str:
        '''Return an unambiguous string representation.'''
        return "\n".join("State "+ repr(state) + " output " + repr(self.G(state)) + "\n" \
                        + "\n".join(" on " + repr(sym) + ": " + repr(self.delta(state, sym)) for sym in range(self.max_input + 1)) \
                        for state in range(self.max_state + 1))

    def set_output(self, state, output):
        '''Set the output of a state to a value.'''

        # If a new output value is added, expand the range
        if output > self.max_output:
            self.max_output = output

        self.outputs[state] = output
    
    def G(self, state):
        '''Return the output of a state (named after the standard G function of a Moore Machine).'''
        if state in self.outputs:
            return self.outputs[state]
        else:
            # If not specified, the output is zero by default.
            return 0
    
    def deepcopy(self):
        return copy.deepcopy(self)

    def mutate(self):
        # Change one arc in the auomaton to a random destination, wihch could expand the state space.
        # So, a mutation operator can take an arc from an existing state, point it to a random state, and assign a random output to that state (and the state may be new).
        # Choose a target state for the mutated arc, which could be a new state being added.
        target_state = random.randint(0,self.max_state + 1)

        # If the state is new, give it a random output.
        if target_state > self.max_state:
            self.set_output(target_state, random.randint(0, self.max_output))
        
        # Set the arc from a random existing state to the target state.
        self.add_arc(random.randint(0,self.max_state), random.randint(0,self.max_input), target_state)
   
    def display(self, inputs=string.ascii_lowercase, states=string.ascii_uppercase, outputs=["REJECT","ACCEPT","THIRD","FOURTH"]):
        print()
        print("State |Output|", end="")
        for a in range(self.max_input + 1):
            print(f"{readable_symbol(a,inputs):>7}", end="")
        print()
        print("-" * 7 * (self.max_input + 3))
        for s in range(self.max_state + 1):
            print(f"{readable_symbol(s,states):>6}|", end="")
            print(f"{readable_symbol(self.G(s),outputs):>6}|", end="")
            for a in range(self.max_input + 1):
                print(f"{readable_symbol(self.delta(s, a),states):>7}", end="")
            print()


    @classmethod
    def from_string(cls, s):
        '''Initialise from a multiline string.  Each line contains a state number, output value and next states, starting from input 0.'''
        #Create the CSA.
        mm = cls()
        # Split the string into lines.
        for line in s.splitlines():
            a = list(map(int,line.split()))
            state = a[0]
            mm.outputs[state] = a[1]
            for symbol, next in enumerate(a[2:]):
                mm.add_arc(state, symbol, next)
        return mm



# Unit testing code.
# Create a subclass of unittest.Testcase, with each test being a method named beginning with "test_".
# At the end, as the "main" executable code of the module, check if the name of the cu

import unittest as ut

class TestCSA(ut.TestCase):
    def test_creation(self):
        a = CanonicalMooreMachine()
        self.assertEqual(len(a.transitions), 1)
        self.assertEqual(a.delta(0, 0), 0)
        self.assertEqual(a.outputs[0], 0)

    def test_add_arc(self):
        a = CanonicalMooreMachine()
        a.add_arc(0, 7, 8)
        self.assertEqual(a.max_input, 7)
        self.assertEqual(a.max_state, 8)
        self.assertEqual(a.delta(0, 7), 8)

    def test_iterate(self):
        a = CanonicalMooreMachine()
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
        a = CanonicalMooreMachine.from_string(s)
        self.assertEqual(a.max_state, 8)
        self.assertEqual(a.max_input, 2)

    def test_run(self):
        s = ("0 0 0 1 2\n"
             "1 0 0 1 2\n"
             "2 1 8 1 2")
        a = CanonicalMooreMachine.from_string(s)
        r = Run(a)
        self.assertEqual(r.state, 0)
        r.multistep([0, 0, 2, 1, 2])
        self.assertEqual(r.automaton.outputs[r.state], 1)
        d = repr(r)
        self.assertIsInstance(d, str)
        r.restart(1)
        self.assertEqual(r.automaton.outputs[r.state], 0)

    def test_mutate(self):
        random.seed(a=0, version=2)
        a = CanonicalMooreMachine()
        a.mutate()
        a.mutate()
        #a.display()
        self.assertEqual(a.max_state,2)
        self.assertEqual(a.delta(1, 0), 0)

    def test_copy(self):
        random.seed(a=0, version=2)
        m1 = CanonicalMooreMachine.from_string(("0 1 2 1\n"
         "1 0 0 2\n"
         "2 0 2 2"))
        m2 = m1.deepcopy()
        m2.mutate()
        m2.mutate()
        #m1.display()
        #m2.display()
        self.assertEqual(m2.max_state,4)
        self.assertEqual(m2.delta(0, 1), 3)
        self.assertEqual(m1.delta(0, 1), 1)

if __name__ == '__main__':
    ut.main()
