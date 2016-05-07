'''
Created on 29 apr. 2016

@author: brandtp
'''
import unittest
from test.mytestexceptions import TestException
from parsertools.base import ParseStruct
from parsertools.parsers.sparqlparser import parser, parseQuery

class TestQPTripleRefs(unittest.TestCase):


    def setUp(self):
        self.testCases = {}
        self.testCases['ADMIN'] = []
        self.testCases['ADMIN'].append(
            { 
            'pass': {
                'resources/alignPassSimple0.xml': {
                    ''
                    }
                },
             'fail': {}

        pass


    def tearDown(self):
        pass


    def testQPTripleRefs(self):
        self.about = ''      # (ParseInfo) the atomic node in the sparql tree representing the node
        self.type = ''       # (String) the Basic Graph Pattern position of the node: <S|P|O>
        self.binds = []      # (String) a list of names of two (BGPType=p) or one (=s or =o) Vars that are bound by this node: <VAR1 | VAR2 | PNAME_LN>
        self.associates = {} # (Dict(uri, ParseInfo)) the (s,p,o) triple, each element being a QPNodeother two qpNodes in the triple

        rq = parseQuery(data)
        srcNodes = rq.searchElements(element_type=entity_type, value=src_qname)
        if srcNodes == []: 
            raise TestException("Cannot find element <{}> of type {} in sparqlData".format(src_qname, entity_type))

        for qrySrcNode in srcNodes: 
            qpt = self.QueryPatternTripleAssociation(entity_expression=entity_expression, sparql_tree=self.parsedQuery, nsMgr=self.nsMgr)
            qpt.addQPTRef(qrySrcNode)
            self.qpTriples.append(qpt)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testQPTripleRefs']
    unittest.main()