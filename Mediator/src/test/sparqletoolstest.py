'''
Created on 29 apr. 2016

@author: brandtp
'''
import unittest
from test.mytestexceptions import TestException
from parsertools.base import ParseStruct
from parsertools.parsers import sparqlparser 
import inspect
import json
from mediator import sparqlTools
from test import mytestexceptions

class TestVarConstraints(unittest.TestCase):


    def setUp(self):
        self.testdir = './resources/sparqlQueries/'
        filepath = self.testdir + 'manifest.json'
        print("="*30)
        print("Test configuration from {}:".format(filepath))
        with open(filepath) as f:    
            self.testCases = json.load(f)


    def tearDown(self):
        pass

# Skeleton for a manifest.json driven test process
# 
#     def testSomeModuleName(self):
#         testModuleName = inspect.currentframe().f_code.co_name
#         tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:SUT"] == testModuleName]
#         print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
#         for test in tests:
#             print('\tTesting {} ({}) ..'.format(self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")
#         
#             ----Do You Tests----
#
#             print(". done!")
#         



    def testValueLogicExpression(self):
        '''
            Test that: The created object is a Dictionary with entries {'varRef': varRef, 'comparator': comparator, 'restriction': restriction}
            Test subject: The node in the sparql tree that represents the variable
            Test data: sparql value logic expressions
        '''
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:SUT"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        for test in tests:
            print('\tTesting {} subtests: {} ({}) ..'.format(len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")
            # Get the test subject, i.e., the sparql_var
            if self.testCases[test]["mf:action"]["mf:subject"]["rdf:type"] != "sparql_var": raise TestException("Invalid test data, expected 'sparql_var', got '{}'".format(self.testCases[test]["mf:action"]["mf:subject"]["rdf:type"]))
            sparql_var = self.testCases[test]["mf:action"]["mf:subject"]["value"]
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] != "sparle_query": raise TestException("Invalid test data, expected 'sparle_query', got '{}'".format(testData["rdf:type"]))
                file = self.testdir + testData["value"]
                with open(file) as f:
                    qry = f.read()
    
                rq = sparqlparser.parseQuery(qry)
    #             print(rq.dump())
                constraints = rq.searchElements(label="constraint")
    #             print("filter:\n", constraints)
                if constraints == None or constraints == []: raise TestException("Cannot find 'constraints' labels in sparql query")
                for fe in constraints:
        #                 print("searching {}".format(sparql_var))
                    # Get the variables in this constraint
                    varElements = fe.searchElements(element_type=sparqlparser.SPARQLParser.Var, value=sparql_var)
                    if varElements == None or varElements == []: raise TestException("Cannot find a variable in the sparql tree")
                    
                    # Loop over the expected results
                    for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                        # Now the test environment is complete, hence perform the PASS annd FAIL tests
                        # Create for each found variable a Value Logic Expression 
                        for var in varElements:
                            if testCriteria["rdf:type"] == "PASS":
                                # Execute the PASS tests, e.g., get the expected results to compare with
                                filename = testCriteria["value"]
            #                     print("filename:\n", filename)
                                with open(self.testdir + filename) as f:
                                    results_exp = json.load(f)

                                # For each filter element that has been found, perform the test
#                                 print("creating vln")
                                vln = sparqlTools.Context.VarConstraints.ValueLogicExpression(variable_node=var)
            #                     print("vln : ", vln)
                                # Test if this value logic expression was expected or not
                                assert len(vln) > 0, "Test failed: No value logic expressions created"
                                vle = {
                                    "v": {"type": type(vln["varRef"]).__name__, "value": str(vln["varRef"]) } ,
                                    "c": {"type": type(vln["comparator"]).__name__, "value": str(vln["comparator"]) } ,
                                    "r": {"type": type(vln["restriction"]).__name__, "value": str(vln["restriction"]) } 
                                }
                                assert vle in results_exp["results"]["bindings"], "Test failed: created a value logic expression that was not expected: \n{}".format(vle)
                                
                            elif testCriteria["rdf:type"] == "FAIL":
                                # Execute the FAIL tests
                                with self.assertRaises(testCriteria["value"]):
                                    # The following method call should raise an exception
                                    _ = sparqlTools.Context.VarConstraints.ValueLogicExpression(variable_node=var)

                            else: raise TestException("Illegal value in test manifest, expected 'PASS' or 'FAIL', got '{}'".format(testCriteria["rdf:type"])) 

            print(". done!")

    def testVarConstraint(self):
        '''
            Input:
            - sparql_tree: (sparqlparser.ParseStruct)
            - sparql_var: (string) 
            Test that: the created object contains the following attributes:
            - boundVar: (string) : the name of the variable
            - valueLogicEpressions: (list) : a list of (ValueLogicExpression) that represent the constraints that apply to this variable. Each element in the
                list represents a singe constraint, e.g., "?var > 23.0", or "DATATYPE(?var) = '<iripath><class_name>'"
            Test subject: the name of the sparql variable
            Test data: sparql FILTER constructs
        '''

        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:SUT"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        for test in tests:
            print('\tTesting {} subtests: {} ({}) ..'.format(len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")

            # Get the test subject, i.e., the sparql_var
            if self.testCases[test]["mf:action"]["mf:subject"]["rdf:type"] != "sparql_var": raise TestException("Invalid test data, expected 'sparql_var', got '{}'".format(self.testCases[test]["mf:action"]["mf:subject"]["rdf:type"]))
            sparqlVarName = self.testCases[test]["mf:action"]["mf:subject"]["value"]
            
            # Cycle through each test data that occurs in the test case
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] != "sparle_query": raise TestException("Invalid test data, expected 'sparle_query', got '{}'".format(testData["rdf:type"]))
 
                # Get the test data, i.e., read the query file and parse the query
                file = self.testdir + testData["value"]
                with open(file) as f:
                    qry = f.read()
                sparqlTree = sparqlparser.parseQuery(qry)
                assert sparqlTree != None and sparqlTree.searchElements(label="constraint") != []
#                     print(sparqlTree.dump())

                # Loop over the test criteria
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now the test environment is complete, hence perform the PASS and FAIL tests
                    # Establish the constraints that belong to the variable under test

                    if testCriteria["rdf:type"] == "PASS":
                        # Execute the PASS tests, e.g., get the expected results to compare with
                        filename = testCriteria["value"]
#                         print("filename:\n", filename)
                        with open(self.testdir + filename) as f:
                            resultsExp = json.load(f)
    
                        # PERFORM THE OPERATION UNDER TEST
    #                                 print("creating vcs")
                        vcs = sparqlTools.Context.VarConstraints(sparql_tree=sparqlTree, sparql_var_name=sparqlVarName)
    #                     print("vcs : ", vcs)
                        
                        # Test if this value logic expression was expected or not
                        assert len(vcs.getValueLogicExpressions()) > 0, "Test failed: No value logic expressions created"
                        for vle in vcs.getValueLogicExpressions():
                            vleExpanded = {
                                "v": {"type": type(vle["varRef"]).__name__, "value": str(vle["varRef"]) } ,
                                "c": {"type": type(vle["comparator"]).__name__, "value": str(vle["comparator"]) } ,
                                "r": {"type": type(vle["restriction"]).__name__, "value": str(vle["restriction"]) } 
                            }
                            assert vleExpanded in resultsExp["results"]["bindings"], "Test failed: created a value logic expression that was not expected: \n{}".format(vle)
                            assert vcs.getBoundVar() == sparqlVarName
    
                    elif testCriteria["rdf:type"] == "FAIL":
                        # Execute the FAIL tests
                        try:
                            # The following method call should raise an exception
                            _ = sparqlTools.Context.VarConstraints(sparql_tree=sparqlTree, sparql_var_name=sparqlVarName)
                        except Exception as e:
                            assert type(e).__name__ == testCriteria["value"]
    
                    else: raise TestException("Illegal value in test manifest, expected 'PASS' or 'FAIL', got '{}'".format(testCriteria["rdf:type"])) 

            print(". done!")


class TestQueryPatternTripleAssociation(unittest.TestCase):
                                        
    def setUp(self):
        pass
         

    def tearDown(self):
        pass

    def testInit(self):
        assert False, "Create testcase for class qptAssociations"
        
    def testAddQPTRef(self):
        assert False, "Create testcase for AddQPTRef"
        
    def testGetQPTRef(self):
        assert False, "Create testcase for getQPTRef"


class TestQPTripleRef(unittest.TestCase):
                                        
    def setUp(self):
        pass
         

    def tearDown(self):
        pass

    def testInit(self):
        assert False, "Create testcase for class QPTripleRef"
        
    def testSetType(self):
        assert False, "Create testcase for setType"
        
    def testAddAssociate(self):
        assert False, "Create testcase for addAssociate"

    def testConsiderBinding(self):
        assert False, "Create testcase for considerBinding"
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testQPTripleRefs']
    unittest.main()