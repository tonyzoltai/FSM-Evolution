#!//usr/bin/env python

'''
Informal tools for interactive testing and general messing about with automata.
'''

import semiautomata as sa

input_map = "abcdefghijklmnopqrstuvwxyz"
output_map = ["REJECT", "ACCEPT"]
l1 =   ("0 1 0 1\n"
        "1 0 1 0")
l2 =    ("0 1 2 1\n"
         "1 0 0 2\n"
         "2 0 2 2")

a = sa.CanonicalMooreMachine.from_string(l2)
run = sa.Run(a)

print("")
stop = False
while not stop:
    i = input("> ")
    if i == "Q":
        stop = True
    elif i == "R":
        run.restart()
    else:
        mapped_i = map(lambda x: input_map.index(x),i)
        run.multistep(mapped_i)
        print(output_map[run.automaton.outputs[run.state]])

