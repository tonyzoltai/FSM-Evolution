'''
Generate iterators for countable sets.

Classes:

    ...

Functions:

    ...
'''

__author__ = "Gabor 'Tony' Zoltai"
__copyright__ = "Copyright 2021-2022, Gabor Zoltai"
__credits__ = ["Gabor Zoltai"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Gabor Zoltai"
__email__ = "tony.zoltai@gmail.com"
__status__ = "Prototype"

import itertools as it

def twoD(m):
    '''Generator for pairs of N0 numbers less than m.'''
    for x in range(m):
        for y in range(m):
            yield (x,y)

def ND(n, m):
    '''Generate all n-length lists of N0 numbers less than m.'''
    return it.product(range(m),repeat = n)

def nat_tuples():
    '''Generate all tuples of non-negative integers.'''
    return it.chain.from_iterable(map(lambda n: it.product(range(n), repeat=n),it.count()))

def all_words_from_alphabet(a):
    '''Generate all sequences of items from the given set/alphabet, which can be any iterable.'''
    return it.chain.from_iterable(map(lambda n: it.product(a, repeat=n), it.count()))

def all_concatenations_from_strings(a):
    '''Generate all concatenations of the strings yielded by iterable a.'''
    return map(lambda i: "".join(i), all_words_from_alphabet(a))

        
#gen = all_concatenations_from_strings({'a','b','c'})

#for i in it.islice(zip(it.count(), gen), 30):
#    print(i)

