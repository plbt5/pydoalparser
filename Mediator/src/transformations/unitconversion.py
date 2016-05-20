'''
This is a library of transformation functions that transform values from one unit into another

Created on 6 mei 2016
@author: brandtp
'''
from decimal import Decimal

def CtoF(value = None):
    '''
    This is a lib function to convert Centigrades into Fahrenheit
    '''
    Cmin = Decimal('-273.15')
    Cmax = Decimal('1.416833000000000000000000000E+32')  # Decimal('1.416833') * Decimal('10') ** Decimal('32')
    assert value != None and value != '', "Cannot unit conversion on empty value"
    assert Decimal(value) >= Cmin and Decimal(value) <= Cmax, "Temperature must be between 0 and 1 Planck"
    return Decimal(value) * Decimal(9) / Decimal(5) + Decimal(32)

def FtoC(value = None):
    '''
    This is a lib function to convert Cantigrades into Fahrenheit
    '''
    Fmin = Decimal('-459.67')
    Fmax = Decimal('2.5502994E+32')
    assert value != None and value != '', "Cannot perform unit conversion on empty value"
    assert Decimal(value) >= Fmin and Decimal(value) <= Fmax, "Temperature must be between 0 and 1 Planck"
    return (Decimal(value) - Decimal(32)) * Decimal(5) / Decimal(9)

def TempConvertor(temp_value = None, src_unit = None, tgt_unit = None):
    '''
    This is a lib function to convert temperatures
    '''
    assert temp_value != None and temp_value != '' and isinstance(src_unit, str) and isinstance(tgt_unit, str), "Cannot unit conversion on empty value or invalid units"
    assert src_unit.lower() in ['c', 'f'], "Can only convert from Centigrades ('c') or fahrenhei('f'), got '{}'".format(src_unit)
    assert tgt_unit.lower() in ['c', 'f'], "Can only convert to Centigrades ('c') or fahrenhei('f'), got '{}'".format(tgt_unit)
    if src_unit.lower() == 'c':
        if tgt_unit.lower() == 'f': return CtoF(temp_value)
        else: return(temp_value)
    else:
        if tgt_unit.lower() == 'c': return FtoC(temp_value)
        else: return(temp_value)
        

    