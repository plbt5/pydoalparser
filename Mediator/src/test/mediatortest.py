'''
Created on 26 feb. 2016

@author: brandtp
'''
import unittest
from test.mytestexceptions import TestException
from mediator.mediator import Mediator
from utilities import namespaces
import json
import inspect


class TestMediator(unittest.TestCase):

    
    def setUp(self):
        
        self.testdir = './resources/sparqlQueries/'
        filepath = self.testdir + 'manifest04.json'
        print("="*30)
        print("Test configuration from {}:".format(filepath))
        with open(filepath) as f:    
            self.testCases = json.load(f)
        ns = {
#               'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
#               'xsd': "http://www.w3.org/2001/XMLSchema#",
#               'align':"http://knowledgeweb.semanticweb.org/heterogeneity/alignment#",
#               'edoal':'http://ns.inria.org/edoal/1.0/#',
#               'ontoA': 'http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A',
              'ts'   : 'http://ts.tno.nl/mediator/test#'
              }
        self.nsMgr = namespaces.NSManager(ns, "http://ts.tno.nl/mediator/test#")

        self.fn="../examples/alignTemp1A-1B.xml"
        self.query = '''
            PREFIX  ontoA:  <http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A#>
            PREFIX  rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX  xsd:    <http://www.w3.org/2001/XMLSchema#>
            
            SELECT ?p ?t
            WHERE {
                ?p rdf:type ontoA:Patient .
                ?p ontoA:hasTemp ?t;
                   ontoA:hasAge ?a.
                FILTER ( 
                    ( ?t > 37.0 ) && 
                    ( ?a < 37.0 ) 
                )
            }            
            '''
        self.mediator = Mediator(about='ts:myMediator', nsDict=ns)
        assert self.mediator.getNSs().nsConcat(self.mediator.getNSs().expand('ts'),'myMediator') == self.mediator.getName(), "Expected {}, got {}".format(self.mediator.getNSs().nsConcat(self.mediator.getNSs().expand('ts'),'myMediator'), self.mediator.getName())
        

    def tearDown(self):
        pass
             
       
    def testMediator(self):

        # Fail cases
        with self.assertRaises(AssertionError):
            Mediator(None) 
        with self.assertRaises(AssertionError):
            Mediator(12.0) 
        
    def testTranslate(self):
        # Success case
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:name"] == testModuleName]
        print('Testcase: "{}" about {}, has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], len(tests)))

        for test in tests:
            print('\tTesting system under test "{}" with {} subtests: {} ({}) ..'.format(self.testCases[test]["mf:SUT"], len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")
            # Load an alignment
            if not self.testCases[test]["mf:action"]["mf:subject"].__contains__("alignment") : raise TestException("Invalid test data, expected 'alignment', got '{}'".format(self.testCases[test]["mf:action"]["mf:subject"].keys()[0]))
            self.mediator.addAlignment(alignment_filename=self.testCases[test]["mf:action"]["mf:subject"]["alignment"]["value"])
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                assert testData["sparql_rq"]["rdf:type"] == "rq", "Invalid test data, expected 'rq', got '{}'".format(testData["sparql_rq"]["rdf:type"])
                alignFilename = testData["sparql_rq"]["value"]
                with open(self.testdir + alignFilename) as f:
                    sparl_string = f.read()
                # Loop over the expected results
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    print(".", end="")
                    # Now the test environment is complete, hence perform the PASS and FAIL tests
                    if testCriteria["rdf:type"] == "PASS":
                        # Execute the PASS tests, e.g., get the expected results to compare with
                        filename = testCriteria["value"]
    #                     print("filename:\n", filename)
                        with open(self.testdir + filename) as f:
                            results_exp = f.read()
                        # Do the test, i.e., translate the query
                        result = self.mediator.translate(sparl_string)
                        print(str(result))
                        # Verify the result
                        assert str(result) == results_exp
        print(". done!")

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testMediator']
    unittest.main()