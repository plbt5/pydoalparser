'''
Created on 21 apr. 2016

@author: brandtp
'''
import unittest
from test.mytestexceptions import TestException
from mediator.EDOALparser import ParseAlignment
import xml.etree.ElementTree as etree
from utilities.namespaces import NSManager


class TestNSManager(unittest.TestCase):


    def setUp(self):
        self.testCases = {}
        # Edoal parsing tests
        '''
        The admin tests will check the edoal Alignment element (refer to http://alignapi.gforge.inria.fr/format.html), however, restricted to:
        * <xml>: (value: "yes"/"no") indicates if the alignment can be read as an XML file compliant with the DTD;
        * <level>: (values: "0", "1", "2EDOAL") the level of alignment, characterising its type;
        * <type>: (values: "11"/"1?"/"1+"/"1*"/"?1"/"??"/"?+"/"?*"/"+1"/"+?"/"++"/"+*"/"*1"/"*?"/"?+"/"**"; default "11") 
            This represents the arity of alignment. Usual notations are 1:1, 1:m, n:1 or n:m. We prefer to note if the mapping is injective, 
            surjective and total, or partial on both sides. We then end up with more alignment arities:
            . 1 for injective and total, 
            . ? for injective, 
            . + for total and 
            . * for none
            and each sign concerning one mapping and its converse;
        * <onto1> and <onto2>: (value: Ontology) the source and target ontologies that are being aligned;
        '''
        
        self.testCases['ADMIN'] = []
        self.testCases['ADMIN'].append(
            { 
            'pass': {'resources/alignPassSimple0.xml':                      # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-EQ-Reln
                      {'about': 'http://ds.tno.nl/ontoA-ontoB/CPR-EQ-CPR', 
                       'admin': ['yes', 'PaulBrandt', '2015/08/25', 'manual', 'TEST DATA (simple alignments)', '2EDOAL', '?*'],
                       'ontoS': ["http://tutorial.topbraid.com/ontoA#", None, "http://www.w3.org/2002/07/owl#", "OWL1.0"],
                       'ontoT': ["http://tutorial.topbraid.com/ontoB#", "resources/nl/test1/ontoB.xml", "http://www.w3.org/2002/07/owl#", "OWL1.0"]
                       },
                     'resources/wine_align.xml':                            # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-LT-Reln,
                      {'about': 'http://oms.omwg.org/wine-vin/',            #   & one SmplSrcCls-EQ-CmplxTgtCls, one CmpxlSrcCls-LT-CmplxTgtCls
                       'admin': ['yes', 'http://www.scharffe.fr/foaf.rdf', '2006/06/07', 'manual', 'TESTcase: hugely adapted from original wine-vin example', '2EDOAL', '**'],
                       'ontoS': ["http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#", None, "http://www.w3.org/TR/owl-guide/", "owl"],
                       'ontoT': ["http://ontology.deri.org/vin#", "http://www.scharffe.fr/ontologies/OntologieDuVin.wsml", "http://www.wsmo.org/wsml/wsml-syntax/wsml-dl", "wsml"]
                    }
                },
            'fail': [['resources/alignFail0A.xml', RuntimeError],          # Missing <Alignment> element
                    ['resources/alignFail0B.xml', ValueError],             # Missing 'alignET:about="somename"' in <Alignment > element
                    ['resources/alignFail1A.xml', NotImplementedError],    # Incorrect value for <Level> element: 2EDOAL expected
                    ['resources/alignFail1B.xml', RuntimeError],           # Missing <Level> element 
                    ['resources/alignFail2A.xml', RuntimeError],           # Missing <type> element 
                    ['resources/alignFail2B.xml', ValueError],             # Illegal value for <Level> element 
                    ]
            }
        )
        
        '''
        The Correspondence tests will check the edoal set of correspondences (the <Cell> elements; refer to http://alignapi.gforge.inria.fr/edoal.html), however, restricted to:
        * <Cell {rdf:about=" URI "} /> 
        *     <entity1> entity </entity1> 
        *     <entity2> entity </entity2> 
        *     <relation> STRING </relation> 
        *     <measure> STRING </measure>
        These are all required elements
        '''
        
        self.testCases['CORR'] = []
        self.testCases['CORR'].append(
            { 
            'pass': {
                'resources/alignPassSimple0.xml': {                     # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-EQ-Reln
                    'corrs': [
                        {
                            'name' : "MappingRule_0", 
                            'ent1' : {'et': ParseAlignment.EDOAL['CLASS'], 'eir' : "{http://tutorial.topbraid.com/ontoA#}unEquivanox"},
                            'ent2' : {'et': ParseAlignment.EDOAL['CLASS'], 'eir' : "{http://tutorial.topbraid.com/ontoB#}OneEq"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        },{
                            'name' : "MappingRule_1", 
                            'ent1' : {'et': ParseAlignment.EDOAL['PROP'], 'eir' : "{http://tutorial.topbraid.com/ontoA#}unEquivanox"},
                            'ent2' : {'et': ParseAlignment.EDOAL['PROP'], 'eir' : "{http://tutorial.topbraid.com/ontoB#}OneEq"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                         },{
                            'name' : "MappingRule_2", 
                            'ent1' : {'et': ParseAlignment.EDOAL['RELN'], 'eir' : "{http://tutorial.topbraid.com/ontoA#}unEquivanox"},
                            'ent2' : {'et': ParseAlignment.EDOAL['RELN'], 'eir' : "{http://tutorial.topbraid.com/ontoB#}OneEq"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        },{
                            'name' : "MappingRule_3", 
                            'ent1' : {'et': ParseAlignment.EDOAL['INST'], 'eir' : "{http://tutorial.topbraid.com/ontoA#}unEquivanox"},
                            'ent2' : {'et': ParseAlignment.EDOAL['INST'], 'eir' : "{http://tutorial.topbraid.com/ontoB#}OneEq"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }
                    ]
                },
                'resources/wine_align.xml': {                           # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-LT-Reln,
                    'corrs': [
                        {
                            'name' : "MappingRule_0", 
                            'ent1' : {'et': ParseAlignment.EDOAL['CLASS'], 'eir' : "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"},
                            'ent2' : {'et': ParseAlignment.EDOAL['CLASS'], 'eir' : "{http://ontology.deri.org/vin#}Millesime"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        },{
                            'name' : "MappingRule_1", 
                            'ent1' : {'et': ParseAlignment.EDOAL['PROP'], 'eir' : "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"},
                            'ent2' : {'et': ParseAlignment.EDOAL['PROP'], 'eir' : "{http://ontology.deri.org/vin#}Millesime"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        },{
                            'name' : "MappingRule_2", 
                            'ent1' : {'et': ParseAlignment.EDOAL['RELN'], 'eir' : "{http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#}VintageYear"},
                            'ent2' : {'et': ParseAlignment.EDOAL['RELN'], 'eir' : "{http://ontology.deri.org/vin#}Millesime"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }
                    ]
                }
            },
            'fail': { #TODO: zet geen testdata in de edoal data, maar maak aparte 'fail'labels: 'AssertionErrors'
                    'resources/alignFail3A.xml': {
                        "MissingMap": RuntimeError},           # Missing <map><Cell>...</Cell></map> element 
                    'resources/alignFail3B.xml': {
                        "MissingCell": RuntimeError},           # Missing <Cell> element 
                    'resources/alignFail3C.xml': {
                        "MappingRule_0": AssertionError, # Empty <Cell> element
                        "MappingRule_1": AssertionError, # Missing <entity1> element
                        "MappingRule_11": AssertionError,# Multiple <entity1> element 
                        "MappingRule_2": AssertionError, # Missing <entity2> element
                        "MappingRule_21": AssertionError,# Multiple <entity2> element 
                        "MappingRule_3": RuntimeError,   # Missing <relation> element 
                        "MappingRule_31": RuntimeError,  # Multiple <relation> element 
                        "MappingRule_32": RuntimeError,  # Illegal <relation> element 
                        "MappingRule_4": RuntimeError,   # Missing <measure> element 
                        "MappingRule_41": RuntimeError,  # Multiple <measure> element
                        "MappingRule_42": RuntimeError,  # Missing About attribute in <measure> element 
                        "MappingRule_5": AssertionError, # Missing About attribute in empty EDOAL element 
                        "MappingRule_6": AssertionError, # Empty <entity> element 
                        "MappingRule_7": AssertionError, # Unknown entity element in entity 
                        "MappingRule_8": AssertionError  # Unknown cell element in entity 
                    }
                }
            }
        )
        
        '''
        A Value expression is a rather central element in the EDAOL alginment. Therefore we designed a separate test for it.
        BNF definition is (refer to http://alignapi.gforge.inria.fr/edoal.html):
        <value> value </value>
        value ::= <Literal {edoal:type=" URI "} edoal:string=" STRING " />
                | instexpr 
                | attrexpr 
                | <Apply edoal:operator=" URI "> <arguments rdf:parseType="Collection">value*</arguments> </Apply> 
                | <Aggregate edoal:operator=" URI "> <arguments rdf:parseType="Collection">value*</arguments> </Aggregate>
        
        instexpr ::= <Instance rdf:about=" URI "/>
        attexpr ::= propexpr | relexpr
        '''
        self.testCases['VALUE'] = []
        self.testCases['VALUE'].append(
            {
            'pass': {
                # The LiteralPass1 tests are all <Literal>'s, but not all possible literal values/xsd:valuetype's have been specified and hence, tested
                'resources/valueLiteralPass1.xml': {
                    'valuePass1A': {
                        'valueType': 'edoal:Literal',
                        'value': 'appelepap',
                        'type': 'xsd:string'
                        },
                    'valuePass1B': {
                        'valueType': 'edoal:Literal',
                        'value': '123',
                        'type': 'xsd:integer'
                        },
                    'valuePass1C': {
                        'valueType': 'edoal:Literal',
                        'value': '1.23',
                        'type': 'xsd:float'
                        }
                    },
                'resources/valueInstancePass1.xml': {
                    'valuePass1A': {
                        'valueType': 'edoal:Instance',
                        'value': 'tno:appelepap'
                        }
                    }
                },
            'fail': {
                # The LiteralFail1 tests are all <Literal>'s, but not all possible literal values/xsd:valuetype's tested
                'resources/valueLiteralFail1.xml': { 
                    'Fail1': AssertionError,        # Empty <entity> element
                    'Fail2': AssertionError,        # Missing edoal:string attribute in <edoal:Literal\>
                    'Fail3': AssertionError         # <edoal:Literal> not an empty element
                    },
                'resources/valueInstanceFail1.xml': { 
                    'Fail1': AssertionError,        # Empty <entity> element
                    'Fail2': AssertionError,        # Missing rdf:about attribute in <edoal:Instance\>
                    'Fail3': AssertionError,        # Empty rdf:about attribute in element
                    'Fail4': AssertionError,        # Incorrect attribute in element
                    'Fail5': AssertionError         # Not an empty element
                    }
                }
            } 
        )


    def tearDown(self):
        pass


    def testParseEdoalAdmin(self):
        info = True
        debug = 3
        rule = 'ADMIN'
        if info or debug >= 1:
            print()
            print('=-'*7)
            print('EDOAL parser tests, {} part'.format(rule))
            print('=-'*7)
        for t in self.testCases[rule]:
            if info:
                print('\ntesting', rule, 'with', len(t['pass']), 'pass case(s) and', len(t['fail']), 'fail case(s)')
            if debug >= 3:
                print('> pass cases:', t['pass'])
                print('> fail cases:', t['fail'])
                print()

            # PASS: Execute the test for each defined correspondence file that is expected to pass
            for p, crit in t['pass'].items():
                # Read and parse XML Alignment file 
                if debug >= 1:
                    print('testing pass case:', p)
                    if debug >= 3:
                        for k,v in crit.items():
                            print('\t{}: {}'.format(k, v))
                pa = ParseAlignment(p)
                # Validate the Administration part, i.e., the first elements in the Alignment.
                assert pa.getAbout() == crit['about'], 'ParseAlignment attribute "{}" conflicts with expected value {}'.format(pa.about, crit['about'])
                assert pa.getCreator() == crit['admin'][1],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(pa.getCreator(), crit['admin'][1])
                assert pa.getDate() == crit['admin'][2],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(pa.getDate(), crit['admin'][2])
                assert pa.getMethod() == crit['admin'][3],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(pa.getMethod(), crit['admin'][3])
                assert pa.getPurpose() == crit['admin'][4],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(pa.getPurpose(), crit['admin'][4])
                assert pa.getLevel() == crit['admin'][5],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(pa.getLevel(), crit['admin'][5])
                assert pa.getType() == crit['admin'][6],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(pa.getType(), crit['admin'][6])
                # Validate the ontology references that are mentioned in the Alignment
                onto = pa.getSrcOnto()
                assert onto.name == crit['ontoS'][0],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.name, crit['ontoS'][0])
                assert onto.location == crit['ontoS'][1],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.location, crit['ontoS'][1])
                assert onto.formalism_uri == crit['ontoS'][2],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_uri, crit['ontoS'][2])
                assert onto.formalism_name == crit['ontoS'][3],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_name, crit['ontoS'][3])
                onto = pa.getTgtOnto()
                assert onto.name == crit['ontoT'][0],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.name, crit['ontoT'][0])
                assert onto.location == crit['ontoT'][1],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.location, crit['ontoT'][1])
                assert onto.formalism_uri == crit['ontoT'][2],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_uri, crit['ontoT'][2])
                assert onto.formalism_name == crit['ontoT'][3],'ParseAlignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_name, crit['ontoT'][3])
                  
            # FAIL: Execute the test for each correspondence that is expected to fail on this query
            f = []                        
            for f in t['fail']:
                # Read and parse XML Alignment file 
                if info or debug >= 1:
                    print('testing fail case:', f)
                # TestNSManager that an incorrect EDOAL Alignment raises the correct exceptions
                try:
                    # For every fail case, one of the below calls will result in an error
                    pa = ParseAlignment(f[0])
                    _ = pa.getAbout()
                    _ = pa.getCreator()
                    _ = pa.getDate()
                    _ = pa.getMethod()
                    _ = pa.getPurpose()
                    _ = pa.getLevel()
                    _ = pa.getType()
                    _ = pa.getSrcOnto()
                    _ = pa.getTgtOnto()
                    raise TestException('TestNSManager {} should have raised exception {}'.format(f[0], f[1]))
                except Exception as e: assert type(e) == f[1], 'TestNSManager {} should have raised exception {}; got {}'.format(f[0], f[1], type(e))
            if info:
                print('='*20)

    def testParseEdoalCorrespondence(self):
        info = True
        debug = 3
        rule = 'CORR'
        if info or debug >= 1:
            print()
            print('=-'*7)
            print('EDOAL parser tests, {} part'.format(rule))
            print('=-'*7)
        for t in self.testCases[rule]:
            if info:
                print('\ntesting', rule, 'with', len(t['pass']), 'pass case(s) and', len(t['fail']), 'fail case(s)')
            if debug >= 3:
                print('> pass cases:', t['pass'])
                print('> fail cases:', t['fail'])
                print()

            # PASS: Execute the test for each defined correspondence file that is expected to pass
            for p, crit in t['pass'].items():
                # Read and parse XML Alignment file 
                if debug >= 1:
                    print('testing pass case:', p)

                pa = ParseAlignment(p)
                
                # Get each correspondence cell 
                cell_elements = pa._align.findall(pa.nsMgr.asClarks('align:map') + '/' + pa.nsMgr.asClarks('align:Cell'))
                assert len(cell_elements) > 0, "Pass tests need to have at least one <align:map> element"
                
                # Iterate over all <Cell>...</Cell> parts
                for cell in cell_elements:
                    # Determine whether the CELL element is a pass or fail cell, based on its name
                    name = cell.get(pa.nsMgr.CLARKS_LABELS['RDFABOUT'])
                    for c in crit['corrs']:
                        if name == c['name']:
                            if debug >= 3: print('\t testing {} ..'.format(name), end="")
                            # Since this cell is part of a pass test, continue test
                            corr = pa.getCorrespondence(cell)
                            assert corr.getName() == c['name']
                            ent = corr.getEE1()
                            assert str(ent.getEntityIriRef()) == c['ent1']['eir'], "Expected <{}>, got <{}>".format(c['ent1']['eir'],ent.getEntityIriRef())
                            assert ent.getEntityType() == c['ent1']['et'], "Expected <{}>, <got> {}".format(c['ent1']['et'],ent.getEntityType())
                            if debug >= 3: print(". done")
                            break
                    if corr.getName() != c['name']:
                        #TODO: TestNSManager completeness - maak teller ipv afhankelijk te zijn van about name
                        raise TestException("Incomplete test setup, or invalid parsing: Testcase for {} expected but not found".format(corr.getName()))

            # FAIL: Execute the test for each correspondence that is expected to fail on this query
            f = []
            for f in t['fail']:
                if info or debug >= 1:
                    print('testing fail case:', f)     
                
                pa = ParseAlignment(f)
                mappings = t['fail'][f]
                assert pa != None and pa != [], "The fail tests, too, require an Edoal alignment. None found in testcase {}".format(f)
                # Get each correspondence cell 
                map_elements = []
                map_elements = pa._align.findall(pa.nsMgr.asClarks('align:map'))
                if map_elements == []:
                    # Found absent <map> element, which should raise an exception
                    try:
                        if debug >= 3: print("\ttesting {} ..".format('MissingMap'), end="")
                        _ = pa.getCorrespondences()
                        raise TestException('Testcase {}: test {} should have raised exception {}'.format(f,'MissingMap', mappings['MissingMap']))
                    except Exception as e: 
                        assert type(e) == mappings['MissingMap'], 'TestNSManager should have raised exception {}; got {}'.format(mappings['MissingMap'], type(e))
                        if debug >= 3: print(". done")
                else:
                    for map_element in map_elements:
                        cell_elements = map_element.findall(pa.nsMgr.asClarks('align:Cell'))
                        if cell_elements == []:
                            if debug >= 3: print("\ttesting {} ..".format('MissingCell'), end="")
                            # Found empty <map> element, which should raise an exception
                            try:
                                _ = pa.getCorrespondences()
                                raise TestException('Testcase {}: test {} should have raised exception {}'.format(f,'MissingCell', mappings['MissingCell']))
                            except Exception as e: 
                                assert type(e) == mappings['MissingCell'], 'TestNSManager should have raised exception {}; got {}'.format(mappings['MissingCell'], type(e))
                                if debug >= 3: print(". done")
                        else:
                            # iterate over all <Cell> elements (only 1?) and validate the failure of each cell
                            for cell in cell_elements:
                                name = cell.get(NSManager.CLARKS_LABELS['RDFABOUT'])
                                assert isinstance(name,str) and name!='', "An edoal {} element requires an {} attribute. None found in this cell in {}".format(cell.tag, pa.nsMrg.CLARKS_LABELS['RDFABOUT'],f)
                                if debug >= 3: print("\ttesting {} ..".format(name), end="")
                                try:
                                    corr = pa.getCorrespondence(cell)
                                    raise TestException('Testcase {}: test {} should have raised exception {}'.format(f,name, mappings[name]))
                                except Exception as e: 
                                    assert type(e) == mappings[name], 'TestNSManager {} should have raised exception {}; got {}'.format(name, mappings[name], type(e))
                                    if debug >= 3: print(". done")
                        
    def testParseEdoalValue(self):
        from utilities.namespaces import NSManager
        ns = {'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              'xsd': "http://www.w3.org/2001/XMLSchema#",
              'align':"http://knowledgeweb.semanticweb.org/heterogeneity/alignment#",
              'edoal':'http://ns.inria.org/edoal/1.0/#',
              't'   : 'http://ns.tno.nl/mediator/test#'
              }
        nsMgr = NSManager(ns, "http://ns.tno.nl/mediator/test#")
        
        info = True
        debug = 3
        rule = 'VALUE'
        if info or debug >= 1:
            print()
            print('=-'*7)
            print('EDOAL parser tests, {} part'.format(rule))
            print('=-'*7)
        for t in self.testCases[rule]:
            if info:
                print('\ntesting', rule, 'with', len(t['pass']), 'pass case(s) and', len(t['fail']), 'fail case(s)')
            if debug >= 3:
                print('> pass cases:', t['pass'])
                print('> fail cases:', t['fail'])
                print()

            testCriteria = []
            
            # PASS: Execute the test for each defined correspondence file that is expected to pass
            for testCase, testCriteria in t['pass'].items():
                if debug >= 1:
                    print('PASS case {} has specified {} tests'.format(testCase,len(testCriteria)))
                # Do the test
                with open(testCase, 'r') as f:
                    test_tree = etree.parse(f)
                root = test_tree.getroot()
                tests = root.findall('t:test', ns)
                if len(testCriteria) != len(tests): raise TestException('TestNSManager setup specifies {} tests, but {} tests found in test data ({})'.format(len(testCriteria), len(tests), testCase))
                if debug >=3: print('Found {} tests in test data'.format(len(tests)))
                for test in tests:
                    tname = test.get(NSManager.CLARKS_LABELS['RDFABOUT'])
                    # Check the test data
                    if tname == None or tname == '': raise TestException('Testcase {}: Use of {} attribute in <test> element required to discern the various testCriteria'.format(testCase, NSManager.nsmap['RDFABOUT']))
                    edoal_entity = test.find('edoal:entity1', ns)
                    if edoal_entity == None: raise TestException('Testcase {}: TestNSManager ({}) is required to contain an <entity1> element'.format(testCase, tname))
                    if debug >=3: print('Testing test: {} ..'.format(tname), end="")
                    edoalValue = ParseAlignment.Value(el=edoal_entity, nsMgr=nsMgr)
                    if edoalValue == None: raise TestException('Testcase {}: TestNSManager ({}) is required to contain a <value> element'.format(testCase, tname))
                    # Check the value type that is under test, perform the test and verify the outcome is as expected
                    if testCriteria[tname]['valueType'] == 'edoal:Literal':
                        assert (testCriteria[tname]['value'], testCriteria[tname]['type']) == edoalValue.getLiteral(), \
                            'Testcase {}, tests {}: expected {} but found {}'.format(testCase, tname, (testCriteria[tname]['value'], testCriteria[tname]['type']), edoalValue.getLiteral())
                    elif testCriteria[tname]['valueType'] == 'edoal:Instance':
                        assert testCriteria[tname]['value'] == edoalValue.getIndividual(),'Testcase {}, tests {}: expected {} but found {}'.format(testCase, tname, testCriteria[tname]['value'], edoalValue.getIndividual())
                    else: raise TestException('No test code implemented for value type {}, please specify and add test code'.format(testCriteria[tname]['valueType']))
                    if debug >=3: print('. done')

            # FAIL: Execute the testCriteria, which are expected to fail
            for testCase, testCriteria in t['fail'].items():
                if debug >= 1:
                    print('\nFAIL case {} has specified {} tests'.format(testCase,len(testCriteria)))

                # Get the filename; each file is a testcase
                with open(testCase, 'r') as f:
                    test_tree = etree.parse(f)
                # Parse the xml-data that represent the test data
                root = test_tree.getroot()
                tests = root.findall('t:test', ns)
                if len(testCriteria) != len(tests): raise TestException('TestNSManager setup specifies {} tests, but {} tests found in test data ({})'.format(len(testCriteria), len(tests), testCase))
                if debug >=3: print('Found {} tests in test data'.format(len(tests)))
                # Illegal use of the Alignment element
                for test in tests:
                    tname = test.get(NSManager.CLARKS_LABELS['RDFABOUT'])
                    # Check the test data
                    if tname == None or tname == '': raise TestException('Testcase {}: Use of {} attribute in <test> element required to discern the various testCriteria'.format(testCase, NSManager.nsmap['RDFABOUT']))
                    edoal_entity=test.find('edoal:entity1', ns)
                    if edoal_entity==None: raise TestException('Testcase {}: TestNSManager ({}) is required to contain an <entity1> element'.format(testCase, tname))
                    # Perform the test, check for the occurrence of an exception and verify that the fault condition raises the correct exception
                    try:
                        if debug >=3: print('testing {} ...'.format(tname), end="")
                        _ = ParseAlignment.Value(el=edoal_entity, nsMgr=nsMgr)
                        # This should be dead code, because an exception should have been raised
                        raise TestException('Testcase {}: TestNSManager {} failed, expected exception ({}) did not occur!'.format(testCase, tname, testCriteria[tname]))
                    except Exception as e: assert type(e) == testCriteria[tname], 'Testcase {}: TestNSManager {} expected {}, got {}'.format(testCase, tname, testCriteria[tname], type(e))
                    if debug >=3: print('. done')

    def _parseOperationTest(self):
        pass
       # _parseOperation(self, operation_el=None)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testParseEdoalAdmin']
    unittest.main()