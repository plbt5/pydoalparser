'''
Created on 26 feb. 2016

@author: brandtp
'''
import unittest
from test.mytestexceptions import * 
from mediator.mediator import Mediator
from utilities import namespaces
import json
import inspect
from parsertools.parsers.sparqlparser import parseQuery


class TestMediator(unittest.TestCase):

    
    def setUp(self):
        
        self.testdir = './resources/mediator/'
        filepath = self.testdir + 'manifest01.json'
        print("="*30)
        print("Test configuration from {}:".format(filepath))
        with open(filepath) as f:    
            self.testCases = json.load(f)
        self.nsDict = {
              'ts'   : 'http://ts.tno.nl/mediator/test#'
              }
        self.nsMgr = namespaces.NSManager(self.nsDict, "http://ts.tno.nl/mediator/test#")
        

    def tearDown(self):
        pass
             
       
    def testMediator(self):
        '''
        Test that:
        1 - mediation creation is successful
        '''
        testModuleName = inspect.currentframe().f_code.co_name
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,testModuleName), end="", flush=True)
        # Success cases
        mediator = Mediator(about='ts:myMediator', nsDict=self.nsDict)
        assert mediator.getName() == self.nsMgr.asIRI('ts:myMediator')

        # Fail cases
        with self.assertRaises(AssertionError):
            Mediator(None) 
        with self.assertRaises(AssertionError):
            Mediator(12.0) 
            
        print(". done!")
    
    def testAddAlignment(self):
        '''
        Test that:
        1 - mediator can add an alignment
        2 - mediator refuses to add same alignment files
        3 - mediator refuses to add duplicate alignments
        '''
        testModuleName = inspect.currentframe().f_code.co_name
        print('Testcase {}\n\ttesting {} '.format(self.__class__.__name__,testModuleName), end="", flush=True)
        
        mediator = Mediator(about='ts:myMediator', nsDict=self.nsDict)
        assert self.nsMgr.asIRI('ts:myMediator') == mediator.getName(), "Expected {}, got {}".format(self.nsMgr.asIRI('ts:myMediator'), mediator.getName())

        # Success case
        mediator.addAlignment(alignment_filename="../examples/alignTemp1A-1B.xml")
        assert len(mediator.alignments) == 1, "got {}".format(len(mediator.alignments))
        for iri in mediator.alignments:
            assert iri == "http://ts.tno.nl/mediator/1.0/examples/alignTemp1A-1B.xml", "got '{}'".format(iri)
        print(".", end="")
        
        # Fail case
        with self.assertWarns(UserWarning):
            mediator.addAlignment(alignment_filename="../examples/alignTemp1A-1B.xml")
        print(".", end="")
        with self.assertRaises(AssertionError):
            mediator.addAlignment(alignment_filename="duplicateToAlignTemp1A-1B.xml")
        print(".", end="")
            
        print(". done!")
    
    def testTranslate(self):
        '''
        Test that:
        1 - a mediator can successfully translate various relevant queries (SELECT and ASK)
        2 - a mediator ignores queries with terms that are not mentioned in the alignment
        '''
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:name"] == testModuleName]
        print('Testcase: "{}" about {}, has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], len(tests)))

        mediator = Mediator(about='ts:myMediator', nsDict=self.nsDict)
        assert mediator.getNSs().nsConcat(mediator.getNSs().expand('ts'),'myMediator') == mediator.getName(), "Expected {}, got {}".format(mediator.getNSs().nsConcat(mediator.getNSs().expand('ts'),'myMediator'), mediator.getName())

        # Success case
        for test in tests:
            print('\tTesting system under test "{}" with {} subtests: {} ({}) '.format(self.testCases[test]["mf:SUT"], len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]))
            # Load an alignment
            if not self.testCases[test]["mf:action"]["mf:subject"].__contains__("alignment") : raise TestException("Invalid test data, expected 'alignment', got '{}'".format(self.testCases[test]["mf:action"]["mf:subject"].keys()[0]))
            mediator.addAlignment(alignment_filename=self.testCases[test]["mf:action"]["mf:subject"]["alignment"]["value"])
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                assert testData["sparql_rq"]["rdf:type"] == "rq", "Invalid test data, expected 'rq', got '{}'".format(testData["sparql_rq"]["rdf:type"])
                sparqlFilename = testData["sparql_rq"]["value"]
                assert testData["source_onto"]["rdf:type"] == "iri", "Invalid test data, expected 'iri', got '{}'".format(testData["source_onto"]["rdf:type"])
                srcOntoIri = testData["source_onto"]["value"]
                print("\ttest data: {} instantiates from {}".format(sparqlFilename, srcOntoIri))
                with open(self.testdir + sparqlFilename) as f:
                    sparl_string = f.read()
                print("\ttest query: \n{}".format(sparl_string))
                # Loop over the expected results
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now the test environment is complete, hence perform the PASS and FAIL tests
                    if testCriteria["rdf:type"] == "PASS":
                        # Execute the PASS tests, e.g., get the expected results to compare with
                        filename = testCriteria["value"]
                        with open(self.testdir + filename) as f:
                            results_exp = f.read()
                        # Do the test, i.e., translate the query
                        result = mediator.translate(data = sparl_string, source_onto_ref = srcOntoIri)
                        print("\tTranslation result: {}\n".format(str(result)))
                        # Verify the result
                        assert str(result) == results_exp, "Expected: \n{}\nGot:\n{}".format(results_exp, str(result))
                    elif testCriteria["rdf:type"] == "FAIL":
                        # Execute the FAIL tests, e.g., get the expected results to compare with
                        rq = parseQuery(sparl_string)
                        rq.expandIris()                        
                        with self.assertWarns(AS_EXCEPTION_TYPE[testCriteria["value"]]):
                            result = mediator.translate(data = sparl_string, source_onto_ref = srcOntoIri)
                        assert str(result) == str(rq), "Found '{}'\nexptd '{}'".format(str(result),rq)
                    else: raise TestException("Invalid test data, unknown criterion '{}'".format(testCriteria["rdf:type"]))
                        
        print(". done!")

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testMediator']
    unittest.main()