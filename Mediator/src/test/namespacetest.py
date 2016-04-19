'''
Created on 12 apr. 2016

@author: brandtp
'''
import unittest
from utilities.namespaces import NSManager
from rdflib import term


class Test(unittest.TestCase):


    def setUp(self):
        testNS = {
                    'med'   : 'http://ds.tno.nl/mediator/1.0/',
                    'dc'    : 'http://purl.org/dc/elements/1.1/',
                    'edoal' : 'http://ns.inria.org/edoal/1.0/#'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(testNS, self.base)
        

    def tearDown(self):
        pass

    def testAsClarks(self):
        assert str(self.nsMgr.asClarks('dc:creator')) == '{http://purl.org/dc/elements/1.1/}creator'
        assert str(self.nsMgr.asClarks(':align')) == '{' + self.base + '}align', 'Expected: {}, got: {}'.format('{' + self.base + '}align', str(self.nsMgr.asClarks(':align')))
        with self.assertRaises(Exception): 
            self.nsMgr.asClarks('none:creator')
        with self.assertRaises(Exception): 
            self.nsMgr.asClarks('dc:creator:invalidQname')
        
    def testAsIri(self):
        assert str(self.nsMgr.asIRI('dc:creator')) == 'http://purl.org/dc/elements/1.1/creator', 'Expected: {}, got: {}'.format('http://purl.org/dc/elements/1.1/creator', str(self.nsMgr.asIRI('dc:creator')))
        assert str(self.nsMgr.asIRI(':align')) == self.base + 'align', 'Expected: {}, got: {}'.format(self.base + 'align', str(self.nsMgr.asIRI(':align'))) 
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('none:creator')
        with self.assertRaises(Exception): 
            self.nsMgr.asIRI('dc:creator:invalidQname')

    def testPrefix(self):
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/mediator/1.0/')
        assert pf == 'med', "Expected {}, got {}".format('med', pf)
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/non-existent/1.0/')
        # Test creation of new prefix
        cntr = self.nsMgr._prefixCntr
        expectedPF = self.nsMgr.newPrefix()[:-1] + str(cntr)
        assert pf == expectedPF, "Expected {}, got {}".format(expectedPF, pf)
        # Test new prefix has been registered, i.e., no new prefix has been created again
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/non-existent/1.0/')
        assert pf == expectedPF, "Expected {}, got {}".format(expectedPF, pf)
        
    def testIsQName(self):
        assert self.nsMgr.isQName('appel:ei')
        assert self.nsMgr.isQName(':ei')
        assert not self.nsMgr.isQName('appel:')
        assert not self.nsMgr.isQName(':appel:ei')
        assert not self.nsMgr.isQName('koe:appel:ei')
        assert not self.nsMgr.isQName('http://knowledgeweb.semanticweb.org/heterogeneity/alignment#egg')
    
    def testIsClarks(self):
        assert self.nsMgr.isClarks('{appel}ei')
        assert self.nsMgr.isClarks('{}ei')
        assert not self.nsMgr.isClarks('{appel}')
        assert not self.nsMgr.isClarks('appel{}')
        assert not self.nsMgr.isClarks('appel{ei}')
        assert not self.nsMgr.isClarks('{}{appel}ei')
        assert not self.nsMgr.isClarks('{koe}{appel}ei')
        assert not self.nsMgr.isClarks('}appel}ei')
        assert not self.nsMgr.isClarks('{appel{ei')
        assert not self.nsMgr.isClarks('{appel}{ei')
        assert not self.nsMgr.isClarks('{appel{}ei')

    def testSplit(self):
        # Success scenarios
        pf, prefix_expansion, iri_path = self.nsMgr.split('dc:path')
        assert pf == 'dc' and prefix_expansion == term.URIRef('http://purl.org/dc/elements/1.1/') and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        pf, prefix_expansion, iri_path = self.nsMgr.split(':path')
        assert pf == '' and prefix_expansion == term.URIRef('http://knowledgeweb.semanticweb.org/heterogeneity/alignment#') and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        pf, prefix_expansion, iri_path = self.nsMgr.split('{http://purl.org/dc/elements/1.1/}path')
        assert pf == 'dc' and prefix_expansion == term.URIRef('http://purl.org/dc/elements/1.1/') and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        pf, prefix_expansion, iri_path = self.nsMgr.split('{}path')
        assert pf == '' and prefix_expansion == term.URIRef('http://knowledgeweb.semanticweb.org/heterogeneity/alignment#') and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        # Fail scenarios
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('path:')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a*a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a!a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a@a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a$a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a%a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a^a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a&a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a(a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a)a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a_a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a-a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a+a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a=a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a[a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a]a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a|a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a;a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a"a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split("a'a")
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a~a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a`a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a,a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a<a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a>a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('a?a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.split('http://knowledgeweb.semanticweb.org/heterogeneity/alignment#path')

        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testAsClarks']
    unittest.main()