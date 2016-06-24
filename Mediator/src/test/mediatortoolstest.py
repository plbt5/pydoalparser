'''
Created on 19 apr. 2016

@author: brandtp
'''
import unittest
from mediator import mediatorTools as MT
from utilities.namespaces import NSManager
import inspect
import decimal
from test.mytestexceptions import TestException


class correspondenceTest(unittest.TestCase):


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
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        # Success scenarios
        self.c.setName(name="appelepap") 
        assert self.c.getName() == "appelepap", "Assertion error, got {}".format(self.c.getName())
        self.c.setName(name="unknownPF:appelepap") 
        assert self.c.getName() == "unknownPF:appelepap", "Assertion error, got {}".format(self.c.getName())
        print(".", end="")
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
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 4 + 4
        # Success scenarios
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
            count+=1
            # Success scenarios, QName with prefix
            testEnt = MT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://ds.tno.nl/mediator/1.0/appelepap>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, QName without prefix
            testEnt = MT._Entity(entity_iri=":appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<" + self.base + "appelepap>"
            assert testEnt.getIriRef() == exp_iri and testEnt.getType() == e_type
            # Success scenarios, with correct IRI
            testEnt = MT._Entity(entity_iri="http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, with correct <IRI>
            testEnt = MT._Entity(entity_iri="<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, with correct Clark's notation
            testEnt = MT._Entity(entity_iri="{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: expected '{}', got '{}'.".format(testEnt.getType(), e_type)
            print(".", end="")
        # Failure scenarios
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
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
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testConstruction(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 3 + 3*3 + 4 + 4
        # Mixed success and failure scenarios
        for e_type1 in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP']]:
            count+=1
            testEnt1 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type1, nsMgr=self.nsMgr)
            # Success scenario - unary operation
            constr = MT.Neg(testEnt1)
            assert constr.getCType() == MT._EntityConstruction.NOTSYMBOL, "Testfault: expected '{}', got '{}'.".format(MT._EntityConstruction.NOTSYMBOL, constr.getCType())
            print(".", end="")
            # Binary operation scenarios
            for e_type2 in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP']]:
                testEnt2 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type2, nsMgr=self.nsMgr)
                if e_type1 == e_type2:
                    # Success scenario - binary operations
                    count+=1
                    constr = MT.Union(testEnt1, testEnt2)
                    assert constr.getCType() == MT._EntityConstruction.SQRUNION, "Testfault: expected '{}', got '{}'.".format(MT._EntityConstruction.SQRUNION, constr.getCType())
                    constr = MT.Intersection(testEnt1, testEnt2)
                    assert constr.getCType() == MT._EntityConstruction.SQRINTSCT, "Testfault: expected '{}', got '{}'.".format(MT._EntityConstruction.SQRINTSCT, constr.getCType())
                    print(".", end="")
                else: 
                    # Failure scenario - binary operations
                    count+=1
                    with self.assertRaises(AssertionError): 
                        constr = MT.Union(testEnt1, testEnt2)
                    print(".", end="")
        # Failure scenarios
        testEnt1 = MT._Entity(entity_iri="med:appelepap", entity_type=MT.Alignment.EDOAL['INST'], nsMgr=self.nsMgr)
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
            count+=1
            testEnt2 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                constr = MT.Union(testEnt1, testEnt2)
            print(".", end="")
        testEnt2 = MT._Entity(entity_iri="med:appelepap", entity_type=MT.Alignment.EDOAL['INST'], nsMgr=self.nsMgr)
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
            count+=1
            testEnt1 = MT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                constr = MT.Union(testEnt1, testEnt2)
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testSetSrcEE(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 4*4 + 3*4 + 4
        # Success scenarios; entity_expr of type _Entity
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
            for test_iri in ["med:appelepap", ":appelepap", "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"]:
                count+=1
                testEnt = MT._Entity(entity_iri=test_iri, entity_type=e_type, nsMgr=self.nsMgr)
                self.c.setEE1(entity_expr=testEnt)
                assert self.c.getEE1().getIriRef() == self.nsMgr.asIRI(test_iri), "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getIriRef(), self.nsMgr.asIRI(test_iri))
                assert self.c.getEE1().getType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getType(), e_type)
                print(".", end="")
                if e_type != MT.Alignment.EDOAL['INST']:
                    count+=1
                    # Success scenarios; entity_expr of type _EntityConstruction
                    testEnt2 = MT._Entity(entity_iri="med:perenmoes", entity_type=e_type, nsMgr=self.nsMgr)
                    constr = MT.Union(testEnt, testEnt2)
                    self.c.setEE1(entity_expr=constr)
                    assert self.c.getEE1().getCType() == MT._EntityConstruction.SQRUNION, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getCType(), MT._EntityConstruction.SQRUNION)
                    assert self.c.getEE1().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntType(), e_type)
                    assert self.c.getEE1().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[0], testEnt)
                    assert self.c.getEE1().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[1], testEnt2)
                    constr = MT.Intersection(testEnt, testEnt2)
                    self.c.setEE1(entity_expr=constr)
                    assert self.c.getEE1().getCType() == MT._EntityConstruction.SQRINTSCT, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getCType(), MT._EntityConstruction.SQRINTSCT)
                    assert self.c.getEE1().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntType(), e_type)
                    assert self.c.getEE1().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[0], testEnt)
                    assert self.c.getEE1().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[1], testEnt2)
                    print(".", end="")
        # Failure scenarios
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
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
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testSetTgtEE(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 4*4 + 3*4 + 4
        # Success scenarios; entity_expr of type _Entity
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
            for test_iri in ["med:appelepap", ":appelepap", "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"]:
                count+=1
                testEnt = MT._Entity(entity_iri=test_iri, entity_type=e_type, nsMgr=self.nsMgr)
                self.c.setEE2(entity_expr=testEnt)
                assert self.c.getEE2().getIriRef() == self.nsMgr.asIRI(test_iri), "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getIriRef(), self.nsMgr.asIRI(test_iri))
                assert self.c.getEE2().getType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getType(), e_type)
                print(".", end="")
                if e_type != MT.Alignment.EDOAL['INST']:
                    # Success scenarios; entity_expr of type _EntityConstruction
                    count+=1
                    testEnt2 = MT._Entity(entity_iri="med:perenmoes", entity_type=e_type, nsMgr=self.nsMgr)
                    constr = MT.Union(testEnt, testEnt2)
                    self.c.setEE2(entity_expr=constr)
                    assert self.c.getEE2().getCType() == MT._EntityConstruction.SQRUNION, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getCType(), MT._EntityConstruction.SQRUNION)
                    assert self.c.getEE2().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntType(), e_type)
                    assert self.c.getEE2().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[0], testEnt)
                    assert self.c.getEE2().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[1], testEnt2)
                    constr = MT.Intersection(testEnt, testEnt2)
                    self.c.setEE2(entity_expr=constr)
                    assert self.c.getEE2().getCType() == MT._EntityConstruction.SQRINTSCT, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getCType(), MT._EntityConstruction.SQRINTSCT)
                    assert self.c.getEE2().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntType(), e_type)
                    assert self.c.getEE2().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[0], testEnt)
                    assert self.c.getEE2().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[1], testEnt2)
                    print(".", end="")
        # Failure scenarios
        for e_type in [MT.Alignment.EDOAL['CLASS'], MT.Alignment.EDOAL['RELN'], MT.Alignment.EDOAL['PROP'], MT.Alignment.EDOAL['INST']]:
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
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")

    def testSetCorrRelation(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 5 
        # Success scenarios
        for rel in [MT.MEDRELEQ, MT.MEDRELSUB, MT.MEDRELSUP, MT.MEDRELIN, MT.MEDRELNI]:
            count+=1
            self.c.setCorrRelation(relation=rel)
            assert self.c.getCorrRelation() == rel
            print(".", end="")
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
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N= 6 + 8
        # Success scenarios
        for val, tpe in [(0.01,self.nsMgr.asIRI('xsd:float')),('medium',self.nsMgr.asIRI('xsd:string')),(0.0,self.nsMgr.asIRI('xsd:double')),(1.0,self.nsMgr.asIRI('xsd:float')),(0,self.nsMgr.asIRI('xsd:decimal')),(1,self.nsMgr.asIRI('xsd:integer'))]:
            count+=1
            self.c.setCorrMeasure(measure=val, measure_type=tpe)
            assert (val, tpe) == self.c.getCorrMeasure()
            print(".", end="")
        # Failure scenarios - no check exist yet for incoherence between measure and measure_type, e.g., (0.42, xsd:integer), or ('appelepap', xsd:float)
        for val, tpe in [(0.01,''),(None,self.nsMgr.asIRI('xsd:float')),(None,None),('',None),(None,''),('',''),(-0.1,self.nsMgr.asIRI('xsd:float')),(12,self.nsMgr.asIRI('xsd:integer'))]:
            count+=1
            with self.assertRaises(AssertionError): 
                self.c.setCorrMeasure(measure=val, measure_type=tpe)
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N,count)
        print(". done")
        
class pathTest(unittest.TestCase):

    def setUp(self):
        testNS = {
            'med'   : 'http://ts.tno.nl/mediator/1.0/',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.path = MT.Path()
        self.property = MT.EProperty(entity_iri='med:testProperty', nsMgr=self.nsMgr)
        self.relations = [MT.ERelation(entity_iri='med:testRel1', nsMgr=self.nsMgr), MT.ERelation(entity_iri='med:testRel2', nsMgr=self.nsMgr), MT.ERelation(entity_iri='med:testRel3', nsMgr=self.nsMgr)]
        print('Testcase: {}'.format(self.__class__.__name__))

    def tearDown(self):
        pass
    
    def testPath(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        # PASS test
        for r in self.relations:
            self.path.append(r)
        self.path.append(self.property)
        for path,crit in zip(self.path, self.relations):
            assert path == crit
            print(".", end="")
        assert self.path[-1] == self.property
        print(".", end="")
        
        # FAIL tests
        with self.assertRaises(AssertionError): 
            self.path.append("42")
        print(".", end="")
        with self.assertRaises(AssertionError): 
            self.path.append(self.property)
        print(".", end="")
        with self.assertRaises(AssertionError): 
            self.path.append(self.relations[1])
        print(". done")
    
    
from parsertools.parsers import sparqlparser
from mediator import EDOALparser
class transformTest(unittest.TestCase):

    def setUp(self):
        testNS = {
            'med'   : 'http://ts.tno.nl/mediator/1.0/',
            't'     : 'http://ts.tno.nl/mediator/test#',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'ne'    : 'http://ts.tno.nl/mediator/1.0/examples/NonExistent/',
            'oa'    : 'http://tutorial.topbraid.com/ontoA/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.c = MT.Correspondence(nsMgr=self.nsMgr)
        self.operands = []
        
        
        q = '''
            PREFIX    oa:    <http://tutorial.topbraid.com/ontoA/>
            SELECT ?t WHERE 
                {
                    oa:Patient oa:hasTemp ?t.
                     FILTER (  ?t > 37.0  ).
                } 
        '''
        self.testCases = {}
        
        '''
        The Transform tests will validate:
        * testTransformation: the creation of a transformation specification
        * testMakeTransform:  the transition from the name of an operation to a callable function
        * testTransform:      the transition from the specification of the operands to the inclusion of the correct values in the operation
        '''
        

        self.testCases['TRANSFORM'] = []
        self.testCases['TRANSFORM'].append(
            {
            'pass': {
                # 
                'resources/transformSimplePass1.xml': {
                    'transformPass1': {
                        'test_entity_iri': 'oa:hasTemp',
                        'sparql_var_name': '?t',
                        'result': decimal.Decimal('98.6')
                        },
                    'transformPass2': {
                        'test_entity_iri': 'oa:hasTemp',
                        'sparql_var_name': '?t',
                        'result': decimal.Decimal('98.6')
                        }
                    }
                },
            'fail': {
                # 
                'resources/valueSimpleFail1.xml': { 
                    'FailRelation3': AssertionError         # Valid attribute, invalid element (element is not empty) 
                    },
                'resources/valuePathFail1.xml': { 
                    'FailComplexPathNotImpl'  : NotImplementedError    # Correct path, but too complex to be implemented yet
                    }
                }
            } 
        )

        self.qt = sparqlparser.parseQuery(q)
        self.qt_filters = self.qt.searchElements(label="constraint")
        if self.qt_filters == None or self.qt_filters == [] or self.qt_filters[0] == None: raise TestException("Need to have test data before testing can begin")
        
        alignFile = "resources/alignPassTransformation1.xml"
        self.align = EDOALparser.Alignment(alignFile, self.nsMgr)
        if self.align == None: raise TestException("Cannot find an alignment in file '{}'".format(alignFile))
        self.corrs = self.align._align.findall(str(self.nsMgr.asClarks(':map')) + '/' + str(self.nsMgr.asClarks(':Cell')))
        if self.corrs == None or self.corrs == []: raise TestException("Cannot find <map><Cell> elements in file '{}'".format(alignFile))
        self.Transformations = []
        
        for corr in self.corrs:
            TransformationElmnts = corr.findall(str(self.nsMgr.asClarks('edoal:transformation')) + '/' + str(self.nsMgr.asClarks('edoal:Transformation')))
            if TransformationElmnts == None or TransformationElmnts == []: raise TestException("Cannot find <transformation><Transformation> elements in file '{}'".format(alignFile))
            self.Transformations += TransformationElmnts
            
        print('Testcase: {}'.format(self.__class__.__name__))

    def tearDown(self):
        pass
    

    def testTransformation(self):
        # Test the connection to, and correct execution of, a predefined python method
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        from transformations import unitconversion
        # setup specifics
        oneOperands = []
        t = self.Transformations[0]
        operandEl=t.find(str(self.nsMgr.asClarks('edoal:entity1')))
        if operandEl == None: raise TestException("Cannot find <edoal:entity1> element in <edoal:Transformation> ")
        oneOperands.append(self.align.Value(el=operandEl, parse_alignment=self.align))
        
        twoOperands = []
        operandEl=t.find(str(self.nsMgr.asClarks('edoal:entity2'))+'/'+ str(self.nsMgr.asClarks('edoal:Apply'))+'/'+ str(self.nsMgr.asClarks('edoal:arguments')))
        if operandEl == None: raise TestException("Cannot find <edoal:entity2><edoal:Apply><edoal:arguments> element in <edoal:Transformation> ")
        for value_el in operandEl.iter():
            if value_el.tag == self.nsMgr.asClarks('edoal:Literal'):
                twoOperands.append(self.align.Value(el=value_el, parse_alignment=self.align))

        # PASS tests
        # First test: init a complete transformation
        assert 'FtoC' in dir(unitconversion)
        t = MT.Transformation(python_module='unitconversion', method_name='FtoC', operands=oneOperands)
        assert t != None, "Failed to make a Transformation"
        print(".", end="")
        assert t.getLocalMethod()[1] == 'FtoC', "Expected {}, got {}".format('FtoC', t.getLocalMethod()[1])
        print(".", end="")
        assert t.getLocalMethod()[0].__name__ == 'transformations.unitconversion', "Expected {}, got {}".format('transformations.unitconversion', t.getLocalMethod()[0].__name__)
        print(".", end="")
        assert t._operands == oneOperands, "Failed to register operands: expected {}, got {}".format(oneOperands, t._operands)
        print(".", end="")
        args = '32'
        assert t.getOperationResult(args) == decimal.Decimal('0'), "Expected {} as transformation result, got {}".format(decimal.Decimal('0'), t.getOperationResult(value=args))
        print(".", end="")
        
        # Second test: init an empty transformation, and add the elements
        assert 'CtoF' in dir(unitconversion)
        t = MT.Transformation()
        assert t != None, "Failed to make an empty Transformation"
        print(".", end="")
        t.registerLocalMethod(python_module='unitconversion', method_name='CtoF')
        assert t.getLocalMethod()[1] == 'CtoF', "Failed to register local method: Expected {}, got {}".format('CtoF', t.getLocalMethod()[1])
        print(".", end="")
        assert t.getLocalMethod()[0].__name__ == 'transformations.unitconversion', "Failed to register local method: Expected {}, got {}".format('transformations.unitconversion', t.getLocalMethod()[0].__name__)
        print(".", end="")
        t.registerOperands(operands=oneOperands)
        assert t._operands == oneOperands, "Failed to register operands: expected {}, got {}".format(oneOperands, t._operands)
        print(".", end="")
        assert t.getOperationResult('0') == decimal.Decimal('32'), "Expected {} as transformation result, got {}".format(decimal.Decimal('32'), t.getOperationResult(value='0'))
        print(".", end="")
        
        # Third test: init a partially empty transformation, and add two operands
        assert 'TempConvertor' in dir(unitconversion)
        t = MT.Transformation(python_module='unitconversion', method_name='TempConvertor')
        assert t != None, "Failed to make an partly empty Transformation"
        print(".", end="")
        assert t.getLocalMethod()[1] == 'TempConvertor', "Failed to register local method: Expected {}, got {}".format('CtoF', t.getLocalMethod()[1])
        print(".", end="")
        assert t.getLocalMethod()[0].__name__ == 'transformations.unitconversion', "Failed to register local method: Expected {}, got {}".format('transformations.unitconversion', t.getLocalMethod()[0].__name__)
        print(".", end="")
        t.registerOperands(operands=twoOperands)
        assert t._operands == twoOperands, "Failed to register operands: expected {}, got {}".format(twoOperands, t._operands)
        print(".", end="")
        assert t.getOperationResult(temp_value = '0', src_unit = 'c', tgt_unit = 'f') == decimal.Decimal('32'), "Expected {} as transformation result, got {}".format(decimal.Decimal('32'), t.getOperationResult(temp_value = '0', src_unit = 'f', tgt_unit = 'c'))
        print(".", end="")
        
        # Fail scenarios
        with self.assertRaises(AssertionError):
            MT.Transformation(python_module='unitconversion', method_name='CtoF', operands=['InvalidOperand'])
        print(".", end="")
        with self.assertRaises(AssertionError):
            MT.Transformation(python_module='unitconversion', method_name='appelepap', operands=oneOperands)
        print(".", end="")
        with self.assertRaises(AssertionError):
            MT.Transformation(python_module='appelepap', method_name='FtoC', operands=oneOperands)
        print(". done")


    def testMakeTransform(self):
        # Success scenarios
        # Test the creation of a callable transformation
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        t = MT.Transformation(python_module='unitconversion', method_name='FtoC', operands=self.operands)
        t.makeTransform(resultIRI='newIRI')
        assert callable(t.transform), "Expected callable function, but {} is not callable".format(t.transform)
        print(".", end="")
        assert t.getOperationResult('32') == decimal.Decimal('0'), "Expected {} as transformation result, got {}".format(decimal.Decimal('0'), t.getOperationResult('32'))
        print(".", end="")

        # Fail scenarios
        t = MT.Transformation(operands=self.operands)
        with self.assertRaises(AssertionError): 
            t.makeTransform(resultIRI='newIRI')
        print(".", end="")
        t = MT.Transformation(python_module='unitconversion', operands=self.operands)
        with self.assertRaises(AssertionError): 
            _ = t.makeTransform(resultIRI='newIRI')
        print(".", end="")
        t = MT.Transformation(method_name='FtoC', operands=self.operands)
        with self.assertRaises(AssertionError): 
            _ = t.makeTransform(resultIRI='newIRI')
        print(". done")


    def testTransform(self):
        from mediator import sparqlTools
        info = True
        debug = 3
        rule = 'TRANSFORM'
        if info or debug >= 1:
            print()
            print('=-'*7)
            print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
            print('=-'*7)
        for transform_tests in self.testCases[rule]:
            if info:
                print('\ntesting', rule, 'with', len(transform_tests['pass']), 'pass case(s) and', len(transform_tests['fail']), 'fail case(s)')
            if debug >= 3:
                print('> pass cases:', transform_tests['pass'])
                print('> fail cases:', transform_tests['fail'])
                print()
            testCriteria = []

            # PASS: Execute the test for each defined correspondence file that is expected to pass
            # Setup specifics for this testCase
            for testCase, testCriteria in transform_tests['pass'].items():
                if debug >= 1:
                    print('PASS case {} has specified {} tests'.format(testCase,len(testCriteria)))
                
                # Create a Alignment object only to have a valid Alignment object and create a valid nsMgr;
                #    the test data is incorrect edoal, and this code below takes that into consideration
                align = EDOALparser.Alignment(testCase, self.nsMgr)
                if align == None: raise TestException("Cannot find an alignment in file '{}'".format(testCase))

                testsEl = align._align.findall(self.nsMgr.asClarks('t:tests'))
                if testsEl == None or len(testsEl) == 0: raise TestException("No tests found, cannot perform tests")
                tests = testsEl[0].findall(self.nsMgr.asClarks('t:test'))
                if len(testCriteria) != len(tests): raise TestException('Test setup specifies {} tests, but {} tests found in test data ({})'.format(len(testCriteria), len(tests), testCase))
                if debug >=3: print('Found {} tests in test data'.format(len(tests)))
                for test in tests:
                    tname = test.get(NSManager.CLARKS_LABELS['RDFABOUT'])
                    # Check the test data is valid
                    if tname == None or tname == '': raise TestException('Testcase {}: Use of {} attribute in <test> element required to discern the various testCriteria'.format(testCase, NSManager.nsmap['RDFABOUT']))
                    edoal_entity = test.find(self.nsMgr.asClarks('edoal:entity1'))
                    if edoal_entity == None: raise TestException('Testcase {}: Test ({}) is required to contain an <entity1> element'.format(testCase, tname))
                    if debug >=3: print('Testing test: {} ..'.format(tname), end="")
                    # Parse the operation from the test data
                    oprtnEl = edoal_entity.find(self.nsMgr.asClarks('edoal:Apply'))
                    if oprtnEl is None: oprtnEl = edoal_entity.find(self.nsMgr.asClarks('edoal:Aggregate'))
                    if oprtnEl is None: raise TestException('Testcase {}: Test ({}) is required to contain a <Apply> or <Aggregate> element'.format(testCase, tname))
                    _, op_method = (oprtnEl.get(self.nsMgr.asClarks('edoal:operator'))).rsplit('/', 1)
                    if op_method is None: raise TestException('Testcase {}: Test ({}) is required to contain an operator attribute in the <Apply> or <Aggregate> element'.format(testCase, tname))
                    # Parse the operands from the test data
                    operands = []
                    args = oprtnEl.find(self.nsMgr.asClarks('edoal:arguments'))
                    for arg in list(args):
                        operands.append(align.Value(el=arg, parse_alignment=align))
                    if operands == []: raise TestException('Testcase {}: Test ({}) is required to contain at least one <arguments> element'.format(testCase, tname))

                    # Create the transformation specification ...
                    if not tname in testCriteria: raise TestException('Testcase {}: Test "{}" does not have any criteria, quitting.'.format(testCase, tname))
                    t = MT.Transformation(python_module='unitconversion', method_name=op_method, operands=operands)
                    if t == None: raise TestException("Cannot create a transformation with module 'unitconversion' and method '{}'".format(op_method))
                    # ... produce the callable transformation ...
                    t.makeTransform(resultIRI="someIri")
                    # ... produce the variable constraints from the query
                    # ... ... Check if the test query is available
                    if self.qt == []: raise TestException("Need to have test data (parsed sparql query) before testing can begin")
                    # ... ... produce the property entity
                    tei = testCriteria[tname]['test_entity_iri']
                    propEntity = MT.EProperty(entity_iri=tei, nsMgr=self.nsMgr)
                    assert propEntity.getIriRef() == self.nsMgr.asIRI(tei), "Invalid test data: could not create Property {}, got {}".format(self.nsMgr.asIRI(tei), propEntity.getIriRef())
                    # ... ... make the variable constraint
                    svn = testCriteria[tname]['sparql_var_name']
                    vcs = sparqlTools.Context.VarConstraints(sparql_tree=self.qt, sparql_var_name=svn, entity=propEntity)
                    # Do the test
                    result = t.transform(var_constraints = vcs)
                    print (result)
                    assert result == testCriteria[tname]['result'], "Test '{}' failed: expected '{}', got '{}'".format(tname, testCriteria[tname]['result'], result)
                    print(".", end="")
                    
            # Fail scenarios        
            for testCase, testCriteria in transform_tests['fail'].items():
                if debug >= 1:
                    print('FAIL case {} has specified {} tests'.format(testCase,len(testCriteria)))
                    assert False, "Implement fail tests for testTransform"
                    print(".", end="")

                    print(". done")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()