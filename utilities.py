#!//usr/bin/env python

''''Generally useful things.'''

def pit(iterator, n = None):
    for i, j in enumerate(iterator):
        print(i, j)
        if n is not None and i >= n:
            break