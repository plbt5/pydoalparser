'''
Created on 29 apr. 2016

@author: brandtp
'''
import unittest
from test.mytestexceptions import TestException
from parsertools.parsers.sparqlparser import SPARQLParser, parseQuery
import inspect
import json
from mediator import sparqlTools, mediatorTools
from utilities import namespaces
from itertools import zip_longest
from mediator.sparqlTools import isSparqlResult, isSparqlQuery


# Skeleton for a manifest.json driven test process
#
#     def setUp(self):
#         self.testdir = './resources/sparqlQueries/'
#         filepath = self.testdir + 'manifestXX.json'
#         print("="*30)
#         print("Test configuration from {}:".format(filepath))
#         with open(filepath) as f:    
#             self.testCases = json.load(f)
# 
#     def testSomeModuleName(self):
#         # According to test_type04 in manifest
#         testModuleName = inspect.currentframe().f_code.co_name
#         tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:testDef"] == testModuleName]
#         print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
#         for test in tests:
#             print('\t* {}: Testing {}.{} ({}): '.format(test, self.testCases[test]["mf:class"], self.testCases[test]["mf:SUT"], self.testCases[test]["rdfs:comment"]), end="")
#             for testData in self.testCases[test]["mf:action"]["mf:data"]:
#                 if testData["rdf:type"] == "file": 
#                     file = self.testdir + testData["value"]
#                     with open(file) as f:
#                         testString = f.read()
#                 elif testData["rdf:type"] == "string" or testData["rdf:type"] == "dict":
#                     testString = testData["value"]
#                 elif testData["rdf:type"] == "none":
#                     testString = None                
#                 else: raise TestException("Incorrect test data, expected 'file' or 'string', got {}".format(testData["rdf:type"]))
#                 for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
#                     # Now adapt the test environment to the PASS or FAIL tests
#                     if testCriteria["rdf:type"] == "PASS":
#                         # Get the test criterion from file
#                         file = self.testdir + testCriteria["value"]
#                         with open(file) as f:
#                             testCriterion = json.load(f)
#                         
#                         # Execute the PASS tests
#                         # PERFORM THE OPERATION UNDER TEST
#                         call me here
#                         # Assert its validity
#                         assert blahblahblah -- this is test dependent
#                     elif testCriteria["rdf:type"] == "FAIL": 
#                         # Fail scenarios
#                         # Get the test criterion, i.e., the exception name that should be thrown
#                         # PERFORM THE OPERATION UNDER TEST
#                         try:
#                             # Do the (failing) test call, and assert the correct exception is thrown
#                             call me here
#                             raise TestException("{}: failed the test, expected call to FAIL but it survived".format(testModuleName))
#                         except Exception as e: assert type(e).__name__ == testCriteria["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"], type(e))
#                     else: raise TestException("Incorrect test criterion, expected 'PASS' or 'FAIL', got {}".format(testData["rdf:type"]))
#                     print(".", end="")
#             print(". done!")




class TestVarConstraints(unittest.TestCase):


    def setUp(self):
        self.testdir = './resources/sparqlQueries/sparqlTools/'
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
    '''
    Test the creation of a complete QPTAssoc around one EntityExpression. A QPTAssoc contains:
            represents = '' # (EntityExpression) the EDOAL entity_iri (Class, Property, Relation, Instance) name;
            qptRefs = []    # List of (QPTripleRef)s, i.e., Query Pattern nodes that address the Entity Expression
            pfdNodes = {}   # Temporary namespace dictionary. Dict of (ParseStruct)s indexed by prefix : the PrefixDecl nodes that this entity_iri relates to
            sparqlTree = '' # The sparql tree that this class uses to relate to

    '''
                                        
    def setUp(self):
        self.testdir = './resources/sparqlQueries/sparqlTools/'
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

    def testAddQPTRefs(self):
        import os
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:testDef"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        # Test environment input
        # 1 - Create EntityExpression Class
        # 2 - Set related element_type = SPARQLParser.IRIREF
        # 3 - Value of the element in the query tree
        # 4 - search for proper node in sparql tree
        
        for test in tests:
            print('\t* {}: Testing {}.{} ({}): '.format(test, self.testCases[test]["mf:class"], self.testCases[test]["mf:SUT"], self.testCases[test]["rdfs:comment"]), end="")
            if list(self.testCases[test]["mf:action"]["mf:subject"])[0] != "sparle_query": raise TestException("Invalid test data, expected 'sparle_query', got '{}'".format(list(self.testCases[test]["mf:action"]["mf:subject"])[0]))
            file = self.testdir + self.testCases[test]["mf:action"]["mf:subject"]["sparle_query"]["value"]
            if not os.path.exists(file): raise TestException("Incorrect test data, cannot find file {}".format(file))
            with open(file) as f:
                parsedQry = parseQuery(f.read())
#             print(parsedQry.dump())
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
                entity_expr = mediatorTools._Entity(entity_iri=sparqlIri, entity_type=EDOALparser.Alignment.EDOAL[testData["EE_type"]["value"]], nsMgr=self.nsMgr)
        
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now the test environment is complete, hence perform the PASS and FAIL tests
                    # Establish the constraints that belong to the variable under test

                    if testCriteria["rdf:type"] == "PASS":
                        # Execute the PASS tests, e.g., get the expected results to compare with
                        filename = testCriteria["value"]
#                         print("filename:\n", filename)
                        with open(self.testdir + filename) as criteria_f:
                            re = json.load(criteria_f)
                            resultsExp = re["results"]
                        # Validate the number of QPT's that should be found in this test setup
                        assert len(srcNodes) == int(testData["qptCount"]), "Expected '{}', got '{}'".format(testData["qptCount"], len(srcNodes))
                        
                        # PERFORM THE OPERATION UNDER TEST (init QPTA)
                        qpt = sparqlTools.Context.QueryPatternTripleAssociation(entity=entity_expr, sparql_tree=parsedQry, nsMgr=self.nsMgr)

                        # Test outcome against expected criteria
                        assert qpt.represents == entity_expr, "Expected '{}', got '{}'".format(entity_expr, qpt.represents)
                        # PERFORM THE OPERATION UNDER TEST (now for each srcNode)
                        for count, srcNode in enumerate(srcNodes):
                            qpt.addQPTRefs(srcNode)
                            # Test outcome against expected criteria
                            for k, qptCrit in enumerate(resultsExp[sparqlIri]["qpts"]):
                                print("{}({})".format(testData["id"],k), end=" ")
                                assert len(qpt.qptRefs) == int(resultsExp[sparqlIri]["count"]), "Expected '{}', got '{}'".format(resultsExp[sparqlIri]["count"], len(qpt.qptRefs))
                                assert str(qpt.qptRefs[k].referred) == entity_expr.getIriRef(), "Expected '{}', got '{}'".format(entity_expr.getIriRef(), qpt.qptRefs[k].referred)
                                assert str(qpt.qptRefs[k].referred) == qptCrit["n"]["value"], "Expected '{}', got '{}'".format(qptCrit["n"]["value"], qpt.qptRefs[k].referred)
                                assert type(qpt.qptRefs[k].referred).__name__ == qptCrit["n"]["type"], "Expected '{}', got '{}'".format(qptCrit["n"]["type"],type(qpt.qptRefs[k].referred).__name__)
                                assert qpt.qptRefs[k].type == qptCrit["t"]["value"], "Expected '{}', got '{}'".format(qptCrit["t"]["value"], qpt.qptRefs[k].type)
                                assert str(qpt.qptRefs[k].associates['SUBJ']) == qptCrit["s"]["value"], "Expected '{}', got '{}'".format(qptCrit["s"]["value"], str(qpt.qptRefs[k].associates['SUBJ']))
                                assert type(qpt.qptRefs[k].associates['SUBJ']).__name__ == qptCrit["s"]["type"], "Expected '{}', got '{}'".format(qptCrit["s"]["type"], type(qpt.qptRefs[k].associates['SUBJ']).__name__)
                                assert str(qpt.qptRefs[k].associates['PROP']) == qptCrit["p"]["value"], "Expected '{}', got '{}'".format(qptCrit["p"]["value"], str(qpt.qptRefs[k].associates['PROP']))
                                assert type(qpt.qptRefs[k].associates['PROP']).__name__ == qptCrit["p"]["type"], "Expected '{}', got '{}'".format(qptCrit["p"]["type"], type(qpt.qptRefs[k].associates['PROP']).__name__)
                                assert str(qpt.qptRefs[k].associates['OBJ']) == qptCrit["o"]["value"], "Expected '{}', got '{}'".format(qptCrit["o"]["value"], str(qpt.qptRefs[k].associates['OBJ']))
                                assert type(qpt.qptRefs[k].associates['OBJ']).__name__ == qptCrit["o"]["type"], "Expected '{}', got '{}'".format(qptCrit["o"]["type"], type(qpt.qptRefs[k].associates['OBJ']).__name__)
                                for vb in qpt.qptRefs[k].binds:
                                    assert vb in qptCrit["b"], "Expected '{}', got '{}'".format(qptCrit["b"], vb)   
                        assert len(qpt.qptRefs) == int(resultsExp[sparqlIri]["count"]), "Expected '{}', got '{}'".format(resultsExp[sparqlIri]["count"], len(qpt.qptRefs))
                        print(".", end="")
                        for pfd in qpt.pfdNodes:
                            assert qpt.pfdNodes[pfd]['ns_iriref'] == resultsExp[sparqlIri]["ns"][pfd], "Expected '{}' for prefix '{}', got '{}'".format(resultsExp[sparqlIri]["ns"][pfd], pfd, qpt.pfdNodes[pfd]['ns_iriref'])
                        assert len(qpt.pfdNodes) == len(resultsExp[sparqlIri]["ns"]), "Expected {} nodes, got {}".format(len(resultsExp[sparqlIri]["ns"]), len(qpt.pfdNodes))
                    else: 
                        # Fail scenarios
                        # PERFORM THE OPERATION UNDER TEST
                        try:
                            qpt = sparqlTools.Context.QueryPatternTripleAssociation(entity=entity_expr, sparql_tree=parsedQry, nsMgr=self.nsMgr)
                            qpt.addQPTRefs(srcNodes[0])
                            raise TestException("{}: failed the test, expected call to raise '{}' but it survived".format(testModuleName, testCriteria["value"]))
                        except Exception as e: assert type(e).__name__ == testCriteria["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"], type(e))
                        print(".", end="")
            print(". done!")




class TestQPTripleRef(unittest.TestCase):
                                        
    def setUp(self):
        self.testdir = './resources/sparqlQueries/sparqlTools/'
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
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:testDef"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        for test in tests:
            print('\t* {}: Testing {}.{} ({}): '.format(test, self.testCases[test]["mf:class"], self.testCases[test]["mf:SUT"], self.testCases[test]["rdfs:comment"]), end="")
            # Get the test subject, i.e., the BGP element that this is about
            testSubject = self.testCases[test]["mf:action"]["mf:subject"]
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
                if testSubject["bgp_referred"]["rdf:type"]=="iri": elType=SPARQLParser.iri
                elif testSubject["bgp_referred"]["rdf:type"] in ["VAR1","VAR2"]: elType=SPARQLParser.Var
                query_nodes = parsedQry.searchElements(label = None, element_type=elType, value=testSubject["bgp_referred"]["value"])
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
                            re = json.load(criteria_f)
                            resultsExp = re["results"]
                        atom = query_nodes[0].descend()
                        if not query_nodes[0].descend().isAtom(): raise TestException("Test for class QPTripleRef should find atom, but found {}".format(query_nodes[0]))
                        # PERFORM THE OPERATION UNDER TEST
                        theNode = sparqlTools.Context.QueryPatternTripleAssociation.QPTripleRef()
                        theNode.addReferred(referred=query_nodes[0], bgp_type=testSubject["bgp_position"]["value"])
                        # Test outcome against expected criteria
                        assert theNode.referred == atom, "Test failure: Expected '{}', got '{}'".format(repr(atom),repr(theNode.referred))
                        assert str(theNode.referred) == resultsExp["bindings"][0]["o"]["value"]
                        assert type(theNode.referred).__name__ == resultsExp["bindings"][0]["o"]["type"]
                        assert theNode.type == resultsExp["bindings"][0]["t"]["value"]
                        assert resultsExp["bindings"][0]["t"]["value"] in theNode.associates
                        assert len(theNode.associates) == int(resultsExp["bindings"][0]["l"]["value"])
                        assert theNode.associates[resultsExp["bindings"][0]["t"]["value"]] == atom
                        assert len(theNode.binds) == int(resultsExp["bindings"][0]["b"]["value"])
                        print(".", end="")

            print(". done!")


        

class TestContext(unittest.TestCase):
    '''
    Test the creation of a complete context around one EntityExpression. A context contains:
        entity_expr = ''    # (mediator.mediatorTools.EntityExpression) The EDOAL entity_expression, i.e., one of (Class, Property, Relation, Instance) or their combinations, this context is about;
        parsedQuery = ''    # (parser.grammar.ParseInfo) The parsed query that is to be mediated
        qptAssocs = []      # List of (QueryPatternTripleAssociation)s, representing the triples that are addressing the subject entity_expression
        constraints = {}    # Dictionary, indexed by the bound variables that occur in the qptAssocs, as contextualised Filters.
        nsMgr = None        # (namespaces.NSManager): the current nsMgr that can resolve any namespace issues of this mediator 
    '''

    def setUp(self):
        self.testdir = './resources/sparqlQueries/sparqlTools/'
        filepath = self.testdir + 'manifest05.json'
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
    
 
    def testInit(self):
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:testDef"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        for test in tests:
            print('\t* {}: Testing {}.{} ({}): '.format(test, self.testCases[test]["mf:class"], self.testCases[test]["mf:SUT"], self.testCases[test]["rdfs:comment"]), end="")
            # Create the subject
            subject = self.testCases[test]["mf:action"]["mf:subject"][0]
            if subject["rdf:type"] == "iri_ref":
                srcEE = mediatorTools.EProperty(entity_iri=subject["value"], nsMgr=self.nsMgr)
            else:
                raise TestException("Incorrect test subject type, expected 'iri_ref', got {}".format(subject["rdf:type"]))
            # Loop over the test data
            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] == "file": 
                    file = self.testdir + testData["value"]
                    with open(file) as f:
                        testString = f.read()
                elif testData["rdf:type"] == "string":
                    testString = testData["value"]
                else: raise TestException("Incorrect test data, expected 'file' or 'string', got {}".format(testData["rdf:type"]))
                parsed_data = parseQuery(testString)
#                 print(parsed_data.dump())
                parsed_data.expandIris()
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    print(testCriteria["id"], end=" ")
                    # Now adapt the test environment to the PASS or FAIL tests
                    if testCriteria["rdf:type"] == "PASS":
                        # Get the test criterion from file
                        file = self.testdir + testCriteria["value"]
                        with open(file) as f:
                            testCriterion = json.load(f)
                         
                        # Execute the PASS tests
                        # PERFORM THE OPERATION UNDER TEST
                        context = sparqlTools.Context(entity_expression=srcEE, entity_type=SPARQLParser.iri, sparqlTree=parsed_data, nsMgr=self.nsMgr)
                        # Assert its validity
                        # 1 - Assert the triples in the Context
                        assert context.entity_expr == srcEE, "Test failure: Expected '{}', got '{}'".format(str(srcEE),str(context.entity_expr))
                        assert len(context.qptAssocs[srcEE.getIriRef()].qptRefs) == len(testCriterion["results"]["bindings"]), "Expected {}, got {}".format(len(testCriterion["results"]["bindings"]), len(context.qptAssocs[srcEE.getIriRef()].qptRefs))
                        for i, qptref in enumerate(context.qptAssocs[srcEE.getIriRef()].qptRefs):
#                             print("Triple results {}  : {}".format(i,str(qptref)))
#                             print("  test criterion {}: {}".format(i,testCriterion["results"]["bindings"][i]))
                            assert sparqlTools.Context.localLabels['subject'] in qptref.associates
                            assert str(qptref.associates[sparqlTools.Context.localLabels['subject']]) == testCriterion["results"]["bindings"][i]["s"]["value"], \
                                "expected '{}', got '{}'".format(testCriterion["results"]["bindings"][i]["s"]["value"], str(qptref.associates[sparqlTools.Context.localLabels['subject']]))
                            assert sparqlTools.Context.localLabels['property'] in qptref.associates
                            assert str(qptref.associates[sparqlTools.Context.localLabels['property']]) == testCriterion["results"]["bindings"][i]["p"]["value"], \
                                "expected '{}', got '{}'".format(testCriterion["results"]["bindings"][i]["p"]["value"], str(qptref.associates[sparqlTools.Context.localLabels['property']]))
                            assert sparqlTools.Context.localLabels['object'] in qptref.associates
                            assert str(qptref.associates[sparqlTools.Context.localLabels['object']]) == testCriterion["results"]["bindings"][i]["o"]["value"], \
                                "expected '{}', got '{}'".format(testCriterion["results"]["bindings"][i]["o"]["value"], str(qptref.associates[sparqlTools.Context.localLabels['object']]))
                        # 2 - Assert the constraints in the Context
                        for var, varConstraints in context.constraints.items():
#                             print("Contraints result ['{}']: {}".format(var, varConstraints))
                            assert var in testCriterion["results"]["constraints"], "'{}' not in '{}'".format(var, (key for key in testCriterion["results"]["constraints"]))
#                             print ("  test criterion ['{}']: {}".format(var,testCriterion["results"]["constraints"][var]))
                            for varConstraint in varConstraints:
                                if len(testCriterion["results"]["constraints"][var]) > 0 or len(varConstraint._valueLogicExprList) > 0:
                                    assert varConstraint.getBoundVar() == var
                                    assert len(varConstraint.getValueLogicExpressions()) == len(testCriterion["results"]["constraints"][var])
                                    for vle in varConstraint.getValueLogicExpressions():
                                        vleExpanded = {
                                            "varRef"     : {"type": type(vle["varRef"]).__name__, "value": str(vle["varRef"]) } ,
                                            "comparator" : {"type": type(vle["comparator"]).__name__, "value": str(vle["comparator"]) } ,
                                            "restriction": {"type": type(vle["restriction"]).__name__, "value": str(vle["restriction"]) } 
                                        }
                                        assert vleExpanded in testCriterion["results"]["constraints"][var], "Test failed: created a value logic expression that was not expected: \n{}".format(vle)

                    elif testCriteria["rdf:type"] == "FAIL": 
                        # FAIL SCENARIONS
                        # Fail scenarios come in 2 variations:
                        # 1 - Throwing an error. For this kind it is only asserted that the correct error has been thrown
                        #TODO: extend the verification to also assert on the text of the  thrown error.
                        # 2 - Throwing a warning only, but continuing the process. Now the results of the call are asserted, similarly  to a PASS test. 
                        # Get the test criterion, i.e., the exception name that should be thrown
                        # PERFORM THE OPERATION UNDER TEST 
                        
                        # But, first check the test type, in order to know how to interpret the test result.
                        if self.testCases[test]["rdf:type"] == "testType02":
                            if testCriteria["value"]["rdf:type"] == "error":
                                try:
                                    # Do the (failing) test call, and assert the correct exception is thrown
                                    context = sparqlTools.Context(entity_expression=srcEE, entity_type=SPARQLParser.iri, sparqlTree=parsed_data, nsMgr=self.nsMgr)
                                    raise TestException("{}: failed the test, expected call to raise '{}' but it survived".format(testModuleName, testCriteria["value"]["value"]))
                                except Exception as e: assert type(e).__name__ == testCriteria["value"]["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"]["value"], type(e))
                            elif testCriteria["value"]["rdf:type"] == "file":
                                file = self.testdir + testCriteria["value"]["value"]
                                with open(file) as f:
                                    testCriterion = json.load(f)
                                # Do the (failing) test call, and assert the correct exception is thrown
                                context = sparqlTools.Context(entity_expression=srcEE, entity_type=SPARQLParser.iri, sparqlTree=parsed_data, nsMgr=self.nsMgr)
                                for i, binding in enumerate(testCriterion["results"]["bindings"]):
                                    assert context.entity_expr == srcEE, "Test failure: expected '{}', got '{}'.".format(str(srcEE),str(context.entity_expr))
                                    assert context.qptAssocs == binding["assocs"], "Test failure: expected '{}', got '{}'.".format(binding["assocs"], context.qptAssocs)
                                    assert context.constraints == binding["constraints"], "Test failure: expected '{}', got '{}'.".format(binding["constraints"], context.constraints)
                            else: raise TestException("Incorrect test criterion, expected 'File' or 'error', got {}".format(testCriteria["value"]["rdf:type"]))
                        else: raise TestException("Incorrect test type, expected 'testType02', got {}".format(testCriteria["value"]["rdf:type"]))
                    else: raise TestException("Incorrect test criterion, expected 'PASS' or 'FAIL', got {}".format(testCriteria["value"]["rdf:type"]))
                    print(".", end="")
            print(". done!")



class TestSparqlQueryResultSet(unittest.TestCase):
                                        
    def setUp(self):
        self.testdir = './resources/sparqlQueries/'
        filepath = self.testdir + 'manifest04.json'
        print("="*30)
        print("Test configuration from {}:".format(filepath))
        with open(filepath) as f:    
            self.testCases = json.load(f)
         

    def tearDown(self):
        pass

    def testInit(self):
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:testDef"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        for test in tests:
            print('\t* {}: Testing {}.{} ({}): '.format(test, self.testCases[test]["mf:class"], self.testCases[test]["mf:SUT"], self.testCases[test]["rdfs:comment"]), end="")

            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] == "file": 
                    file = self.testdir + testData["value"]
                    with open(file) as f:
                        testString = f.read()
                elif testData["rdf:type"] == "string" or testData["rdf:type"] == "dict":
                    testString = testData["value"]
                else: raise TestException("Incorrect test data, expected 'file', 'dict' or 'string', got '{}'".format(testData["rdf:type"]))
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now adapt the test environment to the PASS or FAIL tests
                    if testCriteria["rdf:type"] == "PASS":
                        # Get the test criterion from file
                        file = self.testdir + testCriteria["value"]
                        with open(file) as f:
                            testCriterion = json.load(f)
#                         print("test criterion: {}".format(testCriterion))
                        
                        # Execute the PASS tests
                        # PERFORM THE OPERATION UNDER TEST
                        resultSet = sparqlTools.SparqlQueryResultSet(testString)
                        # Assert its validity
                        assert resultSet.qType == testCriterion["qType"], "Expected '{}', got '{}'".format(testCriterion["qType"], resultSet.qType)
                        if testCriterion["qType"] == sparqlTools.queryForm.select:
                            assert resultSet.isResponseToSELECT(), "Expected True, got False"
                            assert not resultSet.isResponseToASK(), "Expected False, got True"
                            assert resultSet.getVars() == testCriterion["vars"], "Expected '{}', got '{}'".format(testCriterion["vars"], resultSet.vars)
                            assert len(resultSet) == len(testCriterion["bindings"]), "Expected {}, got length {}".format(len(testCriterion["bindings"]), len(resultSet))
                            assert resultSet.getBindings() == testCriterion["bindings"], "Expected '{}', got '{}'".format(testCriterion["bindings"], resultSet.bindings)
                        elif testCriterion["qType"] == sparqlTools.queryForm.ask:
                            assert resultSet.isResponseToASK(), "Expected True, got False"
                            assert not resultSet.isResponseToSELECT(), "Expected False, got True"
                            assert len(resultSet) == 1, "Expected 1, got length {}".format(len(resultSet))
                            assert resultSet.hasSolution() == testCriterion["boolean"], "Expected '{}', got '{}'".format(testCriterion["boolean"], resultSet.hasSolution())
                        else: raise TestException("{}: only support result sets from 'ASK' or 'SELECT' queries, got '{}'".format(testModuleName, testCriterion["qType"]))
                    elif testCriteria["rdf:type"] == "FAIL": 
                        # Fail scenarios
                        # Get the test criterion, i.e., the exception name that should be thrown
                        # PERFORM THE OPERATION UNDER TEST
                        
                        # But, first check the test type, in order to know how to interpret the test result.
                        if self.testCases[test]["rdf:type"] == "testType01":
                            try:
                                # Do the (failing) test call, and assert the correct exception is thrown
                                _ = sparqlTools.SparqlQueryResultSet(testString)
                                raise TestException("{}: failed the test, expected call to FAIL but it survived".format(testModuleName))
                            except Exception as e: assert type(e).__name__ == testCriteria["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"], type(e))
                        elif self.testCases[test]["rdf:type"] == "testType02":
                            if testCriteria["value"]["rdf:type"] == "error":
                                try:
                                    _ = sparqlTools.SparqlQueryResultSet(testString)
                                    raise TestException("{}: Test failure, expected call to raise '{}' but it survived".format(testModuleName, testCriteria["value"]["value"]))
                                except Exception as e: assert type(e).__name__ == testCriteria["value"]["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"]["value"], type(e))
                            elif testCriteria["value"]["rdf:type"] == "file":
                                file = self.testdir + testCriteria["value"]["value"]
                                with open(file) as f:
                                    testCriterion = json.load(f)
                                # Do the (failing) test call, and assert the correct exception is thrown
                                sqrs = sparqlTools.SparqlQueryResultSet(testString)
                                for i, binding in enumerate(testCriterion["results"]["bindings"]):
                                    # Do your assertions
                                    pass
                            else: raise TestException("Incorrect test criterion, expected 'File' or 'error', got {}".format(testCriteria["value"]["rdf:type"]))
                        else: raise TestException("Incorrect test type, expected 'testType01', got '{}'".format(self.testCases[test]["rdf:type"]))
                    else: raise TestException("Incorrect test criterion, expected 'PASS' or 'FAIL', got '{}'".format(testData["rdf:type"]))
                    print(".", end="")
            print(". done!")

    def testIsSparqlResult(self):
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:testDef"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        for test in tests:
            print('\t* {}: Testing {}.{} ({}): '.format(test, self.testCases[test]["mf:class"], self.testCases[test]["mf:SUT"], self.testCases[test]["rdfs:comment"]), end="")

            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] == "file": 
                    file = self.testdir + testData["value"]
                    if file[-1] == 'j':
                        # Assume a json file ('.srj')
                        with open(file) as f:
                            testString = json.load(f)
                    else:
                        # Assume an xml file, hence a string as result
                        with open(file) as f:
                            testString = f.read()
                elif testData["rdf:type"] == "string" or testData["rdf:type"] == "dict":
                    testString = testData["value"]
                elif testData["rdf:type"] == "none":
                    testString = None                
                else: raise TestException("Incorrect test data, expected 'file', 'dict' or 'string', got '{}'".format(testData["rdf:type"]))
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now adapt the test environment to the PASS or FAIL tests
                    if testCriteria["rdf:type"] == "PASS":
                        # Get the test criterion from file
                        testCriterion = (testCriteria["value"] == "True")
#                         print("test input: {}".format(testString))
#                         print("test criterion: {}".format(testCriterion))
                        
                        # Execute the PASS tests
                        # PERFORM THE OPERATION UNDER TEST
                        assert isSparqlResult(testString) == testCriterion, "Expected '{}', got '{}'".format(testCriterion, isSparqlResult(testString))
                    elif testCriteria["rdf:type"] == "FAIL": 
                        # Fail scenarios
                        # Get the test criterion, i.e., the exception name that should be thrown
                        # PERFORM THE OPERATION UNDER TEST
                        
                        # But, first check the test type, in order to know how to interpret the test result.
                        if self.testCases[test]["rdf:type"] == "testType01":
                            try:
                                # Do the (failing) test call, and assert the correct exception is thrown
                                _ = isSparqlResult(testString)
                                raise TestException("{}: failed the test, expected call to FAIL but it survived".format(testModuleName))
                            except Exception as e: assert type(e).__name__ == testCriteria["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"], type(e))
#                         elif self.testCases[test]["rdf:type"] == "testType02":
#                             if testCriteria["value"]["rdf:type"] == "error":
#                                 try:
#                                     _ = isSparqlResult(testString)
#                                     raise TestException("{}: Test failure, expected call to raise '{}' but it survived".format(testModuleName, testCriteria["value"]["value"]))
#                                 except Exception as e: assert type(e).__name__ == testCriteria["value"]["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"]["value"], type(e))
#                             elif testCriteria["value"]["rdf:type"] == "file":
#                                 file = self.testdir + testCriteria["value"]["value"]
#                                 with open(file) as f:
#                                     testCriterion = json.load(f)
#                                 # Do the (failing) test call, and assert the correct exception is thrown
#                                 sqrs = sparqlTools.SparqlQueryResultSet(testString)
#                                 for i, binding in enumerate(testCriterion["results"]["bindings"]):
#                                     # Do your assertions
#                                     pass
#                             else: raise TestException("Incorrect test criterion, expected 'File' or 'error', got {}".format(testCriteria["value"]["rdf:type"]))
                        else: raise TestException("Incorrect test type, expected 'testType01', got '{}'".format(self.testCases[test]["rdf:type"]))
                    else: raise TestException("Incorrect test criterion, expected 'PASS' or 'FAIL', got '{}'".format(testData["rdf:type"]))
                    print(".", end="")
            print(". done!")


    def testIsSparqlQuery(self):
        testModuleName = inspect.currentframe().f_code.co_name
        tests = [entry for entry in self.testCases["mf:entries"] if self.testCases[entry]["mf:testDef"] == testModuleName]
        print('Testcase: "{}" about {}, module under test "{}" has {} tests'.format(self.testCases["manifest"]["mf:name"], self.testCases["manifest"]["rdfs:comment"], testModuleName, len(tests)))
        for test in tests:
            print('\t* {}: Testing {}.{} ({}): '.format(test, self.testCases[test]["mf:class"], self.testCases[test]["mf:SUT"], self.testCases[test]["rdfs:comment"]), end="")

            for testData in self.testCases[test]["mf:action"]["mf:data"]:
                if testData["rdf:type"] == "file": 
                    file = self.testdir + testData["value"]
                    with open(file) as f:
                        testString = f.read()
                elif testData["rdf:type"] == "string" or testData["rdf:type"] == "dict":
                    testString = testData["value"]
                elif testData["rdf:type"] == "none":
                    testString = None
                elif testData["rdf:type"] == "integer":
                    testString = int(testData["value"])            
                else: raise TestException("Incorrect test data, expected 'file', 'dict' or 'string', got '{}'".format(testData["rdf:type"]))
                for testCriteria in [r for r in self.testCases[test]["mf:result"] if r["id"]==testData["id"]]:
                    # Now adapt the test environment to the PASS or FAIL tests
                    if testCriteria["rdf:type"] == "PASS":
                        # Get the test criterion from file
                        testCriterion = (testCriteria["value"] == "True")
#                         print("test input data: {}".format(testString))
#                         print("test criterion: {}".format(testCriterion))
                        
                        # Execute the PASS tests
                        # PERFORM THE OPERATION UNDER TEST
                        assert isSparqlQuery(testString) == testCriterion, "Expected '{}', got '{}'".format(testCriterion, isSparqlQuery(testString))
                    elif testCriteria["rdf:type"] == "FAIL": 
                        # Fail scenarios
                        # Get the test criterion, i.e., the exception name that should be thrown
                        # PERFORM THE OPERATION UNDER TEST
                        
                        # But, first check the test type, in order to know how to interpret the test result.
                        if self.testCases[test]["rdf:type"] == "testType01":
                            try:
                                # Do the (failing) test call, and assert the correct exception is thrown
                                _ = isSparqlQuery(testString)
                                raise TestException("{}: failed the test, expected call to FAIL but it survived".format(testModuleName))
                            except Exception as e: assert type(e).__name__ == testCriteria["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"], type(e))
#                         elif self.testCases[test]["rdf:type"] == "testType02":
#                             if testCriteria["value"]["rdf:type"] == "error":
#                                 try:
#                                     _ = isSparqlResult(testString)
#                                     raise TestException("{}: Test failure, expected call to raise '{}' but it survived".format(testModuleName, testCriteria["value"]["value"]))
#                                 except Exception as e: assert type(e).__name__ == testCriteria["value"]["value"], "Expected exception '{}', got '{}'".format(testCriteria["value"]["value"], type(e))
#                             elif testCriteria["value"]["rdf:type"] == "file":
#                                 file = self.testdir + testCriteria["value"]["value"]
#                                 with open(file) as f:
#                                     testCriterion = json.load(f)
#                                 # Do the (failing) test call, and assert the correct exception is thrown
#                                 sqrs = sparqlTools.SparqlQueryResultSet(testString)
#                                 for i, binding in enumerate(testCriterion["results"]["bindings"]):
#                                     # Do your assertions
#                                     pass
#                             else: raise TestException("Incorrect test criterion, expected 'File' or 'error', got {}".format(testCriteria["value"]["rdf:type"]))
                        else: raise TestException("Incorrect test type, expected 'testType01', got '{}'".format(self.testCases[test]["rdf:type"]))
                    else: raise TestException("Incorrect test criterion, expected 'PASS' or 'FAIL', got '{}'".format(testData["rdf:type"]))
                    print(".", end="")
            print(". done!")
         


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testQPTripleRefs']
    unittest.main()