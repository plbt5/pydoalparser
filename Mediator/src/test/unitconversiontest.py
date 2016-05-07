'''
Created on 6 mei 2016

@author: brandtp
'''
import unittest
from transformations import unitconversion
from decimal import Decimal
import decimal
import os.path

class Test(unittest.TestCase):


    def testCtoF(self):
        assert unitconversion.CtoF(0) == 32
        assert unitconversion.CtoF(37) == Decimal('98.6')
        assert unitconversion.CtoF(Decimal(-32)*Decimal(5)/Decimal(9)) == Decimal('0')
        assert unitconversion.CtoF(-50) == Decimal('-58')
        assert unitconversion.CtoF('0.001') == Decimal('32.0018')
        assert unitconversion.CtoF('1') == unitconversion.CtoF(1)
        assert unitconversion.CtoF('-100') == unitconversion.CtoF(-100)
        with self.assertRaises(decimal.InvalidOperation): 
            unitconversion.CtoF('appelepap')

    def testFtoC(self):
        assert unitconversion.FtoC(32) == Decimal('0')
        assert unitconversion.FtoC(-49) == Decimal('-45')
        assert unitconversion.FtoC(113) == Decimal('45')
        assert unitconversion.FtoC(0.001) == Decimal('-17.7772222222222222222106574')
        assert unitconversion.FtoC('32') == Decimal('0')
        assert unitconversion.FtoC('-100') == unitconversion.FtoC(-100)
        with self.assertRaises(decimal.InvalidOperation): 
            unitconversion.FtoC('appelepap')

    def testFCInverse(self):
        assert unitconversion.CtoF(unitconversion.FtoC('835.95')) == Decimal('835.95')
        assert unitconversion.CtoF(unitconversion.FtoC('-837.95')) == Decimal('-837.95')
        assert unitconversion.CtoF(unitconversion.FtoC('0')) == Decimal('0')
        assert unitconversion.CtoF(unitconversion.FtoC(0)) == Decimal(0)
        assert unitconversion.CtoF(unitconversion.FtoC('0')) == Decimal(0)
        
        assert unitconversion.FtoC(unitconversion.CtoF('838.95')) == Decimal('838.95')
        assert unitconversion.FtoC(unitconversion.CtoF('-833.95')) == Decimal('-833.95')
        assert unitconversion.FtoC(unitconversion.CtoF(0)) == Decimal('0')
    
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCtoF']
    unittest.main()