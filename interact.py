#!//usr/bin/env python

'''
Informal tools for interactive testing and general messing about with automata.
'''

import itertools
import random
import string
import semiautomata as sa
import countable
import FSMScorer
import NaidooRefLanguages as Naidoo


input_map = string.ascii_lowercase
states_map = string.ascii_uppercase
output_map = ["REJECT", "ACCEPT"]

def display(a):
    a.display(inputs=input_map, states=states_map, outputs=output_map)


# Parameters

propagator_count = 100                                           # number of individuals chosen for propagation to next generation
offspring_per_propagator = 100                                   # the number of offspring to breed from each propagator
population_size = propagator_count * offspring_per_propagator   # number of individuals in each generation
scoring_string_limit = 7                                        # score all strings shorter than this



random.seed(a=0, version=2)
automaton = sa.CanonicalMooreMachine.from_string(Naidoo.RefLanguages[0])
run = sa.Run(automaton)
comparison = automaton

print("Welcome.  Here is your starting machine.  Type ? for help.")
display(automaton)

stop = False
while not stop:
    cmd = input("> ")
    if cmd == "?":
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
        P - population - mutate the current machine into a population of 10, and score each against the Comparison machine
        V - Evolve - like P, but generates successive generations, spawning from the previous top scorer
        F - From string:  set the current machine to one read in canonical representation from user input
        L n - set the current machine to an acceptor for Naidoo's reference language n
        Any other string is fed as input to the machine and the current state's output is displayed.''')
    elif cmd == "Q":
        stop = True
    elif cmd == "R":
        run.restart()
    elif cmd == "D":
        display(automaton)
    elif cmd == "N":
        automaton = sa.CanonicalMooreMachine(1,1)
        run = sa.Run(automaton)
        display(automaton)
    elif cmd == "M":
        automaton.mutate()
        display(automaton)
    elif cmd == "E":
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
    elif cmd == "G":
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
    elif cmd == "X":
        automaton = sa.CanonicalMooreMachine.from_string(l2)
        run = sa.Run(automaton)
        display()
    elif cmd == "C":
        comparison = automaton.deepcopy()
        print("Comparison set.")
    elif cmd == "S":
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
        scorer = FSMScorer.FSMScorer.from_function(sa.Run(comparison).runstring,itertools.chain.from_iterable(countable.ND(it,comparison.max_input + 1) for it in range(scoring_string_limit)))
        print(scorer.reference_dict)
        s,optimal = scorer.score(automaton)
        print("Score: ", s, " out of a possible ", optimal)
    elif cmd == "P":
        scorer = FSMScorer.FSMScorer.from_function(sa.Run(comparison).runstring,itertools.chain.from_iterable(countable.ND(it,comparison.max_input + 1) for it in range(scoring_string_limit)))
        population = []
        for cmd in range(population_size):
            m = automaton.deepcopy()
            m.mutate()
            population.append(m)
        for m in population:
            s,optimal = scorer.score(m)
            display(m)
            print("Score:", s, "of", optimal)
    elif cmd == "V":

        scoring_strings = list(itertools.chain.from_iterable(countable.ND(it,comparison.max_input + 1) for it in range(scoring_string_limit)))
        max_score = len(scoring_strings)
        scorer = FSMScorer.FSMScorer.from_function(sa.Run(comparison).runstring,scoring_strings)

        print("Maximal score:", max_score)

        # Initialise the parent of the starting generation
        parents = [automaton]
        parent_weights = [1]

        for g in itertools.count():
            print("Generation", g)
            population = []

            # initialise the child generation
            children = []
            children_weights = []

            # add as many children of weighted-randomly-chosen parents as the population calls for
            for parent in random.choices(parents, weights=parent_weights, k=population_size):
                # reproduce the parent
                child = parent.deepcopy()

                # mutate the child
                child.mutate()

                # score the child
                (score, _) = scorer.score(child)

                # add the child to the new generation list
                children.append(child)

                # accumulate the scores into a weights list
                children_weights.append(score)

            print("Best Score:", max(children_weights))
            cmd = input("<enter> for next generation >")
            if cmd != "":
                break
            else:
                parents = children
                parent_weights = children_weights







        # # Initialise population zero from the current machine
        # propagators = [(1,automaton)]
        # for i in range(propagator_count):
        #     m = automaton.deepcopy()
        #     propagators.append((1,m))
        
        # # Loop through generations until user exits
        # for g in itertools.count():
        #     print("Generation", g)
        #     population = []

        #     # initialise the new generation from the propagators
        #     for p in propagators:
        #         population.append(p)    # the propagator survives
        #         for j in range(offspring_per_propagator - 1):
        #             # create offspring by mutation
        #             m = p.deepcopy()
        #             m.mutate()
        #             population.append(m)

        #     # score and select the next propagators
        #     # propagators = []
        #     # threshold = 0

        #     population.sort(reverse=True, key=lambda m: scorer.score(m)[0])

        #     print("Population size:", len(population))

        #     #for u in population:
        #     #    print(scorer.score(u))
        #     #    display(u)

        #     propagators = population[0:propagator_count]
        #     #propagators = [population[0]]
            
        #     print(len(propagators))

        #     print("Best Score:", scorer.score(propagators[0]))

        #     """
        #     for m in population:
        #         s,optimal = scorer.score(m)
        #         if s == optimal:
        #             print("#######################################################################Perfect score")

        #         # Threshold Free sl.    Add Update T
        #         #   0       0           0   0
        #         #   0       1           1   0
        #         #   1       0           1   1
        #         #   1       1           1   1

        #         if len(propagators) < propagator_count:
        #             # admit the individual, there is a free propagator slot
        #             propagators.append(m)
        #         elif s > threshold:
        #             propagators.append(m)
        #             propagators.sort()

        #         # Pull the threshold up if it has been exceeded
        #         if s > threshold:
        #                 threshold = s

                        


        #     best = 0
        #     for m in population:
        #         s,optimal = scorer.score(m)
        #         if s == optimal:
        #             print("#######################################################################Perfect score")
        #         if s >= best:   # use a later one of two equally scoring machines, to allow new neutral mutants to replace parents
        #             best = s
        #             propagators = m.deepcopy()
        #     print("Selected machine had score", best)
        #     """

        #     cmd = input("<enter> for next generation >")
        #     if cmd != "":
        #         break
        # automaton = propagators [0]

        # Set the current machine to be the first child that achieved the best score in the latest generation
        automaton = max(enumerate(children), key=lambda o: children_weights[o[0]])[1]
        display(automaton)
    elif cmd == "F":
        s = ""
        while True:
            line = input("state output on_0 on_1 ...:")
            if line == "":
                break
            s = s + line + "\n"
        automaton = sa.CanonicalMooreMachine.from_string(s)
        run = sa.Run(automaton)
        display(automaton)

    elif len(cmd) > 0 and cmd[0] == "L":
        n = int(cmd[1:])
        if n < 1 or n > len(Naidoo.RefLanguages):
            print("No preset machine/language numbered ", n)
        else:
            automaton = sa.CanonicalMooreMachine.from_string(Naidoo.RefLanguages[n - 1])
            run = sa.Run(automaton)
            display(automaton)
    else:
        mapped_i = map(lambda x: input_map.index(x),cmd)
        run.multistep(mapped_i)
        print("Internal State: ", states_map[run.state])
        print(output_map[run.automaton.outputs[run.state]])
