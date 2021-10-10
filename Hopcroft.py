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
 
Q = set(range(6))
Sigma = set(range(2))
delta = [[1, 2], [0, 3], [4, 5], [4, 5], [4, 5], [5, 5]]
q0 = 0
F = {2, 3, 4}
 
# Initialise the partition
P = [Q, Q - F]
W = [F]
 
while len(W) > 0:
  A = W.pop()
  for c in Sigma:
    # let X be the set of states for which a transition on c leads to a state in A
    Y = []
    for fstate in Q:
        if delta[fstate][c] in A:
          Y = Y + [fstate]
    X = set(Y)
    print (c, X)
