'''
Created on 26 feb. 2016

@author: brandtp
'''
import unittest
from mediator.mediator import Mediator
from utilities import namespaces


class TestMediator(unittest.TestCase):

    
    def setUp(self):
        from mediator.EDOALparser import Alignment

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

    def tearDown(self):
        pass
             
       
    def testMediator(self):

        # Fail cases
        with self.assertRaises(AssertionError):
            Mediator(None) 
        with self.assertRaises(AssertionError):
            Mediator(12.0) 
        
        # Success case
        m = Mediator(about='ts:myMediator', nsDict={'ts'   : 'http://ts.tno.nl/mediator/1.0/test#'})
        print("m: \n", m.getNSs())
        assert m.getNSs().nsConcat(m.getNSs().expand('ts'),'myMediator') == m.getName(), "Expected {}, got {}".format(m.getNSs().nsConcat('ts','myMediator'), m.getName())
        
        m.addAlignment(alignment_filename=self.fn)
        for align in m.alignments:
            print("Alignment: ", m.alignments[align].getAbout())
            print("\tsource Ont: ", m.alignments[align].getSrcOnto())
            print("\ttarget Ont: ", m.alignments[align].getTgtOnto())
        
        m.translate(self.query)

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testMediator']
    unittest.main()