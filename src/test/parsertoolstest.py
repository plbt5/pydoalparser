'''
Created on 19 apr. 2016

@author: brandtp
'''
import decimal
import inspect
import unittest

from edoalparser import EDOALparser
from edoalparser import parserTools as PT
from test.mytestexceptions import TestException
from utilities.namespaces import NSManager


class correspondenceTest(unittest.TestCase):

    def setUp(self):
        testNS = {
            'med'   : 'http://ds.tno.nl/mediator/1.0/',
            'dc'    : 'http://purl.org/dc/elements/1.1/',
            'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        self.c = PT.Correspondence(nsMgr=self.nsMgr)
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
        N = 4 + 4
        # Success scenarios
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            count += 1
            # Success scenarios, QName with prefix
            testEnt = PT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://ds.tno.nl/mediator/1.0/appelepap>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, QName without prefix
            testEnt = PT._Entity(entity_iri=":appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<" + self.base + "appelepap>"
            assert testEnt.getIriRef() == exp_iri and testEnt.getType() == e_type
            # Success scenarios, with correct IRI
            testEnt = PT._Entity(entity_iri="http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, with correct <IRI>
            testEnt = PT._Entity(entity_iri="<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: got '{}', expected '{}'.".format(testEnt.getType(), e_type)
            # Success scenarios, with correct Clark's notation
            testEnt = PT._Entity(entity_iri="{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear", entity_type=e_type, nsMgr=self.nsMgr)
            exp_iri = "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"
            assert testEnt.getIriRef() == exp_iri, "Testfault: got '{}', expected '{}'.".format(testEnt.getIriRef(), exp_iri)
            assert testEnt.getType() == e_type, "Testfault: expected '{}', got '{}'.".format(testEnt.getType(), e_type)
            print(".", end="")
        # Failure scenarios
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            count += 1
            with self.assertRaises(RuntimeError): 
                testEnt = PT._Entity(entity_iri=":^_invalidIriChar", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = PT._Entity(entity_iri=":!_invalidIriChar", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = PT._Entity(entity_iri="^_invalidIriChar", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = PT._Entity(entity_iri="", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = PT._Entity(entity_iri="unknownPF:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(RuntimeError): 
                testEnt = PT._Entity(entity_iri="noPFOrAnythingWhatsoever", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = PT._Entity(entity_iri=12, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = PT._Entity(entity_iri=12.3, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = PT._Entity(entity_iri=True, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = PT._Entity(entity_iri=False, entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                testEnt = PT._Entity(entity_iri=None, entity_type=e_type, nsMgr=self.nsMgr)
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N, count)
        print(". done")

    def testConstruction(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N = 3 + 3 * 3 + 4 + 4
        # Mixed success and failure scenarios
        for e_type1 in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP']]:
            count += 1
            testEnt1 = PT._Entity(entity_iri="med:appelepap", entity_type=e_type1, nsMgr=self.nsMgr)
            # Success scenario - unary operation
            constr = PT.Neg(testEnt1)
            assert constr.getCType() == PT._EntityConstruction.NOTSYMBOL, "Testfault: expected '{}', got '{}'.".format(PT._EntityConstruction.NOTSYMBOL, constr.getCType())
            print(".", end="")
            # Binary operation scenarios
            for e_type2 in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP']]:
                testEnt2 = PT._Entity(entity_iri="med:appelepap", entity_type=e_type2, nsMgr=self.nsMgr)
                if e_type1 == e_type2:
                    # Success scenario - binary operations
                    count += 1
                    constr = PT.Union(testEnt1, testEnt2)
                    assert constr.getCType() == PT._EntityConstruction.SQRUNION, "Testfault: expected '{}', got '{}'.".format(PT._EntityConstruction.SQRUNION, constr.getCType())
                    constr = PT.Intersection(testEnt1, testEnt2)
                    assert constr.getCType() == PT._EntityConstruction.SQRINTSCT, "Testfault: expected '{}', got '{}'.".format(PT._EntityConstruction.SQRINTSCT, constr.getCType())
                    print(".", end="")
                else: 
                    # Failure scenario - binary operations
                    count += 1
                    with self.assertRaises(AssertionError): 
                        constr = PT.Union(testEnt1, testEnt2)
                    print(".", end="")
        # Failure scenarios
        testEnt1 = PT._Entity(entity_iri="med:appelepap", entity_type=PT.Alignment.EDOAL['INST'], nsMgr=self.nsMgr)
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            count += 1
            testEnt2 = PT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                constr = PT.Union(testEnt1, testEnt2)
            print(".", end="")
        testEnt2 = PT._Entity(entity_iri="med:appelepap", entity_type=PT.Alignment.EDOAL['INST'], nsMgr=self.nsMgr)
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            count += 1
            testEnt1 = PT._Entity(entity_iri="med:appelepap", entity_type=e_type, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError): 
                constr = PT.Union(testEnt1, testEnt2)
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N, count)
        print(". done")

    def testSetSrcEE(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N = 4 * 4 + 3 * 4 + 4
        # Success scenarios; entity_expr of type _Entity
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            for test_iri in ["med:appelepap", ":appelepap", "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"]:
                count += 1
                testEnt = PT._Entity(entity_iri=test_iri, entity_type=e_type, nsMgr=self.nsMgr)
                self.c.setEE1(entity_expr=testEnt)
                assert self.c.getEE1().getIriRef() == self.nsMgr.asIRI(test_iri), "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getIriRef(), self.nsMgr.asIRI(test_iri))
                assert self.c.getEE1().getType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getType(), e_type)
                print(".", end="")
                if e_type != PT.Alignment.EDOAL['INST']:
                    count += 1
                    # Success scenarios; entity_expr of type _EntityConstruction
                    testEnt2 = PT._Entity(entity_iri="med:perenmoes", entity_type=e_type, nsMgr=self.nsMgr)
                    constr = PT.Union(testEnt, testEnt2)
                    self.c.setEE1(entity_expr=constr)
                    assert self.c.getEE1().getCType() == PT._EntityConstruction.SQRUNION, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getCType(), PT._EntityConstruction.SQRUNION)
                    assert self.c.getEE1().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntType(), e_type)
                    assert self.c.getEE1().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[0], testEnt)
                    assert self.c.getEE1().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[1], testEnt2)
                    constr = PT.Intersection(testEnt, testEnt2)
                    self.c.setEE1(entity_expr=constr)
                    assert self.c.getEE1().getCType() == PT._EntityConstruction.SQRINTSCT, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getCType(), PT._EntityConstruction.SQRINTSCT)
                    assert self.c.getEE1().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntType(), e_type)
                    assert self.c.getEE1().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[0], testEnt)
                    assert self.c.getEE1().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE1().getEntities()[1], testEnt2)
                    print(".", end="")
        # Failure scenarios
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            count += 1
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
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N, count)
        print(". done")

    def testSetTgtEE(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N = 4 * 4 + 3 * 4 + 4
        # Success scenarios; entity_expr of type _Entity
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            for test_iri in ["med:appelepap", ":appelepap", "http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear", "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"]:
                count += 1
                testEnt = PT._Entity(entity_iri=test_iri, entity_type=e_type, nsMgr=self.nsMgr)
                self.c.setEE2(entity_expr=testEnt)
                assert self.c.getEE2().getIriRef() == self.nsMgr.asIRI(test_iri), "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getIriRef(), self.nsMgr.asIRI(test_iri))
                assert self.c.getEE2().getType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getType(), e_type)
                print(".", end="")
                if e_type != PT.Alignment.EDOAL['INST']:
                    # Success scenarios; entity_expr of type _EntityConstruction
                    count += 1
                    testEnt2 = PT._Entity(entity_iri="med:perenmoes", entity_type=e_type, nsMgr=self.nsMgr)
                    constr = PT.Union(testEnt, testEnt2)
                    self.c.setEE2(entity_expr=constr)
                    assert self.c.getEE2().getCType() == PT._EntityConstruction.SQRUNION, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getCType(), PT._EntityConstruction.SQRUNION)
                    assert self.c.getEE2().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntType(), e_type)
                    assert self.c.getEE2().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[0], testEnt)
                    assert self.c.getEE2().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[1], testEnt2)
                    constr = PT.Intersection(testEnt, testEnt2)
                    self.c.setEE2(entity_expr=constr)
                    assert self.c.getEE2().getCType() == PT._EntityConstruction.SQRINTSCT, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getCType(), PT._EntityConstruction.SQRINTSCT)
                    assert self.c.getEE2().getEntType() == e_type, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntType(), e_type)
                    assert self.c.getEE2().getEntities()[0] == testEnt, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[0], testEnt)
                    assert self.c.getEE2().getEntities()[1] == testEnt2, "Testfault: got '{}', expected '{}'.".format(self.c.getEE2().getEntities()[1], testEnt2)
                    print(".", end="")
        # Failure scenarios
        for e_type in [PT.Alignment.EDOAL['CLASS'], PT.Alignment.EDOAL['RELN'], PT.Alignment.EDOAL['PROP'], PT.Alignment.EDOAL['INST']]:
            count += 1
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
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N, count)
        print(". done")

    def testSetCorrRelation(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N = 5 
        # Success scenarios
        for rel in [PT.MEDRELEQ, PT.MEDRELSUB, PT.MEDRELSUP, PT.MEDRELIN, PT.MEDRELNI]:
            count += 1
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
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N, count)
        print(". done")

    def testSetCorrMeasure(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        count = 0
        N = 6 + 8
        # Success scenarios
        for val, tpe in [(0.01, self.nsMgr.asIRI('xsd:float')), ('medium', self.nsMgr.asIRI('xsd:string')), (0.0, self.nsMgr.asIRI('xsd:double')), (1.0, self.nsMgr.asIRI('xsd:float')), (0, self.nsMgr.asIRI('xsd:decimal')), (1, self.nsMgr.asIRI('xsd:integer'))]:
            count += 1
            self.c.setCorrMeasure(measure=val, measure_type=tpe)
            assert (val, tpe) == self.c.getCorrMeasure()
            print(".", end="")
        # Failure scenarios - no check exist yet for incoherence between measure and measure_type, e.g., (0.42, xsd:integer), or ('appelepap', xsd:float)
        for val, tpe in [(0.01, ''), (None, self.nsMgr.asIRI('xsd:float')), (None, None), ('', None), (None, ''), ('', ''), (-0.1, self.nsMgr.asIRI('xsd:float')), (12, self.nsMgr.asIRI('xsd:integer'))]:
            count += 1
            with self.assertRaises(AssertionError): 
                self.c.setCorrMeasure(measure=val, measure_type=tpe)
            print(".", end="")
        assert count == N, "Didn't test everything, expected {} tests, done only {}".format(N, count)
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
        self.path = PT.Path()
        self.property = PT.EProperty(entity_iri='med:testProperty', nsMgr=self.nsMgr)
        self.relations = [PT.ERelation(entity_iri='med:testRel1', nsMgr=self.nsMgr), PT.ERelation(entity_iri='med:testRel2', nsMgr=self.nsMgr), PT.ERelation(entity_iri='med:testRel3', nsMgr=self.nsMgr)]
        print('Testcase: {}'.format(self.__class__.__name__))

    def tearDown(self):
        pass
    
    def testPath(self):
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        # PASS test
        for r in self.relations:
            self.path.append(r)
        self.path.append(self.property)
        for path, crit in zip(self.path, self.relations):
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
        self.c = PT.Correspondence(nsMgr=self.nsMgr)
        self.operands = []
        self.testCases = {}
        
        '''
        The Transform tests will validate:
        * testTransformation: the creation of a transformation specification
        * testMakeTransform:  the transition from the name of an operation to a callable function
        * testTransform:      the transition from the specification of the operands to the inclusion of the correct values in the operation
        '''
        
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
        operandEl = t.find(str(self.nsMgr.asClarks('edoal:entity1')))
        if operandEl == None: raise TestException("Cannot find <edoal:entity1> element in <edoal:Transformation> ")
        oneOperands.append(self.align.Value(el=operandEl, parse_alignment=self.align))
        
        twoOperands = []
        operandEl = t.find(str(self.nsMgr.asClarks('edoal:entity2')) + '/' + str(self.nsMgr.asClarks('edoal:Apply')) + '/' + str(self.nsMgr.asClarks('edoal:arguments')))
        if operandEl == None: raise TestException("Cannot find <edoal:entity2><edoal:Apply><edoal:arguments> element in <edoal:Transformation> ")
        for value_el in operandEl.iter():
            if value_el.tag == self.nsMgr.asClarks('edoal:Literal'):
                twoOperands.append(self.align.Value(el=value_el, parse_alignment=self.align))

        # PASS tests
        # First test: init a complete transformation
        assert 'FtoC' in dir(unitconversion)
        t = PT.Transformation(python_module='unitconversion', method_name='FtoC', operands=oneOperands)
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
        t = PT.Transformation()
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
        t = PT.Transformation(python_module='unitconversion', method_name='TempConvertor')
        assert t != None, "Failed to make an partly empty Transformation"
        print(".", end="")
        assert t.getLocalMethod()[1] == 'TempConvertor', "Failed to register local method: Expected {}, got {}".format('CtoF', t.getLocalMethod()[1])
        print(".", end="")
        assert t.getLocalMethod()[0].__name__ == 'transformations.unitconversion', "Failed to register local method: Expected {}, got {}".format('transformations.unitconversion', t.getLocalMethod()[0].__name__)
        print(".", end="")
        t.registerOperands(operands=twoOperands)
        assert t._operands == twoOperands, "Failed to register operands: expected {}, got {}".format(twoOperands, t._operands)
        print(".", end="")
        assert t.getOperationResult(temp_value='0', src_unit='c', tgt_unit='f') == decimal.Decimal('32'), "Expected {} as transformation result, got {}".format(decimal.Decimal('32'), t.getOperationResult(temp_value='0', src_unit='f', tgt_unit='c'))
        print(".", end="")
        
        # Fail scenarios
        with self.assertRaises(AssertionError):
            PT.Transformation(python_module='unitconversion', method_name='CtoF', operands=['InvalidOperand'])
        print(".", end="")
        with self.assertRaises(AssertionError):
            PT.Transformation(python_module='unitconversion', method_name='appelepap', operands=oneOperands)
        print(".", end="")
        with self.assertRaises(AssertionError):
            PT.Transformation(python_module='appelepap', method_name='FtoC', operands=oneOperands)
        print(". done")

    def testMakeTransform(self):
        # Success scenarios
        # Test the creation of a callable transformation
        print('\tTesting {} '.format(inspect.currentframe().f_code.co_name), end="")
        t = PT.Transformation(python_module='unitconversion', method_name='FtoC', operands=self.operands)
        t.makeTransform(resultIRI='newIRI')
        assert callable(t.transform), "Expected callable function, but {} is not callable".format(t.transform)
        print(".", end="")
        assert t.getOperationResult('32') == decimal.Decimal('0'), "Expected {} as transformation result, got {}".format(decimal.Decimal('0'), t.getOperationResult('32'))
        print(".", end="")

        # Fail scenarios
        t = PT.Transformation(operands=self.operands)
        with self.assertRaises(AssertionError): 
            t.makeTransform(resultIRI='newIRI')
        print(".", end="")
        t = PT.Transformation(python_module='unitconversion', operands=self.operands)
        with self.assertRaises(AssertionError): 
            _ = t.makeTransform(resultIRI='newIRI')
        print(".", end="")
        t = PT.Transformation(method_name='FtoC', operands=self.operands)
        with self.assertRaises(AssertionError): 
            _ = t.makeTransform(resultIRI='newIRI')
        print(". done")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
