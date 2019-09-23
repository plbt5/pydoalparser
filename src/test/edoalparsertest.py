'''
Created on 21 apr. 2016

@author: brandtp
'''
import unittest
import warnings

from edoalparser.EDOALparser import Alignment
from edoalparser.parserTools import EClass
from test.mytestexceptions import TestException
from utilities.namespaces import NSManager
import xml.etree.ElementTree as etree


class TestEDOALParser(unittest.TestCase):

    def setUp(self):
#         from mediator.EDOALparser import Alignment
        ns = {'rdf'  : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              'xsd'  : "http://www.w3.org/2001/XMLSchema#",
              'align':"http://knowledgeweb.semanticweb.org/heterogeneity/alignment#",
              'dc'   : 'http://purl.org/dc/elements/1.1/',
              'edoal':'http://ns.inria.org/edoal/1.0/#',
              'alext': 'http://exmo.inrialpes.fr/align/ext/1.0/',
              'medtfn': 'http://ts.tno.nl/mediator/1.0/transformations#',
              't'    : 'http://ts.tno.nl/mediator/test#'
              }
        self.nsMgr = NSManager(ns, "http://knowledgeweb.semanticweb.org/heterogeneity/alignment#")
        print(str(self.nsMgr))
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
            'pass': {'resources/alignPassSimple0.xml':  # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-EQ-Reln
                      {'about': 'http://ds.tno.nl/ontoA-ontoB/CPR-EQ-CPR',
                       'admin': ['yes', 'PaulBrandt', '2015/08/25', 'manual', 'TEST DATA (simple alignments)', '2EDOAL', '?*'],
                       'ontoS': ["<http://tutorial.topbraid.com/ontoA#>", None, "<http://www.w3.org/2002/07/owl#>", "OWL1.0"],
                       'ontoT': ["<http://tutorial.topbraid.com/ontoB#>", "resources/nl/test1/ontoB.xml", "<http://www.w3.org/2002/07/owl#>", "OWL1.0"]
                       },
                     'resources/wine_align.xml':  # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-LT-Reln,
                      {'about': 'http://oms.omwg.org/wine-vin/',  #   & one SmplSrcCls-EQ-CmplxTgtCls, one CmpxlSrcCls-LT-CmplxTgtCls
                       'admin': ['yes', 'http://www.scharffe.fr/foaf.rdf', '2006/06/07', 'manual', 'TESTcase: hugely adapted from original wine-vin example', '2EDOAL', '**'],
                       'ontoS': ["<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#>", None, "<http://www.w3.org/TR/owl-guide/>", "owl"],
                       'ontoT': ["<http://ontology.deri.org/vin#>", "http://www.scharffe.fr/ontologies/OntologieDuVin.wsml", "<http://www.wsmo.org/wsml/wsml-syntax/wsml-dl>", "wsml"]
                    }
                },
            'fail': 
                [
                    ['resources/alignFail0A.xml', RuntimeError],  # Missing <Alignment> element
                    ['resources/alignFail0B.xml', ValueError],  # Missing 'alignET:about="somename"' in <Alignment > element
                    ['resources/alignFail1A.xml', NotImplementedError],  # Incorrect value for <Level> element: 2EDOAL expected
                    ['resources/alignFail1B.xml', RuntimeError],  # Missing <Level> element 
                    ['resources/alignFail2A.xml', RuntimeError],  # Missing <type> element 
                    ['resources/alignFail2B.xml', ValueError],  # Illegal value for <Level> element 
                    ['', AssertionError],  # Missing file name 
                    ['resources/missingAlignFile.xml', AssertionError],  # Illegal file name 
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
                'resources/alignPassSimple0.xml': {  # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-EQ-Reln
                    'corrs': [
                        {
                            'name' : "MappingRule_0",
                            'ent1' : {'et': Alignment.EDOAL['CLASS'], 'eir' : "<http://tutorial.topbraid.com/ontoA#unEquivanox>"},
                            'ent2' : {'et': Alignment.EDOAL['CLASS'], 'eir' : "<http://tutorial.topbraid.com/ontoB#OneEq>"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }, {
                            'name' : "MappingRule_1",
                            'ent1' : {'et': Alignment.EDOAL['PROP'], 'eir' : "<http://tutorial.topbraid.com/ontoA#unEquivanox>"},
                            'ent2' : {'et': Alignment.EDOAL['PROP'], 'eir' : "<http://tutorial.topbraid.com/ontoB#OneEq>"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                         }, {
                            'name' : "MappingRule_2",
                            'ent1' : {'et': Alignment.EDOAL['RELN'], 'eir' : "<http://tutorial.topbraid.com/ontoA#unEquivanox>"},
                            'ent2' : {'et': Alignment.EDOAL['RELN'], 'eir' : "<http://tutorial.topbraid.com/ontoB#OneEq>"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }, {
                            'name' : "MappingRule_3",
                            'ent1' : {'et': Alignment.EDOAL['INST'], 'eir' : "<http://tutorial.topbraid.com/ontoA#unEquivanox>"},
                            'ent2' : {'et': Alignment.EDOAL['INST'], 'eir' : "<http://tutorial.topbraid.com/ontoB#OneEq>"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }
                    ]
                },
                'resources/wine_align.xml': {  # Simple Class-EQ-Class, Prop-EQ-Prop, Reln-LT-Reln,
                    'corrs': [
                        {
                            'name' : "MappingRule_0",
                            'ent1' : {'et': Alignment.EDOAL['CLASS'], 'eir' : "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"},
                            'ent2' : {'et': Alignment.EDOAL['CLASS'], 'eir' : "<http://ontology.deri.org/vin#Millesime>"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }, {
                            'name' : "MappingRule_1",
                            'ent1' : {'et': Alignment.EDOAL['PROP'], 'eir' : "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"},
                            'ent2' : {'et': Alignment.EDOAL['PROP'], 'eir' : "<http://ontology.deri.org/vin#Millesime>"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }, {
                            'name' : "MappingRule_2",
                            'ent1' : {'et': Alignment.EDOAL['RELN'], 'eir' : "<http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear>"},
                            'ent2' : {'et': Alignment.EDOAL['RELN'], 'eir' : "<http://ontology.deri.org/vin#Millesime>"},
                            'msre' : 1.0,
                            'reln' : 'EQ'
                        }
                    ]
                }
            },
            'fail': {  # TODO: zet geen testdata in de edoal data, maar maak aparte 'fail'labels: 'AssertionErrors'
                    'resources/alignFail3A.xml': {
                        "MissingMap": RuntimeError},  # Missing <map><Cell>...</Cell></map> element 
                    'resources/alignFail3B.xml': {
                        "MissingCell": RuntimeError},  # Missing <Cell> element 
                    'resources/alignFail3C.xml': {
                        "MappingRule_0": AssertionError,  # Empty <Cell> element
                        "MappingRule_1": AssertionError,  # Missing <entity1> element
                        "MappingRule_11": AssertionError,  # Multiple <entity1> element 
                        "MappingRule_12": AssertionError,  # Non-empty simple <class> element 
                        "MappingRule_13": AssertionError,  # Non-empty simple <property> element 
                        "MappingRule_14": AssertionError,  # Non-empty simple <relation> element 
                        "MappingRule_15": AssertionError,  # Non-empty simple <class> element 
                        "MappingRule_16": AssertionError,  # Non-empty simple <property> element
                        "MappingRule_17": AssertionError,  # Non-empty simple <relation> element
                        "MappingRule_2": AssertionError,  # Missing <entity2> element
                        "MappingRule_21": AssertionError,  # Multiple <entity2> element 
                        "MappingRule_3": RuntimeError,  # Missing <relation> element 
                        "MappingRule_31": RuntimeError,  # Multiple <relation> element 
                        "MappingRule_32": RuntimeError,  # Illegal <relation> element 
                        "MappingRule_4": RuntimeError,  # Missing <measure> element 
                        "MappingRule_41": RuntimeError,  # Multiple <measure> element
                        "MappingRule_42": RuntimeError,  # Missing About attribute in <measure> element 
                        "MappingRule_5": AssertionError,  # Missing About attribute in empty EDOAL element 
                        "MappingRule_6": AssertionError,  # Empty <entity> element 
                        "MappingRule_7": AssertionError,  # Unknown entity element in entity 
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
                'resources/valueSimplePass1.xml': {
                    'valueLiteralePass1A': {
                        'valueType': 'edoal:Literal',
                        'value': 'appelepap',
                        'type': '<http://www.w3.org/2001/XMLSchema#string>'
                        },
                    'valueLiteralePass1B': {
                        'valueType': 'edoal:Literal',
                        'value': '123',
                        'type': '<http://www.w3.org/2001/XMLSchema#integer>'
                        },
                    'valueLiteralePass1C': {
                        'valueType': 'edoal:Literal',
                        'value': '1.23',
                        'type': '<http://www.w3.org/2001/XMLSchema#float>'
                        },
                    'valueInstancePass1': {
                        'valueType': 'edoal:Instance',
                        'value': '<http://ts.tno.nl/mediator/1.0/appelepap>'
                        },
                    'valuePropertyPass1A': {
                        'valueType': 'edoal:Property',
                        'value': '<http://ts.tno.nl/mediator/1.0/appelepap>',
                        'lang': None
                        },
                    'valuePropertyPass1B': {
                        'valueType': 'edoal:Property',
                        'value': '<http://ts.tno.nl/mediator/1.0/appelepap>',
                        'lang': 'NL'
                        },
                    'valueRelationPass1': {
                        'valueType': 'edoal:Relation',
                        'value': '<http://ts.tno.nl/mediator/1.0/appelepap>'
                        }
                    },
                'resources/valueSimplePass2.xml': {
                    'valueLiteralePass2A': {
                        'valueType': 'edoal:Apply',
                        'value': 'transformations.unitconversion/CtoF',
                        'type': '<http://ns.inria.org/edoal/1.0/#apply>'
                        },
                    'valueLiteralePass2B': {
                        'valueType': 'edoal:Apply',
                        'value': 'transformations.unitconversion/TempConvertor',
                        'type': '<http://ns.inria.org/edoal/1.0/#apply>'
                        }
                    },
                'resources/valuePathPass1.xml': {
                    'valuePathPass1A': {
                        'valueType': 'edoal:compose',
                        'value': ['<http://ts.tno.nl/mediator/1.0/example#hasProperty> ({http://ns.inria.org/edoal/1.0/#}property)'],
                        'type': Alignment.EDOAL['PROP']
                        },
                    'valuePathPass1B': {
                        'valueType': 'edoal:compose',
                        'value': ['<http://ts.tno.nl/mediator/1.0/example#hasRelation> ({http://ns.inria.org/edoal/1.0/#}relation)', '<http://ts.tno.nl/mediator/1.0/example#hasProperty> ({http://ns.inria.org/edoal/1.0/#}property)'],
                        'type': Alignment.EDOAL['PROP']
                        },
                    'valuePathPass1C': {
                        'valueType': 'edoal:compose',
                        'value': ['<http://ts.tno.nl/mediator/1.0/example#hasRelation> ({http://ns.inria.org/edoal/1.0/#}relation)'],
                        'type': Alignment.EDOAL['RELN']
                        },
                    'valuePathPass1D': {
                        'valueType': 'edoal:compose',
                        'value': [],
                        'type': Alignment.EDOAL['PROP']
                        },
                    'valuePathPass1E': {
                        'valueType': 'edoal:compose',
                        'value': [],
                        'type': Alignment.EDOAL['RELN']
                        },
                    'valuePathPass1F': {
                        'valueType': 'edoal:compose',
                        'value': ['<http://ts.tno.nl/mediator/1.0/example#hasRelation1> ({http://ns.inria.org/edoal/1.0/#}relation)', '<http://ts.tno.nl/mediator/1.0/example#hasRelation2> ({http://ns.inria.org/edoal/1.0/#}relation)', '<http://ts.tno.nl/mediator/1.0/example#hasProperty> ({http://ns.inria.org/edoal/1.0/#}property)'],
                        'type': Alignment.EDOAL['PROP']
                        }
                    }
                },
            'fail': {
                # The LiteralFail1 tests are all <Literal>'s, but not all possible literal values/xsd:valuetype's tested
                'resources/valueSimpleFail1.xml': { 
                    'FailEmpty1'   : AssertionError,  # Empty <entity> element
                    'FailLiteral1' : AssertionError,  # Missing edoal:string attribute in <edoal:Literal\>
                    'FailLiteral2' : AssertionError,  # Literal is always a single, empty element with its value in the attributes 
                    'FailInstance1': AssertionError,  # Missing rdf:about attribute in <edoal:Instance\>
                    'FailInstance2': AssertionError,  # Empty rdf:about attribute in element
                    'FailInstance3': AssertionError,  # Incorrect attribute in element
                    'FailInstance4': AssertionError,  # Not an empty element
                    'FailProperty1': AssertionError,  # Empty about attribute, empty Lang attribute
                    'FailProperty2': AssertionError,  # Missing about attribute, empty Lang attribute
                    'FailProperty3': AssertionError,  # Empty about attribute, missing Lang attribute 
                    'FailProperty4': AssertionError,  # Missing about attribute, missing Lang attribute
                    'FailProperty5': AssertionError,  # Empty about attribute, valid Lang attribute
                    'FailProperty6': AssertionError,  # Missing about attribute, valid Lang attribute
                    'FailRelation1': AssertionError,  # Empty about attribute
                    'FailRelation2': AssertionError,  # Missing about attribute 
                    'FailRelation3': AssertionError  # Valid attribute, invalid element (element is not empty) 
                    },
                'resources/valuePathFail1.xml': { 
                    'FailPathOfNonAttrExpr1'  : AssertionError,  # Instance path is illegal
                    'FailPathOfNonAttrExpr2'  : AssertionError,  # Literal path is illegal
                    'FailPathOfNonAttrExpr3'  : AssertionError,  # Class path is illegal 
                    'FailPathWithNonAttrExpr1': AssertionError,  # Property Path containing Instance is illegal
                    'FailPathWithNonAttrExpr2': AssertionError,  # Relation Path containing Literal is illegal
                    'FailPathWithNonAttrExpr3': AssertionError,  # Relation Path containing Class is illegal
                    'FailComplexPathNotImpl'  : NotImplementedError  # Correct path, but too complex to be implemented yet
                    }
                }
            } 
        )

    def tearDown(self):
        pass

    def testParseEdoalAdmin(self):
#         from mediator.EDOALparser import Alignment
        info = True
        debug = 3
        rule = 'ADMIN'
        if info or debug >= 1:
            print()
            print('=-' * 7)
            print('EDOAL parser tests, {} part'.format(rule))
            print('=-' * 7)
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
                        for k, v in crit.items():
                            print('\t{}: {}'.format(k, v))
                pa = Alignment(fn=p, nsMgr=self.nsMgr)
                # Validate the Administration part, i.e., the first elements in the Alignment.
                assert pa.getAbout() == crit['about'], 'Alignment attribute "{}" conflicts with expected value {}'.format(pa.about, crit['about'])
                assert pa.getCreator() == crit['admin'][1], 'Alignment attribute "{}" conflicts with expected value {}'.format(pa.getCreator(), crit['admin'][1])
                assert pa.getDate() == crit['admin'][2], 'Alignment attribute "{}" conflicts with expected value {}'.format(pa.getDate(), crit['admin'][2])
                assert pa.getMethod() == crit['admin'][3], 'Alignment attribute "{}" conflicts with expected value {}'.format(pa.getMethod(), crit['admin'][3])
                assert pa.getPurpose() == crit['admin'][4], 'Alignment attribute "{}" conflicts with expected value {}'.format(pa.getPurpose(), crit['admin'][4])
                assert pa.getLevel() == crit['admin'][5], 'Alignment attribute "{}" conflicts with expected value {}'.format(pa.getLevel(), crit['admin'][5])
                assert pa.getType() == crit['admin'][6], 'Alignment attribute "{}" conflicts with expected value {}'.format(pa.getType(), crit['admin'][6])
                # Validate the ontology references that are mentioned in the Alignment
                onto = pa.getSrcOnto()
                assert onto.name == crit['ontoS'][0], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.name, crit['ontoS'][0])
                assert onto.location == crit['ontoS'][1], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.location, crit['ontoS'][1])
                assert onto.formalism_uri == crit['ontoS'][2], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_uri, crit['ontoS'][2])
                assert onto.formalism_name == crit['ontoS'][3], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_name, crit['ontoS'][3])
                onto = pa.getTgtOnto()
                assert onto.name == crit['ontoT'][0], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.name, crit['ontoT'][0])
                assert onto.location == crit['ontoT'][1], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.location, crit['ontoT'][1])
                assert onto.formalism_uri == crit['ontoT'][2], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_uri, crit['ontoT'][2])
                assert onto.formalism_name == crit['ontoT'][3], 'Alignment attribute "{}" conflicts with expected value {}'.format(onto.formalism_name, crit['ontoT'][3])
                  
            # FAIL: Execute the test for each correspondence that is expected to fail on this query
            f = []                        
            for f in t['fail']:
                # Read and parse XML Alignment file 
                if info or debug >= 1:
                    print('testing fail case:', f)
                # Test that an incorrect EDOAL Alignment raises the correct exceptions
                try:
                    # For every fail case, one of the below calls will result in an error
                    pa = Alignment(f[0], nsMgr=self.nsMgr)
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
            # Test the need for a proper nsMgr
            properfile = list(t['pass'].keys())[0]
            with self.assertRaises(AssertionError):
                _ = Alignment(properfile, nsMgr=None)
            # Test adding the same alignment twice    
            pa = Alignment(properfile, nsMgr=self.nsMgr)
            with self.assertRaises(AssertionError):
                pa._addAlignment(fn=properfile, nsMgr=self.nsMgr)
            if info:
                print('=' * 20)

    def testParseEdoalCorrespondence(self):
#         from mediator.EDOALparser import Alignment
        info = True
        debug = 3
        rule = 'CORR'
        if info or debug >= 1:
            print()
            print('=-' * 7)
            print('EDOAL parser tests, {} part'.format(rule))
            print('=-' * 7)
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

                pa = Alignment(fn=p, nsMgr=self.nsMgr)
                
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
                            corr = pa._parseCorrespondence(cell)
                            assert corr.getName() == c['name']
                            entExpr = corr.getEE1()
                            assert entExpr.getIriRef() == c['ent1']['eir'], "Expected '{}', got '{}'".format(c['ent1']['eir'], entExpr.getIriRef())
                            assert entExpr.getType() == c['ent1']['et'], "Expected '{}', got '{}'".format(c['ent1']['et'], entExpr.getType())
                            if debug >= 3: print(". done")
                            break
                    if corr.getName() != c['name']:
                        # TODO: TestNSManager completeness - maak teller ipv afhankelijk te zijn van about name
                        raise TestException("Incomplete test setup, or invalid parsing: Testcase for {} expected but not found".format(corr.getName()))

            # FAIL: Execute the test for each correspondence that is expected to fail on this query
            f = []
            for f in t['fail']:
                if info or debug >= 1:
                    print('testing fail case:', f)     
                
                pa = Alignment(fn=f, nsMgr=self.nsMgr)
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
                        raise TestException('Testcase {}: test {} should have raised exception {}'.format(f, 'MissingMap', mappings['MissingMap']))
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
                                raise TestException('Testcase {}: test {} should have raised exception {}'.format(f, 'MissingCell', mappings['MissingCell']))
                            except Exception as e: 
                                assert type(e) == mappings['MissingCell'], 'TestNSManager should have raised exception {}; got {}'.format(mappings['MissingCell'], type(e))
                                if debug >= 3: print(". done")
                        else:
                            # iterate over all <Cell> elements and validate the failure of each cell
                            for cell in cell_elements:
                                name = cell.get(NSManager.CLARKS_LABELS['RDFABOUT'])
                                assert isinstance(name, str) and name != '', "An edoal {} element requires an {} attribute. None found in this cell in {}".format(cell.tag, pa.nsMrg.CLARKS_LABELS['RDFABOUT'], f)
                                if debug >= 3: print("\ttesting {} ..".format(name), end="")
                                try:
                                    corr = pa._parseCorrespondence(cell)
                                    raise TestException('Testcase {}: test {} should have raised exception {}'.format(f, name, mappings[name]))
                                except Exception as e: 
                                    assert type(e) == mappings[name], 'TestNSManager {} should have raised exception {}; got {}'.format(name, mappings[name], type(e))
                                    if debug >= 3: print(". done")
        
        w = 'resources/alignWarningPass1.xml'
        print('testing warning case:', w)
        pa = Alignment(fn=w, nsMgr=self.nsMgr)
        assert pa != None and pa != [], "Test failure: The test requires an Edoal alignment. None found in testcase {}".format(w)
        assert pa.getAbout() == "http://ds.tno.nl/ontoA-ontoB/DuplicateCells", "Test failure: other alignment read, got '{}'".format(pa.getAbout())
        # Get each correspondence cell 
        cell_elements = pa._align.findall(pa.nsMgr.asClarks('align:map') + '/' + pa.nsMgr.asClarks('align:Cell'))
        assert len(cell_elements) == 3, "Test failure: test needs to have 3 <align:map> elements, got {}".format(len(cell_elements))
        print('\ttesting DuplicateCells ', end="")
        # Iterate over all <Cell>...</Cell> parts
        nameMgr = []
        pa._corrs = []
        for cell in cell_elements:
            # There are three correct <Cell>'s, but the second is a duplicate. 
            # Assert that a duplicate warning is raised, and that the other two correspondences have been created.
            print('.', end="")
            name = cell.get(NSManager.CLARKS_LABELS['RDFABOUT'])
            if name in nameMgr:
                with self.assertWarns(UserWarning):
                    corr = pa._parseCorrespondence(cell)
            else:
                nameMgr.append(name)
                corr = pa._parseCorrespondence(cell)
                pa.appendCorrespondence(corr)
                assert corr.getName() == name
        assert len(pa.getCorrespondences()) == 2, "Got {}".format(len(pa.getCorrespondences()))
        print(' done')
                    
    def testParseEdoalValue(self):
#         from mediator.EDOALparser import Alignment

        info = True
        debug = 3
        rule = 'VALUE'
        if info or debug >= 1:
            print()
            print('=-' * 7)
            print('EDOAL parser tests, {} part'.format(rule))
            print('=-' * 7)
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
                    print('PASS case {} has specified {} tests'.format(testCase, len(testCriteria)))
                # Do the test
                # Create a Alignment object only to have a valid Alignment object and create a valid nsMgr;
                #    the test data is incorrect edoal, and this code below takes that into consideration
                pa = Alignment(fn=testCase, nsMgr=self.nsMgr)
                testsEl = pa._align.findall(self.nsMgr.asClarks('t:tests'))
                if testsEl == None or len(testsEl) == 0: raise TestException("No tests found, cannot perform tests")
                tests = testsEl[0].findall(self.nsMgr.asClarks('t:test'))
                if len(testCriteria) != len(tests): raise TestException('Test setup specifies {} tests, but {} tests found in test data ({})'.format(len(testCriteria), len(tests), testCase))
                if debug >= 3: print('Found {} tests in test data'.format(len(tests)))
                for test in tests:
                    tname = test.get(NSManager.CLARKS_LABELS['RDFABOUT'])
                    # Check the test data
                    if tname == None or tname == '': raise TestException('Testcase {}: Use of {} attribute in <test> element required to discern the various testCriteria'.format(testCase, NSManager.nsmap['RDFABOUT']))
                    edoal_entity = test.find(self.nsMgr.asClarks('edoal:entity1'))
                    if edoal_entity == None: raise TestException('Testcase {}: Test ({}) is required to contain an <entity1> element'.format(testCase, tname))
                    if debug >= 3: print('Testing test: {} ..'.format(tname), end="")
                    edoalValue = pa.Value(el=edoal_entity, parse_alignment=pa)
                    if edoalValue == None: raise TestException('Testcase {}: Test ({}) is required to contain a <value> element'.format(testCase, tname))
                    # Check the value type that is under test, perform the test and verify the outcome is as expected
                    if testCriteria[tname]['valueType'] == 'edoal:Literal':
                        assert (testCriteria[tname]['value'], testCriteria[tname]['type']) == edoalValue.getLiteral(), \
                            'Testcase {}, test {}: expected {} but found {}'.format(testCase, tname, (testCriteria[tname]['value'], testCriteria[tname]['type']), edoalValue.getLiteral())
                    elif testCriteria[tname]['valueType'] == 'edoal:Instance':
                        assert testCriteria[tname]['value'] == edoalValue.getIndividual(), 'Testcase {}, test {}: expected {} but found {}'.format(testCase, tname, testCriteria[tname]['value'], edoalValue.getIndividual())
                    elif testCriteria[tname]['valueType'] in ['edoal:Property', 'edoal:Relation']:
                        assert testCriteria[tname]['value'] == edoalValue.getAttrExpression(), 'Testcase {}, test {}: expected {} but found {}'.format(testCase, tname, testCriteria[tname]['value'], edoalValue.getAttrExpression())
                    elif testCriteria[tname]['valueType'] in ['edoal:Apply', 'edoal:Aggregate']:
                        assert testCriteria[tname]['value'] == edoalValue.getOperator().getName(), 'Testcase {}, test {}: expected {} but found {}'.format(testCase, tname, testCriteria[tname]['value'], edoalValue.getOperator().getName())
                    elif testCriteria[tname]['valueType'] == 'edoal:compose':
                        assert testCriteria[tname]['type'] == edoalValue.getEntityType(), 'Testcase {}, test {}: expected {} but found {}'.format(testCase, tname, testCriteria[tname]['type'], edoalValue.getEntityType())
                        if edoalValue.hasPath():
                            for criterion, attrExpr in zip(testCriteria[tname]['value'], edoalValue.getPath()):
                                assert criterion == str(attrExpr), 'Testcase {}, test {}: expected {} but found {}'.format(testCase, tname, criterion, attrExpr)
                        else: raise AssertionError('Testcase {}, test {}: missing path expression'.format(testCase, tname))
                    else: raise TestException('No test code implemented for value type {}, please specify and add test code'.format(testCriteria[tname]['valueType']))
                    if debug >= 3: print('. done')

            # FAIL: Execute the testCriteria, which are expected to fail
            for testCase, testCriteria in t['fail'].items():
                if debug >= 1:
                    print('\nFAIL case {} has specified {} tests'.format(testCase, len(testCriteria)))

                # Create a Alignment object only to have a valid Alignment object and create a valid nsMgr;
                #    the test data is incorrect edoal, and this code below takes that into consideration
                pa = Alignment(fn=testCase, nsMgr=self.nsMgr)
                testsEl = pa._align.findall(self.nsMgr.asClarks('t:tests'))
                if testsEl == None or len(testsEl) == 0: raise TestException("No tests found, cannot perform tests")
                tests = testsEl[0].findall(self.nsMgr.asClarks('t:test'))
                if len(testCriteria) != len(tests): raise TestException('TestNSManager setup specifies {} tests, but {} tests found in test data ({})'.format(len(testCriteria), len(tests), testCase))
                if debug >= 3: print('Found {} tests in test data'.format(len(tests)))
                # Illegal use of the Alignment element
                for test in tests:
                    tname = test.get(NSManager.CLARKS_LABELS['RDFABOUT'])
                    # Check the test data
                    if tname == None or tname == '': raise TestException('Testcase {}: Use of {} attribute in <test> element required to discern the various testCriteria'.format(testCase, NSManager.nsmap['RDFABOUT']))
                    edoal_entity = test.find(self.nsMgr.asClarks('edoal:entity1'))
                    if edoal_entity == None: raise TestException('Testcase {}: TestCase ({}) is required to contain an <entity1> element'.format(testCase, tname))
                    # Perform the test, check for the occurrence of an exception and verify that the fault condition raises the correct exception
                    try:
                        if debug >= 3: print('testing {} ...'.format(tname), end="")
                        _ = pa.Value(el=edoal_entity, parse_alignment=pa)
                        # This should be dead code, because an exception should have been raised
                        raise TestException('Testcase {}: Test {} failed, expected exception ({}) did not occur!'.format(testCase, tname, testCriteria[tname]))
                    except Exception as e: assert type(e) == testCriteria[tname], 'Testcase {}, test {}: expected {}, got {}'.format(testCase, tname, testCriteria[tname], type(e))
                    if debug >= 3: print('. done')

    def test_parseOperation(self):
        assert False, "Make test for method '_parseOperation()'"

    def test_parseTransform(self):
        assert False, "Make test for method '_parseTransform()'"
        
    def testAlignment(self):
        # Pass testcases
        a = Alignment(fn='resources/valueSimplePass1.xml', nsMgr=self.nsMgr)
        assert a.about == "http://ds.tno.nl/ontoA-ontoB/CPR-EQ-CPR"
        
        # Fail testcases
        with self.assertRaises(AssertionError):
            _ = Alignment(fn='', nsMgr=self.nsMgr)
        with self.assertRaises(AssertionError):
            _ = Alignment(fn='resources/valueSimplePass1.xml', nsMgr=None)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'TestNSManager.testParseEdoalAdmin']
    unittest.main()
