'''
Created on 29 apr. 2016

@author: brandtp
'''
import unittest
from test.mytestexceptions import TestException
from parsertools.base import ParseStruct
from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery
import inspect
import json
from mediator import sparqlTools, mediatorTools
from utilities import namespaces
from test import mytestexceptions
from mediator.mediator import Mediator

class TestVarConstraints(unittest.TestCase):


    def setUp(self):
        self.testdir = './resources/sparqlQueries/'
        filepath = self.testdir + 'manifest01.json'
        print("="*30)
        print("Test configuration from {}:".format(filepath))
        with open(filepath) as f:    
            self.testCases = json.load(f)
        ns = {'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              'xsd': "http://www.w3.org/2001/XMLSchema#",
              'align':"http://knowledgeweb.semanticweb.org/heterogeneity/alignment#",
              'edoal':'http://ns.inria.org/edoal/1.0/#',
              'ontoA': 'http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A',
              't'   : 'http://ts.tno.nl/mediator/test#'
              }
        self.nsMgr = namespaces.NSManager(ns, "http://ts.tno.nl/mediator/test#")


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
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:name"] == testModuleName]
        print('Testcase: "{}" about {}, has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], len(tests)))
        for test in tests:
            print('\tTesting system under test "{}" with {} subtests: {} ({}) ..'.format(self.testCases[test]["mf:SUT"], len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")
            # Get the test subject, i.e., the sparql_var
            if self.testCases[test]["mf:action"]["mf:subject"]["rdf:type"] != "sparql_var": raise TestException("Invalid test data, expected 'sparql_var', got '{}'".format(self.testCases[test]["mf:action"]["mf:subject"]["rdf:type"]))
            sparql_var = self.testCases[test]["mf:action"]["mf:subject"]["value"]
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] != "sparle_query": raise TestException("Invalid test data, expected 'sparle_query', got '{}'".format(testData["rdf:type"]))
                file = self.testdir + testData["value"]
                with open(file) as f:
                    qry = f.read()
    
                rq = parseQuery(qry)
    #             print(rq.dump())
                constraints = rq.searchElements(label="constraint")
    #             print("filter:\n", constraints)
                if constraints == None or constraints == []: raise TestException("Cannot find 'constraints' labels in sparql query")
                for fe in constraints:
        #                 print("searching {}".format(sparql_var))
                    # Get the variables in this constraint
                    varElements = fe.searchElements(element_type=SPARQLParser.Var, value=sparql_var)
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
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:name"] == testModuleName]
        print('Testcase: "{}" about {}, has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], len(tests)))
        for test in tests:
            print('\tTesting system under test "{}" with {} subtests: {} ({}) ..'.format(self.testCases[test]["mf:SUT"], len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")

            # Get the test subject, i.e., the sparql_var
            if self.testCases[test]["mf:action"]["mf:subject"][0]["rdf:type"] != "sparql_var": raise TestException("Invalid test data, expected 'sparql_var', got '{}'".format(self.testCases[test]["mf:action"]["mf:subject"][0]["rdf:type"]))
            sparqlVarName = self.testCases[test]["mf:action"]["mf:subject"][0]["value"]  
                                  
            test_entity_iri=self.testCases[test]["mf:action"]["mf:subject"][1]["value"]
            test_entity = mediatorTools.EProperty(entity_iri=test_entity_iri, nsMgr=self.nsMgr)
            assert test_entity.getIriRef() == self.nsMgr.asIRI(test_entity_iri), "Invalid test data: could not create Property {}, got {}".format(self.nsMgr.asIRI(test_entity_iri), test_entity.getIriRef())

            # Cycle through each test data that occurs in the test case
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] != "sparle_query": raise TestException("Invalid test data, expected 'sparle_query', got '{}'".format(testData["rdf:type"]))
 
                # Get the test data, i.e., read the query file and parse the query
                file = self.testdir + testData["value"]
                with open(file) as f:
                    qry = f.read()
                sparqlTree = parseQuery(qry)
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
                        vcs = sparqlTools.Context.VarConstraints(sparql_tree=sparqlTree, sparql_var_name=sparqlVarName, entity=test_entity)
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
                            _ = sparqlTools.Context.VarConstraints(sparql_tree=sparqlTree, sparql_var_name=sparqlVarName, entity=test_entity)
                        except Exception as e:
                            assert type(e).__name__ == testCriteria["value"]
    
                    else: raise TestException("Illegal value in test manifest, expected 'PASS' or 'FAIL', got '{}'".format(testCriteria["rdf:type"])) 

            print(". done!")


from mediator import EDOALparser
class TestQueryPatternTripleAssociation(unittest.TestCase):
                                        
    def setUp(self):
        self.testdir = './resources/sparqlQueries/'
        filepath = self.testdir + 'manifest03.json'
        print("="*30)
        print("Test configuration from {}:".format(filepath))
        with open(filepath) as f:    
            self.testCases = json.load(f)
        ns = {'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              'xsd': "http://www.w3.org/2001/XMLSchema#",
              'align':"http://knowledgeweb.semanticweb.org/heterogeneity/alignment#",
              'edoal':'http://ns.inria.org/edoal/1.0/#',
              'ontoA': 'http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A#',
              't'   : 'http://ts.tno.nl/mediator/test#'
              }
        self.nsMgr = namespaces.NSManager(ns, "http://ts.tno.nl/mediator/test#")

         

    def tearDown(self):
        pass

    def testAddQPTRef(self):
        import os
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:name"] == testModuleName]
        print('Testcase: "{}" about {}, has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], len(tests)))
        # Test environment input
        # 1 - Create EntityExpression Class
        # 2 - Set related element_type = SPARQLParser.IRIREF
        # 3 - Value of the element in the query tree
        # 4 - search for proper node in sparql tree
        
        for test in tests:
            print('\tTesting system under test "{}" with {} subtests: {} ({}) ..'.format(self.testCases[test]["mf:SUT"], len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")
            if list(self.testCases[test]["mf:action"]["mf:subject"])[0] != "sparle_query": raise TestException("Invalid test data, expected 'sparle_query', got '{}'".format(list(self.testCases[test]["mf:action"]["mf:subject"])[0]))
            file = self.testdir + self.testCases[test]["mf:action"]["mf:subject"]["sparle_query"]["value"]
            if not os.path.exists(file): raise TestException("Incorrect test data, cannot find file {}".format(file))
            with open(file) as f:
                parsedQry = parseQuery(f.read())
            # Expand the query node to test
            parsedQry.expandIris()
#             print(parsedQry.dump())

            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                # Get the test data, i.e., the sparql_iri and its node in the sparql tree
                sparqlIri = testData["sparql_iri"]["value"]
                sparqlIriValue = self.nsMgr.asIRI(sparqlIri)
                srcNodes = parsedQry.searchElements(element_type=SPARQLParser.iri, value=sparqlIriValue)
                if len(srcNodes) == 0: raise TestException("Incorrect test data, cannot find node of {} in sparql query".format(sparqlIriValue))
                # Create the Entity Element that requires a triple association in the sparql tree
                entity_expr = mediatorTools._Entity(entity_iri=testData["sparql_iri"]["value"], entity_type=EDOALparser.Alignment.EDOAL[testData["EE_type"]["value"]], nsMgr=self.nsMgr)
        
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now the test environment is complete, hence perform the PASS and FAIL tests
                    # Establish the constraints that belong to the variable under test

                    if testCriteria["rdf:type"] == "PASS":
                        # Execute the PASS tests, e.g., get the expected results to compare with
                        filename = testCriteria["value"]
#                         print("filename:\n", filename)
                        with open(self.testdir + filename) as criteria_f:
                            resultsExp = json.load(criteria_f)
                        # Validate the number of QPT's that should be found in this test setup
                        assert len(srcNodes) == int(testData["qptCount"]), "Expected '{}', got '{}'".format(testData["qptCount"], len(srcNodes))
                        
                        # PERFORM THE OPERATION UNDER TEST (init QPTA)
                        qpt = sparqlTools.Context.QueryPatternTripleAssociation(entity_expression=entity_expr, sparql_tree=parsedQry, nsMgr=self.nsMgr)

                        # Test outcome against expected criteria
                        assert qpt.represents == entity_expr, "Expected '{}', got '{}'".format(entity_expr, qpt.represents)
                        # PERFORM THE OPERATION UNDER TEST (now for each srcNode)
                        for count, srcNode in enumerate(srcNodes):
                            qpt.addQPTRef(srcNode)
                            # Test outcome against expected criteria
                            for k, qptCrit in enumerate(resultsExp["results"][sparqlIri]["qpts"]):
                                assert str(qpt.qptRefs[k].about) == entity_expr.getIriRef(), "Expected '{}', got '{}'".format(entity_expr.getIriRef(), qpt.qptRefs[k].about)
                                assert str(qpt.qptRefs[k].about) == qptCrit["n"]["value"], "Expected '{}', got '{}'".format(qptCrit["n"]["value"], qpt.qptRefs[k].about)
                                assert type(qpt.qptRefs[k].about).__name__ == qptCrit["n"]["type"], "Expected '{}', got '{}'".format(qptCrit["n"]["type"],type(qpt.qptRefs[k].about).__name__)
                                print(".", end="")
                                assert qpt.qptRefs[k].type == qptCrit["t"]["value"], "Expected '{}', got '{}'".format(qptCrit["t"]["value"], qpt.qptRefs[k].type)
                                assert str(qpt.qptRefs[k].associates['SUBJ']) == qptCrit["s"]["value"], "Expected '{}', got '{}'".format(qptCrit["s"]["value"], str(qpt.qptRefs[k].associates['SUBJ']))
                                assert type(qpt.qptRefs[k].associates['SUBJ']).__name__ == qptCrit["s"]["type"], "Expected '{}', got '{}'".format(qptCrit["s"]["type"], type(qpt.qptRefs[k].associates['SUBJ']).__name__)
                                assert str(qpt.qptRefs[k].associates['PROP']) == qptCrit["p"]["value"], "Expected '{}', got '{}'".format(qptCrit["p"]["value"], str(qpt.qptRefs[k].associates['PROP']))
                                assert type(qpt.qptRefs[k].associates['PROP']).__name__ == qptCrit["p"]["type"], "Expected '{}', got '{}'".format(qptCrit["p"]["type"], type(qpt.qptRefs[k].associates['PROP']).__name__)
                                assert str(qpt.qptRefs[k].associates['OBJ']) == qptCrit["o"]["value"], "Expected '{}', got '{}'".format(qptCrit["o"]["value"], str(qpt.qptRefs[k].associates['OBJ']))
                                assert type(qpt.qptRefs[k].associates['OBJ']).__name__ == qptCrit["o"]["type"], "Expected '{}', got '{}'".format(qptCrit["o"]["type"], type(qpt.qptRefs[k].associates['OBJ']).__name__)
                                for vb in qpt.qptRefs[k].binds:
                                    assert vb in qptCrit["b"], "Expected '{}', got '{}'".format(qptCrit["b"], vb)   
                        assert len(qpt.qptRefs) == int(resultsExp["results"][sparqlIri]["count"]), "Expected '{}', got '{}'".format(resultsExp["results"][sparqlIri]["count"], len(qpt.qptRefs))
                        print(".", end="")
                        for pfd in qpt.pfdNodes:
                            assert qpt.pfdNodes[pfd]['ns_iriref'] == resultsExp["results"][sparqlIri]["ns"][pfd], "Expected '{}' for prefix '{}', got '{}'".format(resultsExp["results"][sparqlIri]["ns"][pfd], pfd, qpt.pfdNodes[pfd]['ns_iriref'])
                        assert len(qpt.pfdNodes) == len(resultsExp["results"][sparqlIri]["ns"]), "Expected {} nodes, got {}".format(len(resultsExp["results"][sparqlIri]["ns"]), len(qpt.pfdNodes))
                    else: 
                        # Fail scenarios
                        # PERFORM THE OPERATION UNDER TEST
                        try:
                            _= sparqlTools.Context.QueryPatternTripleAssociation(entity_expression=entity_expr, sparql_tree=parsedQry, nsMgr=self.nsMgr)
                            qpt.addQPTRef(srcNodes[0])
                        except Exception as e: assert type(e).__name__ == testCriteria["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"], type(e))
                        print(".", end="")
            print(". done!")

        
    def testGetQPTRef(self):
        assert False, "Create testcase for getQPTRef"


class TestQPTripleRef(unittest.TestCase):
                                        
    def setUp(self):
        self.testdir = './resources/sparqlQueries/'
        filepath = self.testdir + 'manifest02.json'
        print("="*30)
        print("Test configuration from {}:".format(filepath))
        with open(filepath) as f:    
            self.testCases = json.load(f)
        ns = {'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              'xsd': "http://www.w3.org/2001/XMLSchema#",
              'align':"http://knowledgeweb.semanticweb.org/heterogeneity/alignment#",
              'edoal':'http://ns.inria.org/edoal/1.0/#',
              'ontoA': 'http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A',
              't'   : 'http://ts.tno.nl/mediator/test#'
              }
        self.nsMgr = namespaces.NSManager(ns, "http://ts.tno.nl/mediator/test#")

         

    def tearDown(self):
        pass

    def testInit(self):
        import os
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:name"] == testModuleName]
        print('Testcase: "{}" about {}, has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], len(tests)))
        for test in tests:
            print('\tTesting system under test "{}" with {} subtests: {} ({}) ..'.format(self.testCases[test]["mf:SUT"], len(self.testCases[test]["mf:action"]["mf:data"]), self.testCases[test]["rdfs:comment"], self.testCases[test]["mf:name"]), end="")
            # Get the test subject, i.e., the BGP element that this is about
            bgp_type = self.testCases[test]["mf:action"]["mf:subject"]["bgp_type"]
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] != "sparle_query": raise TestException("Invalid test data, expected 'sparle_query', got '{}'".format(testData["rdf:type"]))
                file = self.testdir + testData["value"]
                if not os.path.exists(file): raise TestException("Incorrect test data, cannot find file {}".format(file))
                with open(file) as f:
                    qry = f.read()
                # Get the query node to test
                parsedQry = parseQuery(qry)
#                 print(parsedQry.dump())
#                 print ("searching: {}".format(bgp_type))
                query_nodes = parsedQry.searchElements(label = None, element_type=SPARQLParser.iri if bgp_type["rdf:type"]=="iri" else SPARQLParser.Var, value=bgp_type["value"])
#                 print("found: {}".format(len(query_nodes)))
                assert len(query_nodes) > 0

                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now the test environment is complete, hence perform the PASS and FAIL tests
                    # Establish the constraints that belong to the variable under test

                    if testCriteria["rdf:type"] == "PASS":
                        # Execute the PASS tests, e.g., get the expected results to compare with
                        filename = testCriteria["value"]
#                         print("filename:\n", filename)
                        with open(self.testdir + filename) as criteria_f:
                            resultsExp = json.load(criteria_f)
                        # PERFORM THE OPERATION UNDER TEST
                        atom = query_nodes[0].descend()
                        if not query_nodes[0].descend().isAtom(): raise TestException("Test for class QPTripleRef should find atom, but found {}".format(query_nodes[0]))
                        theNode = sparqlTools.Context.QueryPatternTripleAssociation.QPTripleRef(about=query_nodes[0])
                        # Test outcome against expected criteria
                        assert theNode.about == atom
                        assert str(theNode.about) == resultsExp["results"]["bindings"][0]["o"]["value"]
                        assert type(theNode.about).__name__ == resultsExp["results"]["bindings"][0]["o"]["type"]
                        print(".", end="")
                        theNode.setType(self.testCases[test]["mf:action"]["mf:subject"]["bgp_value"]["value"])
                        assert theNode.type == resultsExp["results"]["bindings"][0]["t"]["value"]
                        assert len(theNode.associates) == int(resultsExp["results"]["bindings"][0]["l"]["value"])
                        assert theNode.associates[theNode.type] == atom
                        assert len(theNode.binds) == int(resultsExp["results"]["bindings"][0]["b"]["value"])
                        print(".", end="")

            print(". done!")

        
    def testConsiderBinding(self):
        assert False, "Create testcase for considerBinding"
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testQPTripleRefs']
    unittest.main()