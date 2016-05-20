'''
Created on 26 feb. 2016

@author: brandtp
'''
import unittest
from mediator.mediator import Mediator
from utilities import namespaces


class TestMediator(unittest.TestCase):

    
    def setUp(self):
        from mediator.EDOALparser import ParseAlignment
        ns = {'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
              'xsd': "http://www.w3.org/2001/XMLSchema#",
              'align':"http://knowledgeweb.semanticweb.org/heterogeneity/alignment#",
              'edoal':'http://ns.inria.org/edoal/1.0/#',
              't'   : 'http://ts.tno.nl/mediator/test#'
              }
        self.nsMgr = namespaces.NSManager(ns, "http://ts.tno.nl/mediator/test#")
        self.align = ParseAlignment("resources/alignPassTransformation1.xml")
        self.query = '''
            PREFIX ns:     <http://tutorial.topbraid.com/ontoA/>
            PREFIX foaf:   <http://xmlns.com/foaf/0.1/>
            PREFIX xsd:    <http://www.w3.org/2001/XMLSchema>
            
            SELECT ?p ?t WHERE 
                {
                    ?p a foaf:Person .
                    ?p ns:hasTemp ?t .
                    ?p ns:hasAge ?a .
                    ?t a ns:TempInC .
                     FILTER ( 
                                 ( ?t > 37.0 ) &&
                                 ( ?a < 37.0 ) 
                             ).
                } 
            '''

    def tearDown(self):
        pass
             
       
    def testMediator(self):

        m = Mediator(self.align)
        m.translate(self.query)
        
        with self.assertRaises(TypeError):
            Mediator(None) 
             
        with self.assertRaises(TypeError):
            Mediator("string type") 

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testMediator']
    unittest.main()