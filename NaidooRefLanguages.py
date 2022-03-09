#!/usr/bin/env python3

'''NaidooRefLanguages - CanonicalMooreMachine representations of the reference languages (or complements) from "Evolving Automata Using Genetic Programming" by Amashini Naidoo, '''


# L1    a*

L1 = ("0	0	0	1\n"
      "1	1	1	1")


# L2    (ba)*

L2 = ("0	0	2	1\n"
      "1	1	0	2\n"
      "2	1	2	2")


# L3                Any sentence without an odd number of consecutive a’s after an odd number of consecutive b’s - complement of ((a|b)*a)*b(bb)*a(aa)*(ϵ|(b(a|b)*))

L3 = ("0	0	0	1\n"    # After an even number o f b's (inc zero)'
      "1	0	2	0\n"    # After odd number of b's
      "2	1	3	4\n"    # An odd number of a's after an odd number of b's
      "3	0	2	1\n"    # An even number of a's after an odd number of b's
      "4	1	4	4")     # Definite odd # of a's after odd # of b's


# L4                Any sentence over the alphabet {a, b} without more than two consecutive a’s - complement of b*aaa(a|b)*

L4 = ("0    0     1     0\n"  # No sequence of a's seen
      "1    0     2     0\n"  # One a
      "2    0     3     0\n"  # Two consecutive a's
      "3    1     3     3")   # Three consdecutive a's


# L5                Any sentence with an even number of a’s and an even number of b’s - complement of (aa|bb|((ab|ba)(aa|bb)*(ab|ba)))*

L5 = ("0    0     1     2\n"
      "1    1     0     3\n"
      "2    1     3     0\n"
      "3    1     2     1")


RefLanguages = [L1, L2, L3, L4, L5]





# L6                Any sentence such that the number of a’s differs from the number of b’s by 0 modulo 3
# L7    a*b*a*b*
# L8    a*b
# L9    (a*+c*)b
# L10   (aa)*(bbb)*
# L11               Any sentence with an even number of a’s and an odd number of b’s
# L12   a(aa)*b
# L13               Any sentence over the alphabet {a, b} with an even number of a’s
# L14   (aa)*ba*
# L15   bc*b+ac*a

