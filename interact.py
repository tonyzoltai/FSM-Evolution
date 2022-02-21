#!//usr/bin/env python

'''
Informal tools for interactive testing and general messing about with automata.
'''

import itertools
import random
import string
import semiautomata as sa
import countable
import utilities
import FSMScorer


input_map = string.ascii_lowercase
states_map = string.ascii_uppercase
output_map = ["REJECT", "ACCEPT"]

def display(a):
    a.display(inputs=input_map, states=states_map, outputs=output_map)


l1 =   ("0 1 0 1\n"
        "1 0 1 0")
l2 =    ("0 1 2 1\n"
         "1 0 0 2\n"
         "2 0 2 2")


random.seed(a=0, version=2)
automaton = sa.CanonicalMooreMachine.from_string(l2)
run = sa.Run(automaton)
comparison = automaton

print("Welcome.  Here is your starting machine.  Type ? for help.")
display(automaton)

stop = False
while not stop:
    i = input("> ")
    if i == "?":
        print('''
        Q - quit
        R - restart current machine
        D - display current machine
        N - abandon current machine, start with a very simple model
        M - mutate the current machine, display
        E - step through all strings of the current machine's alphabet, and show the output
        G - step through all the strings the machine accepts (NOTE - may not halt!)
        X - example - load an example machine, for the regular language (ba)*
        C - set the current machine as the Comparison source for Scoring
        S - score the current machine against the Comparison machine
        Any other string is fed as input to the machine and the current state's output is displayed.''')
    elif i == "Q":
        stop = True
    elif i == "R":
        run.restart()
    elif i == "D":
        display(automaton)
    elif i == "N":
        automaton = sa.CanonicalMooreMachine(1,1)
        run = sa.Run(automaton)
        display()
    elif i == "M":
        automaton.mutate()
        display(automaton)
    elif i == "E":
        # create a generator for all strings from an alphabet, i.e. a Sigma star
        sigma_star = countable.all_words_from_alphabet(range(automaton.max_input + 1))
        for w in sigma_star:
            run.restart()
            readable_w = "".join(map(lambda c: input_map[c], w))
            print(readable_w)
            run.multistep(w)
            print(output_map[run.automaton.outputs[run.state]])
            if input("...? ") != "":
                break

        # filter that to create the set of strings in the language
        # reset the machine for each run
        # filter Sigma Start through the machine, and count the times it distinguishes the two sets correctly.
    elif i == "G":
        sigma_star = countable.all_words_from_alphabet(range(automaton.max_input + 1))
        for w in sigma_star:
            run.restart()
            run.multistep(w)
            result = output_map[run.automaton.outputs[run.state]]
            if result == "ACCEPT":
                readable_w = "".join(map(lambda c: input_map[c], w))
                print(readable_w)
                if input("...? ") != "":
                    break
    elif i == "X":
        l2 =    ("0 1 2 1\n"
                 "1 0 0 2\n"
                 "2 0 2 2")
        automaton = sa.CanonicalMooreMachine.from_string(l2)
        run = sa.Run(automaton)
        display()
    elif i == "C":
        comparison = automaton.deepcopy()
        print("Comparison set.")
    elif i == "S":
        # sigma_star = countable.all_words_from_alphabet(range(automaton.max_input + 1))
        # for w in sigma_star:
        #     if len(w) > 3:
        #         break
        #     else:
        #         run.restart()
        #         run.multistep(w)
        #         print (w, automaton.G(run.state))
        print("Comparison machine:")
        display(comparison)
        print("Machine being scored:")
        display(automaton)
        scorer = FSMScorer.FSMScorer.from_function(sa.Run(comparison).runstring,itertools.chain.from_iterable(countable.ND(it,comparison.max_input + 1) for it in range(4)))
        print(scorer.reference_dict)
        s,t = scorer.score(automaton)
        print("Score: ", s, " out of a possible ", t)
    else:
        mapped_i = map(lambda x: input_map.index(x),i)
        run.multistep(mapped_i)
        print("Internal State: ", states_map[run.state])
        print(output_map[run.automaton.outputs[run.state]])

