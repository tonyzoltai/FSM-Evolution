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



