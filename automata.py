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



import itertools


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

    def strings_producing_output(self, o):
        '''Generates all the strings that result in a given output.  Can be used to generate the language of a DFA.'''

        # maintain a list of all the strings of a given length paired with the set of states from which they reach
        #   a state of the given output
        # for each string, if the starting state is a member of their "reaching output" set, output the string
        # To go to the next cycle, replace each string with all strings obtained by prepending an alphabet symbol,
        #   and gather the corresponding states

        # initialise the strings structure
        cur_str = ()
        string_states = {cur_str:set()}
        for state in self.states():
            if self.output(state) == o:
                string_states[cur_str].add(state)
                if state == self.starting_state():
                    yield cur_str

        # Loop conceptually forever (practically until the generator is invoked for the last time)
        while True:
            # initialise the next dict of strings and corresponding states
            new_string_states = dict()
            # Extend each string in the current dict by one preceding symbol
            for cur_str in string_states:
                # Use all symbols of the alphabet
                for symbol in self.inputs():
                    new_str = (symbol, ) + cur_str
                    new_string_states[new_str] = set()
                    # Scan all states whether they move to an in-set state on this symbol
                    for prev_state in self.states():
                        if self.next_state(prev_state,symbol) in string_states[cur_str]:
                            new_string_states[new_str].add(prev_state)
                            if prev_state == self.starting_state():
                                yield new_str
            string_states = new_string_states


        # maintain the set of strings for each reachable state that go from that state to one with the given output
        # cycle up in string lengths, extending the sets of strings
        # yield strings that have reached back to the starting state

        # suffixes_toward_output = dict()
        # suffix = ()
        # for s in self.states():
        #     if self.reachable(self.starting_state(),s):
        #         if self.output(s) == o:
        #             suffixes_toward_output[s] = [ suffix ]
        #             if s == self.starting_state():
        #                 yield suffix
        #         else:
        #             suffixes_toward_output[s] = []

        # while True:
        #     input("cycle:")
        #     for state in list(suffixes_toward_output.keys()):
        #         print("state", s)
        #         for suffix in list(suffixes_toward_output[state]):
        #             print("suffix", suffix)
        #             # Extend each string back by one symbol and assign it to the correct state, and yield it if that is the start state.
        #             for prev_state in list(suffixes_toward_output):
        #                 print("prev_state", prev_state)
        #                 for symbol in self.inputs():
        #                     print("symbol", symbol)
        #                     if self.next_state(prev_state,symbol) == state:
        #                         new_suffix = (symbol,) + suffix
        #                         suffixes_toward_output[prev_state].append(new_suffix)
        #                         if prev_state == self.starting_state():
        #                             yield new_suffix


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
    def from_strings(cls, strings):
        '''Initialise from an iterable of strings.  Each string stands for a state (starting with 0), and contains an output value and next states, starting from input 0.'''
        #Create the Canonical Moore Machine.
        mm = cls()
        for state, line in enumerate(strings):
            if state >= mm.state_count():
                mm.add_state()
            a = list(map(int,line.split()))
            mm.set_output(state, a[0])

            #if there are more symbols here than we had before, then extend the set of inputs
            if len(a) - 1 > mm.input_count():
                mm._input_count = len(a) - 1

            for symbol, next in enumerate(a[1:]):
                mm.set_arc(state, symbol, next)
        return mm


    @classmethod
    def from_string(cls, s):
        '''Initialise from a multiline string.  Each line stands for a state (starting with 0), and contains an output value and next states, starting from input 0.'''
        return cls.from_strings(s.splitlines())

    def minimised(self):
        '''Returns a newly constructed CanonicalMooreMachine that is the minimal equivalent of self.'''
        # Compile a map of the states according to their outputs as the initial potential 
        Map = [self.output(q) for q in self.states()]
        print("Map", Map)
        next_mapping = len(self.outputs_used())
        print("next mapping", next_mapping)

        # Iterate until we find no more splitting of groups
        Split = True
        while Split:
            Split = False
            print("looking for splits")
            # Go through the groups of states according to the current map
            for group in [[s for s in self.states() if Map[s] == m] for m in set(Map)]:
                print("now processing group", group)
                # Compile the signatures of the states in the group, i.e. what groups they transition to by symbol
                Subgroups = dict()
                for state in group:

                    signature = tuple([Map[self.next_state(state, symbol)] for symbol in self.inputs()])

                    # if we don't already have this in Subgroups, add it as a dict key, with the state as a value
                    if signature in Subgroups:
                        Subgroups[signature].add(state)
                    else:
                        Subgroups[signature] = {state}

                    print("state", state, "with signature", signature, "is grouped in", Subgroups[signature])
                
                # If the group has split into more than one, mark the splitting states
                Splits = list(Subgroups.values())[1:]
                if len(Splits) > 0:
                    Split = True
                    for newgroup in Splits:
                        for state in newgroup:
                            Map[state] = next_mapping
                        next_mapping += 1
                print("Map", Map)


                print("===")

        r = CanonicalMooreMachine(next_mapping, self.input_count(), self.output_count())
        processed = set()
        for state, new_state in enumerate(Map):
            if new_state not in processed:
                r.set_output(new_state, self.output(state))
                for symbol in self.inputs():
                    r.set_arc(new_state, symbol, Map[self.next_state(state, symbol)])
                processed.add(new_state)

        print(r)
        return r


        # Partition = [set([q for q in self.states() if self.output(q) == symbol]) for symbol in self.outputs()]
        # print(Partition)

        # # NextPartition will be built up by successively refining.
        # NextPartition = []

        # # Go through the groups in the partition
        # for p in Partition:
        #     # Sub-partition the group by 



        # Suppose there is a DFA D < Q, Σ, q0, δ, F > which recognizes a language L. Then the minimized DFA D < Q’, Σ, q0, δ’, F’ > can be constructed for language L as: 
        # Step 1: We will divide Q (set of states) into two sets. One set will contain all final states and other set will contain non-final states. This partition is called P0. 
        #
        # A partition is a list of sets.  There may be several sets with the same output, but we start with a partition by output.
        # we need to have a unique ID values for a set in a partition.  We also need a way to find this ID value for a given state in a given partition.

        # def part_index(state, partition):
        #     for i in range(len(partition)):
        #         if state in partition[i]:
        #             return i
        #     else:
        #         raise ValueError("State not found in partition.")

        # Partition = [set() for symbol in self.outputs()]
        # for q in self.states():
        #     Partition[self.output(q)].add(q)
        
        # print(Partition)

        # PreviousPartition = Partition
        # # Step 2: Initialize k = 1 
        # # Step 3: Find Pk by partitioning the different sets of Pk-1.

        # # In each set of Pk-1, we will take all possible pair of states. If two states of a set are distinguishable, we will split the sets into different sets in Pk.
        # for index, s in enumerate(PreviousPartition):
        #     for qi, qj in [ (qi,qj) for qi in s for qj in s if qj < qi]:
        #         print(qi, qj)
        #         # How to find whether two states in partition Pk are distinguishable ? 
        #         # Two states ( qi, qj ) are distinguishable in partition Pk if for any input symbol a, δ ( qi, a ) and δ ( qj, a ) are in different sets in partition Pk-1. 
        #         distinct = False
        #         for a in self.inputs():
        #             if part_index(self.next_state(qi, a), PreviousPartition) != part_index(self.next_state(qj, a), PreviousPartition):
        #                 # qi and qj go to groups in the partition that are already known to be different.
        #                 distinct = True
        #                 break
        #         if distinct:




        # Step 4: Stop when Pk = Pk-1 (No change in partition) 
        # Step 5: All states of one set are merged into one. No. of states in minimized DFA will be equal to no. of sets in Pk. 



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

    def test_generate_language(self):
        mm = CanonicalMooreMachine.from_string(
            (
                "0 1 1 0\n"
                "0 3 0 1\n"
                "1 0 3 0\n"
                "1 0 3 0"
            ))
        for i, s in enumerate(mm.strings_producing_output(1)):
            if i == 24:
                self.assertEqual(s, (0, 0, 0, 0, 0))
                break


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

    def test_minimise(self):
        cmm = CanonicalMooreMachine.from_string(
        ("0 1 2 3\n"
         "1 2 1 3\n"
         "1 1 2 3\n"
         "1 3 3 3\n"
         "0 3 3 3\n"
         "0 6 6 5\n"
         "1 5 5 6"))
        cmm2 = cmm.minimised()





if __name__ == '__main__':
    ut.main()