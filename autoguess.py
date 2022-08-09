#!/usr/bin/env python3
'''autoguess - automata in guessing games (outputs to predict next input)

Classes:

    AutomatonGuessing - allows automata to play a guessing game and tallies their scores

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


from copy import deepcopy
import automata

class AutomatonGuessing(object):
    '''allows automata to play a guessing game and tallies their scores'''
    def __init__(self, automaton: automata.MooreMachineRun, input_function) -> None:
        self.automaton = automaton
        self.input_function = input_function
    
    def cycles(self):
        '''Generator of booleans for the cycles of the game (true means the target it matched, false means not)'''
        while True:
            # Get the current prediction of the automaton
            prediction = self.automaton.output()
            # Get the input it was trying to predict
            predictand = self.input_function()
            # Cycle the automaton
            self.automaton.step(predictand)
            # Check if they are equal
            yield predictand == prediction


def cooperative (mmrA: automata.MooreMachineRun, mmrB: automata.MooreMachineRun, max_rounds):
    '''Run a cooperative game between two instances of MooreMachineRun.'''
    next_in_for_A = mmrB.output()
    next_in_for_B = mmrA.output()

    scoreA = 0
    scoreB = 0

    finished = False
    round = 0

    while not finished:
        # Update scores.  Both score if they match the other's output, not if they don't.
        if mmrA.output() == next_in_for_A:
            scoreA += 1
        if mmrB.output() == next_in_for_B:
            scoreB += 1

        print("Round", round)
        print("MmrA state", mmrA.state(), "predict", mmrA.output(), "in", next_in_for_A, scoreA)
        print("MmrB state", mmrB.state(), "predict", mmrB.output(), "in", next_in_for_B, scoreB)
        
        # Determine if finished
        round += 1
        finished = (round == max_rounds)

        if not finished:
            mmrA.step(next_in_for_A)
            mmrB.step(next_in_for_B)
            next_in_for_A = mmrB.output()
            next_in_for_B = mmrA.output()

    return (scoreA, scoreB)



# Mark 2.  Works, but perhaps simpler to implement WITHOUT the generators, see Mark 3.
def cooperative(mmr1: automata.MooreMachineRun, mmr2: automata.MooreMachineRun, rounds):
    '''Run a cooperative game between two instances of MooreMachineRun.'''

    ag1c = AutomatonGuessing(mmr1,lambda: input_for_mmr1).cycles
    ag2c = AutomatonGuessing(mmr2, lambda: input_for_mmr2).cycles

    counter = 0

    score1 = 0
    score2 = 0

    input_for_mmr1 = mmr2.output()
    input_for_mmr2 = mmr1.output()

    for m1, m2 in zip(ag1c(), ag2c()):
        print("Round", counter)
        print("Ag1 state", mmr1.state(), "predict", mmr1.output(), "in", input_for_mmr1, m1)
        print("Ag2 state", mmr2.state(), "predict", mmr2.output(), "in", input_for_mmr2, m2)
        if m1:
            score1 += 1
        if m2:
            score2 += 1
        # get the next two outputs for inputs
        input_for_mmr1 = mmr2.output()
        input_for_mmr2 = mmr1.output()

        counter += 1
        if counter == rounds:
            break
    return (score1, score2)


# Mark 3 - without generators.  This works.       
# def competitive(mmr1: automata.MooreMachineRun, mmr2: automata.MooreMachineRun, rounds):
#     '''Run a cooperative game between two instances of MooreMachineRun.'''

#     ag1c = AutomatonGuessing(mmr1,lambda: input_for_mmr1).cycles
#     ag2c = AutomatonGuessing(mmr2, lambda: input_for_mmr2).cycles

#     counter = 0

#     score1 = 0
#     score2 = 0

#     input_for_mmr1 = mmr2.output()
#     input_for_mmr2 = mmr1.output()

#     for m1, m2 in zip(ag1c(), ag2c()):
#         if m1:
#             score1 += 1
#         if not m2:
#             score2 += 1
#         # get the next two outputs for inputs
#         input_for_mmr1 = mmr2.output()
#         input_for_mmr2 = mmr1.output()

#         counter += 1
#         if counter == rounds:
#             break
#     return (score1, score2)




# THIS CLASS COMMENTED OUT AS *PROBABLY* USELESS
# class MultiGuess(object):
#     '''Plays the guessing game with several running automata, some of which can be trying to guess each other's output.'''
#     def __init__(self, score_start_condition, end_condition, *runs_and_inputs) -> None:
#         '''Accepts conditions to start scoring and to end the game; the players are automata runs and input functions, in pairs.'''
#         self.score_start_condition = score_start_condition
#         self.end_condition = end_condition
#         # "guessers" is a list of objects that have a "cycles" iterator
#         self.guessers = []
#         for r, f in runs_and_inputs:
#             self.guessers.append(AutomatonGuessing(r, f))


#     def cycles(self):
#         '''Yields the scores of the automata in the guessing game, for each cycle thereof.'''
#         scores = [0] * len(self.guessers)
#         scoring = False

#         while not self.end_condition():
#             # "matches" is a list of booleans delivered by the "cycles" generators of 
#             for [*matches] in zip(*(g.cycles() for g in self.guessers)):
#                 # matches now has the booleans returned by all guessers
#                 if self.score_start_condition():
#                     # score commencement condition has been met, we score from here forward
#                     scoring = True
    
#                 if scoring:
#                     for i in range(len(scores)):
#                         if matches[i]:
#                             scores[i] += 1
#             yield scores
    

# Unit testing code.
# Create a subclass of unittest.Testcase, with each test being a method named beginning with "test_".
# At the end, as the executable code of the module, check if the name of the current module is "__main__", i.e. if this the top invocation.
# If so, run the unit tests via unittest.main().

import unittest as ut

class TestAutoGuess(ut.TestCase):
    
    def test_ag_cycles(self):
        # Test by guessing every third symbol to be 1.
        auto = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_strings(
            [
                "1 1 1",
                "0 2 2",
                "0 0 0"
            ]
        ))

        sequence = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
        # guesses:  0  0  1  0  0  1  0  0  1  0  0  1  0  0  1  0  0  1
        # matches:  ^           ^  ^  ^           ^  ^  ^           ^  ^
        # score should be 9

        index = 0
                
        guesser = AutomatonGuessing(auto, lambda: sequence[index])

        score = 0

        for b in guesser.cycles():
            if b:
                score += 1
            index += 1
            if index == len(sequence):
                break

        self.assertEqual(score, 9)


    def test_coop(self):

        # Test two identical machines for 10 iterations - they should both score 10
        mmr1 = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_strings(
            [
                "0 1 1",
                "0 2 2",
                "1 0 0"
            ]
        ))
        mmr2 = deepcopy(mmr1)
        self.assertEqual(mmr1.state(), mmr2.state())
        self.assertIsNot(mmr1, mmr2)

        x, y = cooperative(mmr1, mmr2, 10)

        self.assertEqual(x, 10)
        self.assertEqual(y, 10)

        # Test non-identical machines.  The second always predicts a the repetition of the last symbol.
        mmr1.reset()

        mmr2 = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_strings(
            [
                "0 0 1",
                "1 0 1"
            ]
        ))

        x, y = cooperative(mmr1, mmr2, 10)

        self.assertEqual(x, 4)
        self.assertEqual(y, 4)

        # Test with an always-zero machine and the repeat predictor.

    # def test_comp(self):
    #     # Test two  machines for 10 iterations
    #     mmr1 = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_strings(
    #         [
    #             "0 1 1",
    #             "0 2 2",
    #             "1 0 0"
    #         ]
    #     ))
    #     mmr2 = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_strings(
    #         [
    #             "0 1 1",
    #             "1 0 0"
    #         ]
    #     ))
    #     self.assertEqual(mmr1.state(), mmr2.state())
    #     self.assertIsNot(mmr1, mmr2)

    #     x, y = competitive(mmr1, mmr2, 10)

    #     self.assertEqual(x, 4)
    #     self.assertEqual(y, 4)
        





if __name__ == "__main__":
    ut.main()