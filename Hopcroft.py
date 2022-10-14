#!//usr/bin/env python

'''Tools to minimise Canonical Finite Automata. Includes Hopcroft's algorithm, 
   as well as a slower, naive method.'''

#TODO:
# - Test with two other DFAs
# - Find a case that does "add Y \ X to W"
# - Refactor as function
# - Create unit tests

#https://www.programming-hero.com/code-playground/python/index.html
#http://i.stanford.edu/pub/cstr/reports/cs/tr/71/190/CS-TR-71-190.pdf
 
# Q is he set of states
# Sigma is the input alphabet
# delta is the transition function, Q x Sigma -> Q
# q0 is he starting state
# F is the set of final states
 
# P := {F, Q \ F};
# W := {F};
# while (W is not empty) do
#     choose and remove a set A from W
#     for each c in Σ do
#          let X be the set of states for which a transition on c leads to a state in A
#          for each set Y in P for which X ∩ Y is nonempty and Y \ X is nonempty do
#               replace Y in P by the two sets X ∩ Y and Y \ X
#               if Y is in W
#                    replace Y in W by the same two sets
#               else
#                    if |X ∩ Y| <= |Y \ X|
#                         add X ∩ Y to W
#                    else
#                         add Y \ X to W
#          end;
#     end;
#end;
 
Q = frozenset(range(6))
Sigma = frozenset(range(2))
delta = [[1, 2], [0, 3], [4, 5], [4, 5], [4, 5], [5, 5]]
q0 = 0
F = frozenset({2, 3, 4})

# standard imports
import itertools as it
import string

# our imports
import semiautomata as sa
import utilities as util



#outmap = {s:0 for s in Q - F} | {s:1 for s in F}

# print(semiaut.transitions)

def old_naive_minimisation(semi_a):
  '''Minimise the partitioned canonical semiautomaton semi_a  equivalent pair states.'''
  # The main data structures are two sets of ordered pairs of states.
  # One set collects all definitely non-equivalent states.
  # The other holds those state pairs that stil may be equivalent.
  # The algorithm keeps looping through the still potentially equivalent pairs.
  # Each pair is examined whether there is at least one symbol that moves them to non-equivalent
  # states.  If so, the pair is non-equivalent.
  # The loop stops when there are no new non-equivalent pairs added.
  # Finally, the still equivalent pairs are merged.

  # Create the set of all pairs of states of the SA.

  states = range(semi_a.max_state + 1)
  pairs = set()
  for i in states:
      for j in states[i + 1:]:
        pairs.add((i,j))

  # Move every pair of states where the two sides are in different partitions into the "non-equivalent" set.
  non_equivalent = set()
  refined = False
  for i, j in list(pairs):
    # print("first loop ", i, j)
    if semi_a.G(i) != semi_a.G(j):
      # Two states having different outputs cannot be equivalent
      # print(i, j, "different output")
      non_equivalent.add((i,j))
      pairs.discard((i,j))
      refined = True

  # Repeat finding further non-equivalent states until you can't find any new ones.
  while refined:
    refined = False
    for i, j in list(pairs):
      # If any input maps the two states to states known not to be equivalent, then they are not equivalent.
      for input, next_i in semi_a.alphabet_iterate(i):
        next_j = semi_a.delta(j, input)
        p = (next_i, next_j) if next_i < next_j else (next_j, next_i)
        if p in non_equivalent:
          print(i, j, "not equivalent")
          non_equivalent.add((i,j))
          pairs.discard((i,j))
          refined = True
  
  # Construct the minimised CFA based on the set of state pairs that are equivalent.
  new_cfa = sa.CanonicalSemiAutomaton()
  


  return pairs



  #pairs = {(i,j) for  in it.product(enumerate(Q), repeat=2) if i < j}
  
def naive_minimisation(automaton):
  '''Return a minimised copy of the automaton.'''
  a = automaton.deepcopy()

  # foRM THE SET OF REACHABLE STATES
  # remove any state not in the reachable set

  # create a set of groups of states with the same output

  # for each group:
  #   
  #   for each pair of states in the group:
  #     if the two move to different groups on the same symbol, 


def Hopcroft_minimisation(Q, Sigma, delta, q0, F):
  # Initialise the partition
  P = {Q, frozenset(Q - F)}
  W = {F}
  
  while len(W) > 0:
    A = W.pop()
    print("outermost: ", A)
    for c in Sigma:
      # let X be the set of states for which a transition on c leads to a state in A
      X = frozenset({fstate for fstate in Q if delta[fstate][c] in A})
      print ("outer: ",c, X)
      # for each set Y in P for which X ∩ Y is nonempty and Y \ X is nonempty do
      for Y in P:
        inter = frozenset(X & Y)
        diff = frozenset(Y - X)
        print("   inter: ", inter, "; diff: ", diff)
        if inter != set() and diff != set():
          # replace Y in P by the two sets X ∩ Y and Y \ X  
          P = P - frozenset({Y}) | frozenset({inter, diff})
          print("   new P: ",P)
          # if Y is in W
          if Y in W:
            # replace Y in W by the same two sets
            W = W - frozenset({Y}) & frozenset({inter, diff})
          # else
          else:
            # if |X ∩ Y| <= |Y \ X|
            if len(inter) <= len(diff):
              # add X ∩ Y to W
              W = W & frozenset({inter})
            # else
            else:
              # add Y \ X to W
              W = W & frozenset({diff})
        print("inner: ", Y, W)
  print("final: ", P)
  return F


# Unit testing code
import unittest as ut

class TestHopcroft(ut.TestCase):
  def test_One(self):
    semiaut = sa.CanonicalMooreMachine()

    for state, trans in enumerate(delta):
      for input, next in enumerate(trans):
        semiaut.add_arc(state, input, next)

    for state in F:
      semiaut.outputs[state] = 1

    # util.pit(naive_minimisation(semiaut))
    old_naive_minimisation(semiaut).display(string.ascii_lowercase, string.ascii_uppercase, ["REJECT", "ACCEPT"])

  def test_Two(self):
    cfa_string = ("0 0 1 5\n"
                  "1 0 6 2\n"
                  "2 1 0 2\n"
                  "3 0 2 6\n"
                  "4 0 7 5\n"
                  "5 0 2 6\n"
                  "6 0 6 4\n"
                  "7 0 6 2\n")
    cfa = sa.CanonicalMooreMachine.from_string(cfa_string)
    # util.pit(naive_minimisation(cfa))
    old_naive_minimisation(cfa).display(string.ascii_lowercase, string.ascii_uppercase, ["REJECT", "ACCEPT"])    

if __name__ == '__main__':
  ut.main()