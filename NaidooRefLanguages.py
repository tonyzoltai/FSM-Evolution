#!/usr/bin/env python3

'''NaidooRefLanguages - CanonicalMooreMachine representations of the reference languages (or complements) from "Evolving Automata Using Genetic Programming" by Amashini Naidoo, '''

# Language
# Number    Description (a=0, b=1, c=2)                                                Example
#-------------------------------------------------------------------------------------------------------------
# L1        a* where Σ={a,b}                                            Accepted:aaaa Rejected:aabaa
#-------------------------------------------------------------------------------------------------------------
# L2        (ba)* where Σ={a,b}                                         Accepted:bababa Rejected:babab
#-------------------------------------------------------------------------------------------------------------
# L3        any sentence without an odd number of consecutive a’s
#           after an odd number of consecutive b’s                      Accepted:aaabaabb Rejected:aaabbba
#-------------------------------------------------------------------------------------------------------------
# L4        any sentence over the alphabet {a,b} without more than two
#           consecutive a’s                                             Accepted:aabaabbbaa Rejected:babaaab
#-------------------------------------------------------------------------------------------------------------
# L5        any sentence with an even number of a’s
#           and an even number of b’s                                   Accepted:ababbaba Rejected:aababb
#-------------------------------------------------------------------------------------------------------------
# L6        any sentence such that the numberof a’s differs
#           from the number of b’s by 0 modulo 3                        Accepted:aaabbbbbb Rejected:aaaba
#-------------------------------------------------------------------------------------------------------------
# L7        a*b*a*b* where Σ={a,b}                                      Accepted:aabaaabb Rejected:aabaaba
#-------------------------------------------------------------------------------------------------------------
# L8        a*b where Σ={a,b}                                           Accepted:aaab Rejected:aabaaba
#-------------------------------------------------------------------------------------------------------------
# L9        (a*+c*)b where Σ={a,b,c}                                    Accepted:aaaab,ccb Rejected:accb
#-------------------------------------------------------------------------------------------------------------
# L10       (aa)*(bbb)* where Σ={a,b}                                   Accepted:aabbb Rejected:aabaaba
#-------------------------------------------------------------------------------------------------------------
# L11       any sentence with an even number of a’s and an odd number
#           of b’s                                                      Accepted:aabbb Rejected:aabaaba
#-------------------------------------------------------------------------------------------------------------
# L12       a(aa)*b where Σ={a,b}                                       Accepted:aaaaab Rejected:aa
#-------------------------------------------------------------------------------------------------------------
# L13       any sentence over the alphabet {a,b} with an even number
#           ofa’s                                                       Accepted:aaaabaa Rejected:aaab
#-------------------------------------------------------------------------------------------------------------
# L14       (aa)*ba*                                                    Accepted:aaaabaa Rejected:aaab
#-------------------------------------------------------------------------------------------------------------
# L15       bc*b+ac*a where Σ={a,b,c}                                   Accepted:bccb,accca Rejected:accb
#





# L1        a* where Σ={a,b}                                            Accepted:aaaa Rejected:aabaa

L1 = ("1	0	1\n"
      "0	1	1")

L1_accept = [(0,0,0,0)]
L1_reject = [(0,0,1,0,0)]


# L2        (ba)* where Σ={a,b}                                         Accepted:bababa Rejected:babab

L2 = ("1	1	2\n"
      "0    1     1\n"
      "0    0     1")

L2_accept = [(1,0,1,0,1,0)]
L2_reject = [(1,0,1,0,1)]


# L3        any sentence without an odd number of consecutive a’s
#           after an odd number of consecutive b’s                      Accepted:aaabaabb Rejected:aaabbba

L3 = ("1	0	1\n"    # Even (inc 0) consecutive b's
      "1	2	0\n"    # After odd number of b's
      "0	3	4\n"    # An odd number of a's after an odd number of b's
      "1	2	5\n"    # An even number of a's after an odd number of b's
      "0    4     4\n"    # Definite odd # of a's after odd # of b's
      "1    2     5")     # Some b's after an odd # of b's followed by an eve # of a's

L3_accept = [(0,0,0,1,0,0,1,1)]
L3_reject = [(0,0,0,1,1,1,0), (0,0,1,0,0,1,1,0,0,1,0,1,1)]


# L4        any sentence over the alphabet {a,b} without more than two
#           consecutive a’s                                             Accepted:aabaabbbaa Rejected:babaaab

L4 = ("1     1     0\n"  # No sequence of a's seen
      "1     2     0\n"  # One a
      "1     3     0\n"  # Two consecutive a's
      "0     3     3")   # Three consdecutive a's

L4_accept = [(0,0,1,0,0,1,1,1,0,0)]
L4_reject = [(1,0,1,0,0,0,1)]

# L5                Any sentence with an even number of a’s and an even number of b’s - complement of (aa|bb|((ab|ba)(aa|bb)*(ab|ba)))*
# L5        any sentence with an even number of a’s
#           and an even number of b’s                                   Accepted:ababbaba Rejected:aababb

L5 = ("1     1     2\n"  # even numbner of a's and b's
      "0     0     3\n"  # odd a's, even b's
      "0     3     0\n"  # even a's, odd b's
      "0     2     1")   # odd a's, odd b's

L5_accept = [(0,1,0,1,1,0,1,0)]

L5_reject = [(0,0,1,0,1,1)]


# L6        any sentence such that the numberof a’s differs
#           from the number of b’s by 0 modulo 3                        Accepted:aaabbbbbb Rejected:aaabab

L6 = ("1     1     2\n"       # 0: diff 0 mod 3
      "0     3     0\n"       # 1: 1 more a than b (mod 3)
      "0     0     4\n"       # 2: 1 more b then a (mod 3)
      "0     0     1\n"       # 3: 2 more a than b (mod 3)
      "0     2     0")        # 4: 2 more b than a (mod 3)

L6_accept = [ (),(0,0,0,1,1,1,1,1,1)]

L6_reject = [(0,0,0,1,0,1), (1,1,0,1), (1,), (0,)]

# L7        a*b*a*b* where Σ={a,b}                                      Accepted:aabaaabb Rejected:aabaaba

L7 = ("1    1     2\n"  # 0: empty string
      "1    1     2\n"  # 1: in first a*
      "1    3     2\n"  # 2: in first b*
      "1    3     4\n"  # 3: in second a*
      "1    5     4\n"  # 4: in second b*
      "0    5     5")   # 5: a seen after two runs of b

L7_accept = [ (0,0,1,0,0,0,1,1), (0,0,1,0) ]

L7_reject = [(0,0,1,0,0,1,0)]

# L8        a*b where Σ={a,b}                                           Accepted:aaab Rejected:aabaaba

L8 = ("0    0     1\n"  # 0: in a*
      "1    2     2\n"  # 1: b seen - must be last symbol
      "0    2     2")   # 2: anything else is rejected

L8_accept = [(0,0,0,1), (1,)]
L8_reject = [(0,0,1,0,0,1,0), (1,0)]

# L9        (a*+c*)b where Σ={a,b,c}                                    Accepted:aaaab,ccb Rejected:accb
L9 = ("0    1     2     3\n"  # 0: Decide if a+, c+ or ""
      "0    1     2     4\n"  # 1: a*
      "1    4     4     4\n"  # 2: b seen - must be the last symbol
      "0    4     2     3\n"  # 3: c*
      "0    4     4     4")   # 4: anything else is rejected

L9_accept = [(0,0,0,0,1), (2,2,1)]
L9_reject = [(0,2,2,1)]


# LX        (ab|ba|aab|bba|aaab|bbba|aaaab|bbbba|aaaaab|bbbbba)*        Accepted: abbbbba, ba Rejected: bbbbbb
LX = ("1    1     2\n"  # 0: 
      "0    3     0\n"  # 1: a seen 
      "0    0     4\n"  # 2: b seen 
      "0    5     0\n"  # 3: aa
      "0    0     6\n"  # 4: bb
      "0    7     0\n"  # 5: aaa
      "0    0     8\n"  # 6: bbb
      "0    9     0\n"  # 7: aaaa
      "0    0     10\n" # 8: bbbb
      "0    11    0\n"  # 9: aaaaa
      "0    0     11\n" # 10: bbbbb
      "0    11    11")  # 11: a^5 or b^5 seen, reject everything else 

LX_accept = [(0,1,1,1,1,1,0), (1,0)]
LX_reject = [(1,1,1,1,1,1)]


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

# Unit testing
import unittest

import automata

class TestRefLangs(unittest.TestCase):
      def test_L1(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L1))
            for i in L1_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L1_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def test_L2(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L2))
            for i in L2_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L2_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def test_L3(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L3))
            for i in L3_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L3_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)


      def test_L4(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L4))
            for i in L4_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L4_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def test_L5(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L5))
            for i in L5_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L5_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def test_L6(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L6))
            for i in L6_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L6_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def test_L7(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L7))
            for i in L7_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L7_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def test_L8(self):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(L8))
            for i in L8_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in L8_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def LNtest(self, LN, LN_accept, LN_reject):
            mr = automata.MooreMachineRun(automata.CanonicalMooreMachine.from_string(LN))
            for i in LN_accept:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 1)
            for i in LN_reject:
                  mr.reset()
                  mr.multistep(i)
                  self.assertEqual(mr.output(), 0)

      def test_L9(self):
            self.LNtest(L9, L9_accept, L9_reject)

      def test_LX(self):
            self.LNtest(LX, LX_accept, LX_reject)

if __name__ == "__main__":
      unittest.main()