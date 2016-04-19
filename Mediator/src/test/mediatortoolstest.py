'''
Created on 19 apr. 2016

@author: brandtp
'''
import unittest
from mediator.mediatorTools import *
from utilities.namespaces import NSManager
from mediator.EDOALparser import ParseAlignment
from rdflib.term import _is_valid_uri, URIRef
from parsertools.parsers import sparqlparser


class settersGettersTest(unittest.TestCase):


    def setUp(self):
        testNS = {
            'med'   : 'http://ds.tno.nl/mediator/1.0/',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.c = Correspondence(nsMgr=self.nsMgr)

    def tearDown(self):
        pass

    def testSetName(self):
        # Success scenarios
        self.c.setName(name="appelepap") 
        assert self.c.getName() == "appelepap", "Assertion error, got {}".format(self.c.getName())
        self.c.setName(name="mijnPf:appelepap") 
        assert self.c.getName() == "mijnPf:appelepap", "Assertion error, got {}".format(self.c.getName())
        # Failure scenarios
        with self.assertRaises(AssertionError): 
            self.c.setName(name="")
        with self.assertRaises(AssertionError): 
            self.c.setName(name=12)
        with self.assertRaises(AssertionError): 
            self.c.setName(name=True)
        with self.assertRaises(AssertionError): 
            self.c.setName(name=False)
        with self.assertRaises(AssertionError): 
            self.c.setName(name=None)
            
    def testSetSrcEE(self):
        # Success scenarios, with prefix
        for e_type in [ParseAlignment.EDOALCLASS, ParseAlignment.EDOALRELN, ParseAlignment.EDOALPROP, ParseAlignment.EDOALINST, NSManager.RDFABOUT]:
            self.c.setSrcEE(src_entity="mijnPf:appelepap", entity_type=e_type)
            assert self.c.getSrcEE().getEntityIriRef() == "mijnPf:appelepap" and self.c.getSrcEE().getEntityType() == e_type
        # Success scenarios, without prefix
        for e_type in [ParseAlignment.EDOALCLASS, ParseAlignment.EDOALRELN, ParseAlignment.EDOALPROP, ParseAlignment.EDOALINST, NSManager.RDFABOUT]:
            self.c.setSrcEE(src_entity="appelepap", entity_type=e_type)
            assert self.c.getSrcEE().getEntityIriRef() == "appelepap" and self.c.getSrcEE().getEntityType() == e_type
        # Failure scenarios
        with self.assertRaises(AssertionError): 
            self.c.setSrcEE(src_entity="^_invalidIriChar", entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setSrcEE(src_entity=12, entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setSrcEE(src_entity=True, entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setSrcEE(src_entity=False, entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setSrcEE(src_entity=None, entity_type=ParseAlignment.EDOALCLASS)

    def testSetTgtEE(self):
        for e_type in [ParseAlignment.EDOALCLASS, ParseAlignment.EDOALRELN, ParseAlignment.EDOALPROP, ParseAlignment.EDOALINST, NSManager.RDFABOUT]:
            self.c.setTgtEE(tgt_entity="mijnPf:appelepap", entity_type=e_type)
            assert self.c.getTgtEE().getEntityIriRef() == "mijnPf:appelepap" and self.c.getTgtEE().getEntityType() == e_type
        # Without prefix
        for e_type in [ParseAlignment.EDOALCLASS, ParseAlignment.EDOALRELN, ParseAlignment.EDOALPROP, ParseAlignment.EDOALINST, NSManager.RDFABOUT]:
            self.c.setTgtEE(tgt_entity="appelepap", entity_type=e_type)
            assert self.c.getTgtEE().getEntityIriRef() == "appelepap" and self.c.getTgtEE().getEntityType() == e_type
        # Failure scenarios
        with self.assertRaises(AssertionError): 
            self.c.setTgtEE(tgt_entity="^_invalidIriChar", entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setTgtEE(tgt_entity=12, entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setTgtEE(tgt_entity=True, entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setTgtEE(tgt_entity=False, entity_type=ParseAlignment.EDOALCLASS)
        with self.assertRaises(AssertionError): 
            self.c.setTgtEE(tgt_entity=None, entity_type=ParseAlignment.EDOALCLASS)

    def testSetCorrRelation(self):
        # Success scenarios
        for rel in [MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI]:
            self.c.setCorrRelation(relation=rel)
            assert self.c.getCorrRelation() == rel
        # Failure scenarios
        with self.assertRaises(AssertionError): 
            self.c.setCorrRelation(relation=None)
        with self.assertRaises(AssertionError): 
            self.c.setCorrRelation(relation=12)
        with self.assertRaises(AssertionError): 
            self.c.setCorrRelation(relation="appelepap")
        with self.assertRaises(AssertionError): 
            self.c.setCorrRelation(relation=True)
        with self.assertRaises(AssertionError): 
            self.c.setCorrRelation(relation=False)


class transformTest(unittest.TestCase):
    from parsertools.parsers import sparqlparser
    from parsertools.base import ParseStruct

    def setUp(self):
        testNS = {
            'med'   : 'http://ds.tno.nl/mediator/1.0/',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.c = Correspondence(nsMgr=self.nsMgr)
        
        q = '''
            SELECT ?t WHERE 
                {
                    ns:TempInC ns:hasValue ?t.
                     FILTER (  ?t > 37.0  ).
                } 
        '''
        self.qt = sparqlparser.parseQuery(q)
        self.qt_filters = self.qt.searchElements(element_type=parser.GraphPatternNotTriples)

    def tearDown(self):
        pass


    def testTransform(self):
        # Success scenarios
        self.c.appendTransform(condition=lambda x:True, operands=[parser.DECIMAL], operation=lambda x:x+1, result="c")
        tfs = self.c.getTransforms()
        for f in self.qt_filters:
            result = tfs[0](self,value_logic_node = f)
            assert len(result.searchElements(element_type = parser.DECIMAL, value = "38.0")) > 0
        # Fail scenarios
        with self.assertRaises(AssertionError): 
            result = tfs[0](self,value_logic_node = "appelepap")
        with self.assertRaises(AssertionError): 
            self.c.appendTransform(condition=lambda x:True, operands=[parser.DECIMAL, parser.DECIMAL], operation=lambda x:x+1, result="c")
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()