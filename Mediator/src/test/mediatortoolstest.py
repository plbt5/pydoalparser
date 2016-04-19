'''
Created on 19 apr. 2016

@author: brandtp
'''
import unittest
from mediator.mediatorTools import Correspondence
from utilities.namespaces import NSManager
from mediator.EDOALparser.ParseAlignment import EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST


class settersGettersTest(unittest.TestCase):


    def setUp(self):
        testNS = {
            'med'   : 'http://ds.tno.nl/mediator/1.0/',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.c = Correspondence(self.nsMgr)

    def tearDown(self):
        pass

    def testSetName(self):
        assert self.c.setName("appelepap") == self.c.getName()
    def testSetSrcEE(self):
        srcEnt = self.c.setSrcEE("mijnPf:appelepap", EDOALCLASS)
        assert srcEnt.getName() == "mijnPf:appelepap"
        srcEnt = self.c.setSrcEE("mijnPf:appelepap", EDOALRELN)
        assert srcEnt.getName() == "mijnPf:appelepap"
        srcEnt = self.c.setSrcEE("mijnPf:appelepap", EDOALPROP)
        assert srcEnt.getName() == "mijnPf:appelepap"
        srcEnt = self.c.setSrcEE("mijnPf:appelepap", EDOALINST)
        assert srcEnt.getName() == "mijnPf:appelepap"
        # Without prefix
        srcEnt = self.c.setSrcEE("appelepap", EDOALCLASS)
        assert srcEnt.getName() == "appelepap"
        srcEnt = self.c.setSrcEE("appelepap", EDOALRELN)
        assert srcEnt.getName() == "appelepap"
        srcEnt = self.c.setSrcEE("appelepap", EDOALPROP)
        assert srcEnt.getName() == "appelepap"
        srcEnt = self.c.setSrcEE("appelepap", EDOALINST)
        assert srcEnt.getName() == "appelepap"
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()