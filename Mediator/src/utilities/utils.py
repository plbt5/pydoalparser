'''
Created on 19 jul. 2016

@author: brandtp
'''
import itertools


def grouper(iterable, n=2, filler=None):
    """
    Generic function to group a list, and returns an iterable over groups of N items. By default, e.g., without specifying N, it returns pairs.
    s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ...
    Remaining end elements, i.e., M < N left over items, are returned as a group of N, filled with configurable filler.
    
    source: http://stackoverflow.com/questions/5389507/iterating-over-every-two-elements-in-a-list
    """
    return itertools.zip_longest(*[iter(iterable)]*n, fillvalue=filler)
