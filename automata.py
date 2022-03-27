#!/usr/bin/env python
'''Automata - a re-implementation of automata from the ground up.

Classes:

    SemiAutomaton - superclass of all Automata; an iterator over the states, an iterator over the inputs, plus a transition function mapping pairs of state and input to a new state.
    FiniteSemiAutomaton - as above, but both the states and the inputs are assumed to be finite sets.
    CanonicalSemiAutomaton - a FiniteSemiAutomaton that encodes its states and its inputs as integers, and its transition function as a sparse structure.
    MooreMachine - a FiniteSemiAutomaton with a starting state and a function mapping each state to an output.
    CanonicalMooreMachine - a MooreMachine that encodes states, inputs and outputs as integers, and always starts with state 0.
    MooreMachineRun - a MooreMachine in action, with functions to feed it input and retrieve its output.

Functions:

    None.
'''

__author__ = "Gabor 'Tony' Zoltai"
__copyright__ = "Copyright 2022, Gabor Zoltai"
__credits__ = ["Gabor Zoltai"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Tony Zoltai"
__email__ = "tony.zoltai@gmail.com"
__status__ = "Prototype"



class SemiAutomaton(object):
    '''A not-quite abstract class to ground the capabilities of semiautomata, FSMs/DFAs, Moore machines, Pushdown automata, etc.'''

    def __init__(self, states={None}, input_alphabet = {None}, transition_function=lambda x, y: x) -> None:
        '''Initialises the automaton.  'states' and 'input_alphabet' should be able to be iterated without side-effects.'''
        self._states = states
        self._inputs = input_alphabet
        self._transition = transition_function

    def states(self):
        '''Returns an iterator over the set of states.'''
        return self._states
    
    def inputs(self):
        '''Returns an iterator over the set of inputs.'''
        return self._inputs
    
    def next_state(self, current_state, input_symbol):
        '''Return the result of mapping the state and input via the transition function.'''
        return self._transition(current_state, input_symbol)


class FiniteSemiAutomaton(SemiAutomaton):
    '''A subclass of SemiAutomaton with finite sets of states and inputs.'''

    def path_between(self, from_state, to_state):
        '''Return a sequence of inputs that starting from 'from_state' ends up at 'to_state', or None if this is not possible.  (Note - this is an exhaustive search.)'''

        def path_extension_to(path, visited_states, from_state, to_state):
            # return the first path found between the two states that a depth-first recursive search encounters
            if from_state == to_state:
                return (path, visited_states)
            else:
                for i, s in ((input, self.next_state(from_state, input)) for input in self.inputs()):
                    if s not in visited_states:
                        r = path_extension_to(path + [i], visited_states | {from_state}, s, to_state)
                        if r != None:
                            return r
                else:
                    # if we get here, no paths to to_state were found from the one-step successors of from_state
                    return None

        return path_extension_to([], set(), from_state, to_state)


    def reachable(self, from_state, to_state):
        '''Predicate to test for reachability.'''
        return self.path_between(from_state, to_state) != None

    def state_count(self):
        '''The number of states. (Note - this will run the states iterator all the way through, unless overridden.)'''
        return len(tuple(self.states()))
    
    def input_count(self):
        '''The number of elements in the input alphabet.'''
        return len(tuple(self.inputs()))


class CanonicalSemiAutomaton(FiniteSemiAutomaton):
    '''A kind of Machine where states and inputs are represented by integers, and transition arcs must be explicitly given.'''

    def __init__(self, state_count=1, input_count=1) -> None:
        # super().__init__(states=range(state_count), input_alphabet=range(alphabet_count), transition_function = self._canonical_table_transition)
        self._state_count = state_count
        self._input_count = input_count
        self._transition_table = {}
    
    def states(self):
        return range(self._state_count)
    
    def inputs(self):
        return range(self._input_count)
    
    def next_state(self, state, input):
        '''Implement a transition function based on an internal dictionary of dictionaries, sparse at both levels, with missing entries being self-loops.'''
        if (state, input) in self._transition_table:
            return self._transition_table[(state, input)]
        else:
            # Either the state was not found or a transition for the input from the state was not found; self-loop.
            return state
    
    def set_arc(self, from_state, on_input, to_state):
        '''Set the arc from 'from_state' on 'on_input' to go to 'to_state'.'''

        # If we are adding an arc to a state that has not previously existed, extend the state count.
        greater_state = max(from_state, to_state)
        if greater_state >= self.state_count():
            self.add_state(greater_state - self.state_count() + 1)

        if from_state == to_state:
            # making a self-loop, which is not encoded in the sparse dict
            if (from_state, on_input) in self._transition_table:
                del self._transition_table[(from_state, on_input)]
        else:
            self._transition_table[(from_state, on_input)] = to_state
    
    def add_state(self, number_of_states=1):
        '''Add new states , not connected to any others, and looping back to itself on any symbol.'''
        self._state_count += number_of_states
    
    def delete_state(self, state):
        '''Delete the given state; make it equivalent to the current highest state, then discard that state.'''
        highest_state = self._state_count - 1
        # All arcs going to the highest state should now go to the state to be deleted; all arcs leaving the latter should be copied from the highest state.
        for s in self.states():
            for i in self.inputs():
                if self.next_state(s, i) == highest_state:
                    self.set_arc(s, i, state)

        for i in self.inputs():
            self.set_arc(state, i, self.next_state(highest_state, i))
            self.set_arc(highest_state, i, highest_state)

        # finally, reduce the number of states by 1
        self._state_count -= 1

    def __repr__(self) -> str:
        '''Representation as a string.'''
        width = len(str(self._state_count))
        headings = " " * width + " | "
        for i in range(self._input_count):
            headings += f"{i:>{width}} | "
        rule = "-" * len(headings)
        r = headings + "\n" + rule + "\n"
        for s in self.states():
            r += f"{s:>{width}} | "
            for i in self.inputs():
                r += f"{self.next_state(s, i):>{width}} | "
            r += "\n"
        return r

class MooreMachine(FiniteSemiAutomaton):
    '''Moore Machines are a superclass of standard Finite State Machines / Deterministic Finite Automata, with an output alphabet not restricted to being binary. '''
    def __init__(self, states={None}, input_alphabet={None}, transition_function=lambda s, i: s, starting_state=None, output_function=lambda s: None) -> None:
        super().__init__(states, input_alphabet, transition_function)
        self._starting_state = starting_state
        self._output_function = output_function

    def starting_state(self):
        '''Return the starting state of the Moore Machine.'''
        return self._starting_state

    def output(self, state):
        '''Return the output for the specific state.'''
        return self._output_function(state)
    
    def outputs_used(self):
        '''Return the set of outputs from all states.  (Note - runs in proportional time to number of states.)'''
        return {self.output(s) for s in self.states()}

class CanonicalMooreMachine(CanonicalSemiAutomaton, MooreMachine):
    '''The canonical version of the Moore Machine has integers for outputs, and state 0 is always the starting state.'''

    def __init__(self, state_count=1, input_count=1, output_count=2) -> None:
        super().__init__(state_count, input_count)
        self._starting_state = 0
        self._output_map = dict()
        # No output function - deepcopy operations would propagate the wrong one.
        self._output_function = None
        self._output_count = output_count

    def __repr__(self) -> str:
        r = []
        for i, line in enumerate(super().__repr__().splitlines()):
            if i >= 2:
                line += str(self.output(i - 2))
            r.append(line)
        return "\n".join(r)

    
    def output_count(self):
        '''Return the output alphabet's size.'''
        return self._output_count
    
    def outputs(self):
        '''Return the set of outputs of the Moore Machine.'''
        return set(range(self.output_count()))

    def output(self, state):
        '''Return the output for a given state.'''
        # This is overridden, because deepcopy operations would go wrong if we assigned a lambda to _output_function.
        return self._output_map[state] if state in self._output_map else 0

    def set_output(self, state, output):
        '''Return the output for the specific state.'''
        if output == 0:
            if state in self._output_map:
                del self._output_map[state]
        else:
            self._output_map[state] = output
        
        # The canonical number of outputs is the highest numbered output ever set, plus one,
        # i.e. the output alphabet is from zero up to and including the highest output value.
        if output >= self._output_count:
            self._output_count = output + 1

    
    @classmethod
    def from_string(cls, s):
        '''Initialise from a multiline string.  Each line stands for a state starting with 0, and contains an output value and next states, starting from input 0.'''
        #Create the Canonical Moore Machine.
        mm = cls()
        # Split the string into lines.
        for state, line in enumerate(s.splitlines()):
            if state >= mm.state_count():
                mm.add_state()
            a = list(map(int,line.split()))
            mm.set_output(state, a[0])
            for symbol, next in enumerate(a[1:]):
                mm.set_arc(state, symbol, next)
        return mm

class MooreMachineRun(object):
    '''A Moore Machine in action.'''

    def __init__(self, machine) -> None:
        '''Initialise the running machine, and put it in its starting state.'''
        self._machine = machine
        self.reset()
    
    def reset(self):
        '''Set the running machine to its starting state.'''
        # Use the property of move_to that its default is the starting state
        self.move_to()

    def move_to(self, state=None):
        '''Go to a specific state; by default the machine's starting state.'''
        self._current_state = self._machine.starting_state() if state == None else state

    def state(self):
        '''Returns the current state of the running machine.'''
        return self._current_state

    def output(self):
        '''Returns the running machine's current output.'''
        return self._machine.output(self.state())

    def step(self, input):
        '''Feeds the input to the running machine, moving it forward by one step.'''
        self.move_to(self._machine.next_state(self.state(), input))
    
    def multistep(self, inputs):
        '''Runs the machine from its current state through the iterable providing inputs.  Note - if inputs is an endless iterable, this will not halt.'''
        for i in inputs:
            self.step(i)
    
    def transducer(self, inputs, state=None):
        '''Iterator that yields the outputs of the running machine as it consumes the input iterable.  Note - will reset the machine unless the current state is explicitly specified.'''
        self.move_to(state)
        for i in inputs:
            self.step(i)
            yield self.output()

# Unit testing code.
# Create a subclass of unittest.Testcase, with each test being a method named beginning with "test_".
# At the end, as the "main" executable code of the module, check if the name of the cu

import unittest as ut

class TestSemiAutomata(ut.TestCase):
    def test_SemiAutomaton(self):
        sa = SemiAutomaton()
        for s in sa.states():
            for i in sa.inputs():
                self.assertEqual(sa.next_state(None,"crazystring"), None)
        
        self.assertEqual(sa.next_state("boyband","girlband"), "boyband")
    
    def test_FiniteSemiAutomaton(self):
        fsa = FiniteSemiAutomaton(states=range(6), input_alphabet=[2, 4], transition_function=lambda s, i: (s + i) % 6)

        self.assertFalse(fsa.reachable(4, 1))
        self.assertEqual(fsa.path_between(1, 5), ([2, 2], {1, 3}))

        fsa = FiniteSemiAutomaton(states=range(7), input_alphabet=[2, 1], transition_function=lambda s, i: (s + i) % 6)
        self.assertFalse(fsa.path_between(0, 6), None)
        self.assertTrue(fsa.reachable(6, 1))
        self.assertEqual(fsa.state_count(), 7)

    def test_CanonicalSemiAutomaton(self):
        csa = CanonicalSemiAutomaton(1,3)

        csa.add_state()
        csa.add_state()
        csa.add_state()

        self.assertEqual(csa.state_count(), 4)
        self.assertEqual(csa.input_count(), 3)

        csa.set_arc(3, 0, 3)
        csa.set_arc(3, 1, 2)
        csa.set_arc(3, 2, 1)
        
        csa.set_arc(0, 0, 0)
        csa.set_arc(0, 1, 1)
        csa.set_arc(0, 2, 2)

        csa.delete_state(1)

        self.assertEqual(csa.next_state(0, 2), 2)
        self.assertEqual(csa.next_state(1, 2), 1)
        self.assertEqual(csa.next_state(2, 1), 2)

        csa.delete_state(2)
        self.assertEqual(csa.next_state(0, 2), 2)
        self.assertEqual(csa.next_state(1, 2), 1)
        self.assertEqual(csa.state_count(), 2)

    def test_MooreMachine(self):
        mm = MooreMachine({'A', 'B', 'C'}, {'a', 'b'}, lambda s, i: 'A' if i == 'a' else ('B' if i == 'b' else s), 'A', lambda s: ord(s))

        self.assertEqual(mm.starting_state(), 'A')
        self.assertEqual(mm.output('B'), 66)
        self.assertEqual(mm.outputs_used(), {65, 66, 67})
    
    def test_MooreRun(self):
        mm = MooreMachine({'A', 'B', 'C'}, {'a', 'b'}, lambda s, i: 'A' if i == 'a' else ('B' if i == 'b' else s), 'A', lambda s: ord(s))
        mr = MooreMachineRun(mm)

        self.assertEqual(mr.state(), 'A')

        mr.multistep("aaaab")
        self.assertEqual(mr.output(), 66)

        mr.move_to('C')
        # This transducer run purposely uses a symbol outside of the explicit input alphabet, but for which the transition function is defined anyway
        self.assertEqual(list(mr.transducer("cbca",mr.state())), [67, 66, 66, 65])

        mr.reset()
        self.assertEqual(mr.output(), 65)

    def test_CanonicalMooreMachine(self):
        cmm = CanonicalMooreMachine.from_string(("1 2 1\n"
         "0 0 2\n"
         "0 2 2\n"
         "0 8 8"))
        self.assertEqual(cmm.state_count(), 9)
        self.assertEqual(cmm.output_count(), 2)
        self.assertEqual(cmm.outputs(), {0, 1})

        cmmr = MooreMachineRun(cmm)
        self.assertEqual(list(cmmr.transducer([1, 0, 1, 0, 0, 1, 0, 1])), [0, 1, 0, 1, 0, 0, 0, 0])
        self.assertEqual(list(cmmr.transducer([])), [])

        cmm.set_output(2, 1)
        self.assertEqual(cmm.output(2), 1)




if __name__ == '__main__':
    ut.main()