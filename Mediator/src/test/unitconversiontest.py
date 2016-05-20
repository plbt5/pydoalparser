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
        assert unitconversion.CtoF('-273.15') == Decimal('-459.67')
        with self.assertRaises(decimal.InvalidOperation): 
            unitconversion.CtoF('appelepap')
        with self.assertRaises(AssertionError): 
            unitconversion.CtoF('-274.0')
        with self.assertRaises(AssertionError): 
            unitconversion.CtoF(Decimal('1.416834E+32'))

    def testFtoC(self):
        assert unitconversion.FtoC(32) == Decimal('0')
        assert unitconversion.FtoC(-49) == Decimal('-45')
        assert unitconversion.FtoC(113) == Decimal('45')
        assert unitconversion.FtoC(0.001) == Decimal('-17.7772222222222222222106574')
        assert unitconversion.FtoC('32') == Decimal('0')
        assert unitconversion.FtoC('-100') == unitconversion.FtoC(-100)
        assert unitconversion.FtoC('-459.67') == Decimal('-273.15')
        with self.assertRaises(decimal.InvalidOperation): 
            unitconversion.FtoC('appelepap')
        with self.assertRaises(AssertionError): 
            unitconversion.FtoC('-459.68')
        with self.assertRaises(AssertionError): 
            unitconversion.FtoC('2.5502995E+32')

    def testFCInverse(self):
        assert unitconversion.CtoF(unitconversion.FtoC('835.95')) == Decimal('835.95')
        assert unitconversion.CtoF(unitconversion.FtoC('-37.95')) == Decimal('-37.95')
        assert unitconversion.CtoF(unitconversion.FtoC('0')) == Decimal('0')
        assert unitconversion.CtoF(unitconversion.FtoC(0)) == Decimal(0)
        assert unitconversion.CtoF(unitconversion.FtoC('0')) == Decimal(0)
        
        assert unitconversion.FtoC(unitconversion.CtoF('838.95')) == Decimal('838.95')
        assert unitconversion.FtoC(unitconversion.CtoF('-33.95')) == Decimal('-33.95')
        assert unitconversion.FtoC(unitconversion.CtoF(0)) == Decimal('0')
    
    def testTempConvertor(self):
        assert unitconversion.TempConvertor(temp_value=32, src_unit='f', tgt_unit='c') == Decimal('0')
        assert unitconversion.TempConvertor(temp_value=-49, src_unit='f', tgt_unit='c') == Decimal('-45')
        assert unitconversion.TempConvertor(temp_value=0, src_unit='c', tgt_unit='f') == 32
        assert unitconversion.TempConvertor(temp_value=37, src_unit='c', tgt_unit='f') == Decimal('98.6')
        with self.assertRaises(decimal.InvalidOperation): 
            unitconversion.TempConvertor(temp_value='appelepap', src_unit='f', tgt_unit='c')
        with self.assertRaises(AssertionError): 
            unitconversion.TempConvertor(temp_value='-459.68', src_unit='f', tgt_unit='c')
        with self.assertRaises(AssertionError): 
            unitconversion.TempConvertor(temp_value=32, src_unit='f', tgt_unit='k')
        with self.assertRaises(AssertionError): 
            unitconversion.TempConvertor(temp_value=32, src_unit='k', tgt_unit='c')
        with self.assertRaises(AssertionError): 
            unitconversion.TempConvertor(src_unit='k', tgt_unit='c')
        with self.assertRaises(AssertionError): 
            unitconversion.TempConvertor(temp_value=32, tgt_unit='c')
        with self.assertRaises(AssertionError): 
            unitconversion.TempConvertor(temp_value=32, src_unit='c')
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCtoF']
    unittest.main()