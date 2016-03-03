'''
Created on 26 feb. 2016

@author: brandtp
'''
import unittest
from mediator.mediator import Mediator
from sparqlparser.grammar import ParseInfo
import warnings

import xml.etree.cElementTree as etree

class Test(unittest.TestCase):

    ns = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'xmlns': 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
        'base': 'http://oms.omwg.org/wine-vin/',
        'wine': 'http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#',
        'vin': 'http://ontology.deri.org/vin#',
        'edoal': 'http://ns.inria.org/edoal/1.0/#'
    }

    @classmethod
    def makeTestFunc(self, rule, testCases, *, info=False, debug=0):
        def testFuncC():
            '''
                Execute all Correspondence tests
            '''
            for t in testCases[rule]:
                if info:
                    print('='*20)
                    print('\ntesting', rule, 'with', len(t['pass']), 'pass case(s) and', len(t['fail']), 'fail case(s)')
                if debug >= 3:
                    print('> pass cases:', t['pass'])
                    print('> fail cases:', t['fail'])
                    print()
                # Create the mediator for this testCase
                m = Mediator(t['EDOAL'].getroot())
                # Create the input query an related expected reference query for this testCase
                inData = 'SELECT ?v WHERE {}'.format(t['data'][0])
                refData = 'SELECT ?v WHERE {}'.format(t['data'][1])
                if debug >= 1:
                    print('> input qry :', inData)
                if debug >= 3:
                    print('> expect qry:', refData)
                # PASS: Execute the test for each correspondence that is expected to pass on this query
                for p in t['pass']:
                    if debug >= 1:
                        print('testing pass case:', p)
                    r = m.corrs[p].translate(inData)
                    if debug >= 1:
                        print('> result qry:', r, '\n')
                    assert ''.join(refData.lower().split()) == ''.join(r.lower().split()), 'Translated data conflicts with expected data for correspondence {}'.format(p)
                
                # FAIL: Execute the test for each correspondence that is expected to fail on this query
                f = []                        
                for f in t['fail']: 
                    if debug >= 1:
                        print('testing fail case:', f)
#                     with self.assertRaises(NotImplementedError):
                    try:
                        r = m.corrs[f[0]].translate(inData)
                        # The following two lines should be dead code: Exception should have been raised.
                        print('Incorrect result:', r)
                        assert False, 'Test {} should have raised exception {}'.format(f[0], f[1])
                    except Exception as e: assert type(e) == f[1], 'Test {} should have raised exception {}; got {}'.format(f[0], f[1], type(e))
        
        
        def testFuncM():
            '''
                Execute all Mediator tests
            '''
            for t in testCases[rule]:
                if info:
                    print('='*20)
                    print('\ntesting', rule, 'with', len(t['pass']), 'pass case(s) and', len(t['fail']), 'fail case(s)')
                if debug >= 3:
                    print('> pass cases:', t['pass'])
                    print('> fail cases:', t['fail'])
                    print()

                # PASS: Execute the test for each defined correspondence file that is expected to pass
                for p, crit in t['pass'].items():
                    # Read and parse XML Alignment file 
                    with open(p, 'r') as xml:
                        rdf = etree.parse(xml)
                    if debug >= 1:
                        print('testing pass case:', p)
                        if debug >= 3:
                            for k,v in crit.items():
                                print('\t{}: {}'.format(k, v))
                    #TODO: Make a PASS test execution
                    r = Mediator(rdf.getroot())
                    if debug >= 1:
                        print('\tmedtr:', r)
                        #TODO: Correct TypeError that is raised for print('result:', r)
#                         print('result: TODO print the correct structure of the mediator and correspondence')
                    assert r.about == crit['about'], 'Mediator attribute "{}" conflicts with expected value {}'.format(r.about, crit['about'])
                    assert len(r.corrs) == crit['corrs'], 'Mediator attribute "{}" conflicts with expected value {}'.format(r.about, crit['corrs'])
                
                # FAIL: Execute the test for each correspondence that is expected to fail on this query
                                # Missing <Alignment> element
                f = []                        
                for f in t['fail']:
                    # Read and parse XML Alignment file 
                    with open(f[0], 'r') as xml:
                        rdf = etree.parse(xml)
                    if info or debug >= 1:
                        print('testing fail case:', f)
                    # Test that an incorrect EDOAL Alignment raise the correct exceptions
                    try:
                        m = Mediator(rdf.getroot())
                        assert False, 'Test {} should have raised exception {}'.format(f[0], f[1])
                    except Exception as e: assert type(e) == f[1], 'Test {} should have raised exception {}; got {}'.format(f[0], f[1], type(e))

        # Run the actual tests here                
        if rule == 'MEDIATOR': return testFuncM
        else: return testFuncC
    
    def setUp(self):
        self.testCases = {}

        # Mediator tests
        self.testCases['MEDIATOR'] = []
            
        self.testCases['MEDIATOR'].append({ 
            'pass': {'resources/wine_align.xml': 
                      {'about': 'http://oms.omwg.org/wine-vin/', 
                       'corrs': 5},
                     'resources/alignPass0.xml': 
                      {'about': 'http://oms.omwg.org/ontoA-ontoB/', 
                       'corrs': 1} 
                    },
            'fail': [['resources/alignWrong0A.xml', RuntimeError],          # Missing <Alignment> element
                    ['resources/alignWrong0B.xml', ValueError],             # Missing 'rdf:about="somename"' in <Alignment > element
                    ['resources/alignWrong1A.xml', NotImplementedError],    # Incorrect value for <Level> element: 2EDOAL expected
                    ['resources/alignWrong1B.xml', RuntimeError],           # Missing <Level> element 
                    ['resources/alignWrong2A.xml', RuntimeError],           # Missing <type> element 
                    ['resources/alignWrong2B.xml', ValueError],             # Illegal value for <Level> element 
                    ['resources/alignWrong3.xml', RuntimeError]             # Missing <map><Cell>...</Cell></map> element 
                    ]
              }
            )
                

        
        # SELECT tests
        self.testCases['SELECT'] = []
        with open('resources/wine_align.xml', 'r') as f:
            rdf = etree.parse(f)
        inData = '{?v <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear> .}' 
        outData = '{?v <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://ontology.deri.org/vin#Millesime> .}' 
        self.testCases['SELECT'].append({
            'EDOAL': rdf, 
            'data': [inData, outData],
            'pass': ['MappingRule_0'],
            'fail': [['MappingRule_1', NotImplementedError],
                    ['MappingRule_2', NotImplementedError],
                    ['MappingRule_3', NotImplementedError],
                    ['MappingRule_4', NotImplementedError] 
                    ]
              }
            )

    def tearDown(self):
        pass
        
    def testCorrespondence(self):
        Test.makeTestFunc('SELECT', self.testCases, info=False, debug=0)()

            
       
    def testMediator(self):
        '''
            Test __init__ 
            FAIL expected
            - raise AttributeError on empty Alignment, or data type other than Alignment
        ''' 
        with self.assertRaises(TypeError):
            Mediator(None) 
            
        with self.assertRaises(TypeError):
            Mediator("string type") 
            
        Test.makeTestFunc('MEDIATOR', self.testCases, info=False, debug=0)()

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testMediator']
    unittest.main()