'''
Created on 19 apr. 2016

@author: brandtp
'''
import unittest
from mediator import mediatorTools as MT
from utilities.namespaces import NSManager
import inspect
import decimal


class settersGettersTest(unittest.TestCase):


    def setUp(self):
        testNS = {
            'med'   : 'http://ds.tno.nl/mediator/1.0/',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.c = MT.Correspondence(nsMgr=self.nsMgr)
        print('Testcase: {}'.format(self.__class__.__name__))

    def tearDown(self):
        pass

    def testSetName(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        # Success scenarios
        self.c.setName(name="appelepap") 
        assert self.c.getName() == "appelepap", "Assertion error, got {}".format(self.c.getName())
        self.c.setName(name="unknownPF:appelepap") 
        assert self.c.getName() == "unknownPF:appelepap", "Assertion error, got {}".format(self.c.getName())
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
        print(". done")
            
    def testEntity(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 4 + 4
        # Success scenarios
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            count+=1
            # Success scenarios, QName with prefix
            testEnt = MT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            assert testEnt.getIriRef() == self.nsMgr.asIRI("med:appelepap"), "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), self.nsMgr.asIRI("med:appelepap"))
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, QName without prefix
            testEnt = MT._Entity(entity_iri=":appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            assert testEnt.getIriRef() == self.nsMgr.asIRI(":appelepap") and testEnt.getType() == e_type
            # Success scenarios, with correct IRI
            testEnt = MT._Entity(entity_iri="http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", entity_type=e_type, nsMgr=self.nsMgr)
            assert testEnt.getIriRef() == self.nsMgr.asIRI("http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear"), "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), self.nsMgr.asIRI("http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear"))
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, with correct Clark's notation
            testEnt = MT._Entity(entity_iri="{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear", entity_type=e_type, nsMgr=self.nsMgr)
            assert testEnt.getIriRef() == "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear")
            assert testEnt.getType() == e_type, "Testfault: expected '{}', got '{}'.".format(testEnt.getType(), e_type)
        # Failure scenarios
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            count+=1
            with self.assertRaises(RuntimeError): 
                testEnt = MT._Entity(entity_iri=":^_invalidIriChar", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = MT._Entity(entity_iri=":!_invalidIriChar", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = MT._Entity(entity_iri="^_invalidIriChar", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = MT._Entity(entity_iri="", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = MT._Entity(entity_iri="unknownPF:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = MT._Entity(entity_iri="noPFOrAnythingWhatsoever", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = MT._Entity(entity_iri=12, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = MT._Entity(entity_iri=12.3, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = MT._Entity(entity_iri=True, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = MT._Entity(entity_iri=False, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = MT._Entity(entity_iri=None, entity_type=e_type, nsMgr=self.nsMgr)
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testConstruction(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 3 + 3*3 + 4 + 4
        # Mixed success and failure scenarios
        for e_type1 in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP']]:
            count+=1
            testEnt1 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type1, nsMgr=self.nsMgr)
            # Success scenario - unary operation
            constr = MT.Neg(testEnt1)
            assert constr.getType() == MT._EntityConstruction.NOTSYMBOL, "Testfault: expected '{}', got '{}'.".format(MT._EntityConstruction.NOTSYMBOL, constr.getType())
            # Binary operation scenarios
            for e_type2 in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP']]:
                testEnt2 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type2, nsMgr=self.nsMgr)
                if e_type1 == e_type2:
                    # Success scenario - binary operations
                    count+=1
                    constr = MT.Union(testEnt1, testEnt2)
                    assert constr.getType() == MT._EntityConstruction.SQRUNION, "Testfault: expected '{}', got '{}'.".format(MT._EntityConstruction.SQRUNION, constr.getType())
                    constr = MT.Intersection(testEnt1, testEnt2)
                    assert constr.getType() == MT._EntityConstruction.SQRINTSCT, "Testfault: expected '{}', got '{}'.".format(MT._EntityConstruction.SQRINTSCT, constr.getType())
                else: 
                    # Failure scenario - binary operations
                    count+=1
                    with self.assertRaises(AssertionError): 
                        constr = MT.Union(testEnt1, testEnt2)
        # Failure scenarios
        testEnt1 = MT._Entity(entity_iri="med:appelepap", entity_type=MT.ParseAlignment.EDOAL['INST'], nsMgr=self.nsMgr)
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            count+=1
            testEnt2 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                constr = MT.Union(testEnt1, testEnt2)
        testEnt2 = MT._Entity(entity_iri="med:appelepap", entity_type=MT.ParseAlignment.EDOAL['INST'], nsMgr=self.nsMgr)
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            count+=1
            testEnt1 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                constr = MT.Union(testEnt1, testEnt2)
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testSetSrcEE(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 4*4 + 3*4 + 4
        # Success scenarios; entity_expr of type _Entity
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            for test_iri in ["med:appelepap", ":appelepap", "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"]:
                count+=1
                testEnt = MT._Entity(entity_iri=test_iri, entity_type=e_type, nsMgr=self.nsMgr)
                self.c.setEE1(entity_expr=testEnt)
                assert self.c.getEE1().getExpression().getIriRef() == self.nsMgr.asIRI(test_iri), "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getIriRef(), self.nsMgr.asIRI(test_iri))
                assert self.c.getEE1().getExpression().getType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getType(), e_type)
                if e_type != MT.ParseAlignment.EDOAL['INST']:
                    count+=1
                    # Success scenarios; entity_expr of type _EntityConstruction
                    testEnt2 = MT._Entity(entity_iri="med:perenmoes", entity_type=e_type, nsMgr=self.nsMgr)
                    constr = MT.Union(testEnt, testEnt2)
                    self.c.setEE1(entity_expr=constr)
                    assert self.c.getEE1().getExpression().getType() == MT._EntityConstruction.SQRUNION, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getType(), MT._EntityConstruction.SQRUNION)
                    assert self.c.getEE1().getExpression().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getEntType(), e_type)
                    assert self.c.getEE1().getExpression().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getEntities()[0], testEnt)
                    assert self.c.getEE1().getExpression().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getEntities()[1], testEnt2)
                    constr = MT.Intersection(testEnt, testEnt2)
                    self.c.setEE1(entity_expr=constr)
                    assert self.c.getEE1().getExpression().getType() == MT._EntityConstruction.SQRINTSCT, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getType(), MT._EntityConstruction.SQRINTSCT)
                    assert self.c.getEE1().getExpression().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getEntType(), e_type)
                    assert self.c.getEE1().getExpression().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getEntities()[0], testEnt)
                    assert self.c.getEE1().getExpression().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getExpression().getEntities()[1], testEnt2)
        # Failure scenarios
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            count+=1
            with self.assertRaises(AssertionError): 
                self.c.setEE1(entity_expr="wrong type")
            with self.assertRaises(AssertionError): 
                self.c.setEE1(entity_expr=12)
            with self.assertRaises(AssertionError): 
                self.c.setEE1(entity_expr=12.3)
            with self.assertRaises(AssertionError): 
                self.c.setEE1(entity_expr=True)
            with self.assertRaises(AssertionError): 
                self.c.setEE1(entity_expr=None)
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testSetTgtEE(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 4*4 + 3*4 + 4
        # Success scenarios; entity_expr of type _Entity
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            for test_iri in ["med:appelepap", ":appelepap", "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"]:
                count+=1
                testEnt = MT._Entity(entity_iri=test_iri, entity_type=e_type, nsMgr=self.nsMgr)
                self.c.setEE2(entity_expr=testEnt)
                assert self.c.getEE2().getExpression().getIriRef() == self.nsMgr.asIRI(test_iri), "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getIriRef(), self.nsMgr.asIRI(test_iri))
                assert self.c.getEE2().getExpression().getType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getType(), e_type)
                if e_type != MT.ParseAlignment.EDOAL['INST']:
                    # Success scenarios; entity_expr of type _EntityConstruction
                    count+=1
                    testEnt2 = MT._Entity(entity_iri="med:perenmoes", entity_type=e_type, nsMgr=self.nsMgr)
                    constr = MT.Union(testEnt, testEnt2)
                    self.c.setEE2(entity_expr=constr)
                    assert self.c.getEE2().getExpression().getType() == MT._EntityConstruction.SQRUNION, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getType(), MT._EntityConstruction.SQRUNION)
                    assert self.c.getEE2().getExpression().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getEntType(), e_type)
                    assert self.c.getEE2().getExpression().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getEntities()[0], testEnt)
                    assert self.c.getEE2().getExpression().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getEntities()[1], testEnt2)
                    constr = MT.Intersection(testEnt, testEnt2)
                    self.c.setEE2(entity_expr=constr)
                    assert self.c.getEE2().getExpression().getType() == MT._EntityConstruction.SQRINTSCT, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getType(), MT._EntityConstruction.SQRINTSCT)
                    assert self.c.getEE2().getExpression().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getEntType(), e_type)
                    assert self.c.getEE2().getExpression().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getEntities()[0], testEnt)
                    assert self.c.getEE2().getExpression().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getExpression().getEntities()[1], testEnt2)
        # Failure scenarios
        for e_type in [MT.ParseAlignment.EDOAL['CLASS'], MT.ParseAlignment.EDOAL['RELN'], MT.ParseAlignment.EDOAL['PROP'], MT.ParseAlignment.EDOAL['INST']]:
            count+=1
            with self.assertRaises(AssertionError): 
                self.c.setEE2(entity_expr="wrong type")
            with self.assertRaises(AssertionError): 
                self.c.setEE2(entity_expr=12)
            with self.assertRaises(AssertionError): 
                self.c.setEE2(entity_expr=12.3)
            with self.assertRaises(AssertionError): 
                self.c.setEE2(entity_expr=True)
            with self.assertRaises(AssertionError): 
                self.c.setEE2(entity_expr=None)
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testSetCorrRelation(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 5 
        # Success scenarios
        for rel in [MT.MEDRELEQ, MT.MEDRELSUB, MT.MEDRELSUP, MT.MEDRELIN, MT.MEDRELNI]:
            count+=1
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
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testSetCorrMeasure(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 6 + 8
        # Success scenarios
        for val, tpe in [(0.01,self.nsMgr.asIRI('xsd:float')),('medium',self.nsMgr.asIRI('xsd:string')),(0.0,self.nsMgr.asIRI('xsd:double')),(1.0,self.nsMgr.asIRI('xsd:float')),(0,self.nsMgr.asIRI('xsd:decimal')),(1,self.nsMgr.asIRI('xsd:integer'))]:
            count+=1
            self.c.setCorrMeasure(measure=val, measure_type=tpe)
            assert (val, tpe) == self.c.getCorrMeasure()
        # Failure scenarios - no check exist yet for incoherence between measure and measure_type, e.g., (0.42, xsd:integer), or ('appelepap', xsd:float)
        for val, tpe in [(0.01,''),(None,self.nsMgr.asIRI('xsd:float')),(None,None),('',None),(None,''),('',''),(-0.1,self.nsMgr.asIRI('xsd:float')),(12,self.nsMgr.asIRI('xsd:integer'))]:
            count+=1
            with self.assertRaises(AssertionError): 
                self.c.setCorrMeasure(measure=val, measure_type=tpe)
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")
        

from parsertools.parsers import sparqlparser
class transformTest(unittest.TestCase):

    def setUp(self):
        testNS = {
            'med'   : 'http://ds.tno.nl/mediator/1.0/',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.c = MT.Correspondence(nsMgr=self.nsMgr)
        
        q = '''
            SELECT ?t WHERE 
                {
                    ns:TempInC ns:hasValue ?t.
                     FILTER (  ?t > 37.0  ).
                } 
        '''
        self.qt = sparqlparser.parseQuery(q)
        self.qt_filters = self.qt.searchElements(element_type=sparqlparser.GraphPatternNotTriples)
        print('Testcase: {}'.format(self.__class__.__name__))

    def tearDown(self):
        pass


    def testTransform(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        # Success scenarios
        self.c.appendTransform(operands=[sparqlparser.DECIMAL], operation=lambda x:x+1, result="c")
        tfs = self.c.getTransforms()
        for f in self.qt_filters:
            result = tfs[0](self,value_logic_node = f)
            assert len(result.searchElements(element_type = sparqlparser.DECIMAL, value = "38.0")) > 0
        # Fail scenarios
        with self.assertRaises(AssertionError): 
            result = tfs[0](self,value_logic_node = "appelepap")
        with self.assertRaises(AssertionError): 
            self.c.appendTransform(condition=lambda x:True, operands=[sparqlparser.DECIMAL, sparqlparser.DECIMAL], operation=lambda x:x+1, result="c")
        print(". done")

    def testTransformation(self):
        print('\tTesting {} ..'.format(inspect.currentframe().f_code.co_name), end="")
        from transformations import unitconversion
        
        assert 'FtoC' in dir(unitconversion)
        t = MT.Transformation(python_module='unitconversion', method_name='FtoC', operands=['32'])
        assert t != None
        assert t.getMethod() == 'FtoC'
        assert t.getModule() == unitconversion
        assert t.transform('32') == decimal.Decimal('0')
        
        assert 'CtoF' in dir(unitconversion)
        t = MT.Transformation(python_module='unitconversion', method_name='CtoF', operands=['0'])
        assert t != None
        assert t.getMethod() == 'CtoF'
        assert t.getModule() == unitconversion
        assert t.transform('0') == decimal.Decimal('32')
        
        # Fail scenarios
        with self.assertRaises(AssertionError):
            MT.Transformation(python_module='unitconversion', method_name='appelepap', operands=['32'])
        with self.assertRaises(AssertionError):
            MT.Transformation(python_module='appelepap', method_name='FtoC', operands=['32'])
        print(". done")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()