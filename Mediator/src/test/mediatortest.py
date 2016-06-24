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
        self.mediator = Mediator(about='ts:myMediator', nsDict={'ts'   : 'http://ts.tno.nl/mediator/1.0/test#'})
        assert self.mediator.getNSs().nsConcat(self.mediator.getNSs().expand('ts'),'myMediator') == self.mediator.getName(), "Expected {}, got {}".format(self.mediator.getNSs().nsConcat(self.mediator.getNSs().expand('ts'),'myMediator'), self.mediator.getName())
        

    def tearDown(self):
        pass
             
       
    def testMediator(self):

        # Fail cases
        with self.assertRaises(AssertionError):
            Mediator(None) 
        with self.assertRaises(AssertionError):
            Mediator(12.0) 
        
        # Success case
#         print("Input query: \n", self.query)
#         print("m: \n", m.getNSs())

        self.mediator.addAlignment(alignment_filename=self.fn)
#         for align in m.alignments:
#             print(str(m.alignments[align]))
#             print("\tsource Ont: ", m.alignments[align].getSrcOnto())
#             print("\ttarget Ont: ", m.alignments[align].getTgtOnto())

        result = self.mediator.translate(self.query)
        print(str(result))
        assert str(result) == "PREFIX mns_2: <http://ts.tno.nl/mediator/1.0/examples/ontoTemp1B#> PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> SELECT ?p ?t WHERE { ?p <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://ts.tno.nl/mediator/1.0/examples/ontoTemp1B#PatientNaam> . ?p <http://ts.tno.nl/mediator/1.0/examples/ontoTemp1B#temperature_inF> ?t ; <http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A#hasAge> ?a . FILTER ( ( ?t > 98.6 ) && ( ?a < 37.0 ) ) }"

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testMediator']
    unittest.main()