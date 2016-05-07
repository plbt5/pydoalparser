'''
This is a library of transformation functions that transform values from one unit into another

Created on 6 mei 2016
@author: brandtp
'''
from decimal import Decimal

def CtoF(value = None):
    '''
    This is a lib function to convert Cantigrades into Fahrenheit
    '''
    assert value != None and value != '', "Cannot unit conversion on empty value"
    return Decimal(value) * Decimal(9) / Decimal(5) + Decimal(32)

def FtoC(value = None):
    '''
    This is a lib function to convert Cantigrades into Fahrenheit
    '''
    assert value != None and value != '', "Cannot unit conversion on empty value"
    return (Decimal(value) - Decimal(32)) * Decimal(5) / Decimal(9)


    
        