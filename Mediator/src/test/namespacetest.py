'''
Created on 12 apr. 2016

@author: brandtp
'''
import unittest
from utilities.namespaces import NSManager


class Test(unittest.TestCase):


    def setUp(self):
        testNS = {
                    'med'   : 'http://ds.tno.nl/mediator/1.0/',
                    'dc'    : 'http://purl.org/dc/elements/1.1/',
                    'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        

    def tearDown(self):
        for ns in self.nsMgr.namespaces():
            print(ns)


    def testAsClarks(self):
        assert str(self.nsMgr.asClarks('dc:creator')) == '{http://purl.org/dc/elements/1.1/}creator'
        assert str(self.nsMgr.asClarks(':align')) == '{' + self.base + '}align', 'Expected: {}, got: {}'.format('{' + self.base + '}align', str(self.nsMgr.asClarks(':align'))) 

    def testPrefix(self):
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/mediator/1.0/')
        assert pf == 'med', "Expected {}, got {}".format('med', pf)
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/polleke/1.0/')
        assert pf == 'ns_1', "Expected {}, got {}".format('ns_1', pf)
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/polleke/1.0/')
        assert pf == 'ns_1', "Expected {}, got {}".format('ns_1', pf)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testAsClarks']
    unittest.main()