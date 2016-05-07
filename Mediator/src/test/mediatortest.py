'''
Created on 26 feb. 2016

@author: brandtp
'''
import unittest
from mediator.mediator import Mediator
from mediator.EDOALparser import ParseAlignment
from parsertools.parsers.sparqlparser import parseQuery
import warnings

import xml.etree.cElementTree as etree
from builtins import sorted

class TestMediator(unittest.TestCase):

    ns = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'xmlns': 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
        'base': 'http://oms.omwg.org/wine-vin/',
        'wine': 'http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#',
        'vin': 'http://ontology.deri.org/vin#',
        'edoal': 'http://ns.inria.org/edoal/1.0/#'
    }

    
    def setUp(self):
        pass

    def tearDown(self):
        pass
             
       
    def testMediator(self):

        with self.assertRaises(TypeError):
            Mediator(None) 
             
        with self.assertRaises(TypeError):
            Mediator("string type") 
             
        TestNSManager.makeTestFunc('EDOAL', self.testCases, info=True, debug=3)()

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testMediator']
    unittest.main()