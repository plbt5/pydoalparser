'''
Created on 12 apr. 2016

@author: brandtp
'''
import unittest
from utilities.namespaces import NSManager
import inspect


class TestNSManager(unittest.TestCase):


    def setUp(self):
        testNS = {
                    'med'   : 'http://ds.tno.nl/mediator/1.0/',
                    'dc'    : 'http://purl.org/dc/elements/1.1/',
                    'edoal' : 'http://ns.inria.org/edoal/1.0/#',
                    'test'  : 'http://ds.tno.nl/mediator/1.0'
        }
        self.base = 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
        self.nsMgr = NSManager(nsDict=testNS, base=self.base)
        

    def tearDown(self):
        pass

    def testNsConcat(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        assert self.nsMgr.nsConcat('http://www.w3.org/2001/XMLSchema#', 'appel') == '<http://www.w3.org/2001/XMLSchema#appel>', "got {}".format(self.nsMgr.nsConcat('http://www.w3.org/2001/XMLSchema#', 'appel'))
        assert self.nsMgr.nsConcat('<http://www.w3.org/2001/XMLSchema#>', 'appel') == '<http://www.w3.org/2001/XMLSchema#appel>', "got {}".format(self.nsMgr.nsConcat('<http://www.w3.org/2001/XMLSchema#>', 'appel'))
        assert self.nsMgr.nsConcat('http://www.w3.org/2001/XMLSchema/', 'appel') == '<http://www.w3.org/2001/XMLSchema/appel>', "got {}".format(self.nsMgr.nsConcat('http://www.w3.org/2001/XMLSchema/', 'appel'))
        assert self.nsMgr.nsConcat('<http://www.w3.org/2001/XMLSchema/>', 'appel') == '<http://www.w3.org/2001/XMLSchema/appel>', "got {}".format(self.nsMgr.nsConcat('<http://www.w3.org/2001/XMLSchema/>', 'appel'))
        assert self.nsMgr.nsConcat('http://www.w3.org/2001/XMLSchema', 'appel') == '<http://www.w3.org/2001/XMLSchema/appel>', "got {}".format(self.nsMgr.nsConcat('http://www.w3.org/2001/XMLSchema', 'appel'))
        assert self.nsMgr.nsConcat('<http://www.w3.org/2001/XMLSchema>', 'appel') == '<http://www.w3.org/2001/XMLSchema/appel>', "got {}".format(self.nsMgr.nsConcat('<http://www.w3.org/2001/XMLSchema>', 'appel'))
        print(". done")

    def testCONSTANTS(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        assert self.nsMgr.CLARKS_LABELS['XSDSTRING'] == '{http://www.w3.org/2001/XMLSchema#}string'
        assert self.nsMgr.CLARKS_LABELS['RDFABOUT'] == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'
        assert self.nsMgr.CLARKS_LABELS['RDFDATATP'] == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype'
        assert self.nsMgr.CLARKS_LABELS['RDFPARSTP'] == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}parseType'
        assert self.nsMgr.CLARKS_LABELS['RDFDATATP'] == '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype'
        assert self.nsMgr.CLARKS_LABELS['ALIGNMENT'] == '{http://knowledgeweb.semanticweb.org/heterogeneity/alignment#}Alignment'
        print(". done")

    def testSplitIRI(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        assert ('align',"Alignment") == self.nsMgr._splitIRI("<http://knowledgeweb.semanticweb.org/heterogeneity/alignment#Alignment>"), "Unexpectedly got '{}'".format(self.nsMgr._splitIRI("<http://knowledgeweb.semanticweb.org/heterogeneity/alignment#Alignment>"))
        assert ('med',"Alignment") == self.nsMgr._splitIRI("<http://ds.tno.nl/mediator/1.0/Alignment>")
        with self.assertRaises(AssertionError): 
            self.nsMgr._splitIRI("http:Alignment")
        with self.assertRaises(AssertionError): 
            self.nsMgr._splitIRI("<http:Alignment>")
        with self.assertRaises(AssertionError): 
            self.nsMgr._splitIRI("Alignment")
        with self.assertRaises(AssertionError): 
            self.nsMgr._splitIRI("<Alignment>")
        with self.assertRaises(AssertionError): 
            self.nsMgr._splitIRI("{http://purl.org/dc/elements/1.1/}creator")
        print(". done")
        
    def testAsClarks(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        assert isinstance(self.nsMgr.asClarks('dc:creator'),str)
        assert self.nsMgr.asClarks('dc:creator') == '{http://purl.org/dc/elements/1.1/}creator', 'Expected "{http://purl.org/dc/elements/1.1/}creator", got {}'.format(self.nsMgr.asClarks('dc:creator'))
        assert self.nsMgr.asClarks("<http://purl.org/dc/elements/1.1/creator>") == '{http://purl.org/dc/elements/1.1/}creator', 'Expected "{http://purl.org/dc/elements/1.1/}creator", got {}'.format(self.nsMgr.asClarks("<http://purl.org/dc/elements/1.1/creator>"))
        assert self.nsMgr.asClarks(':align') == '{' + self.base + '}align', 'Expected: {}, got: {}'.format('{' + self.base + '}align', str(self.nsMgr.asClarks(':align')))
        with self.assertRaises(Exception): 
            self.nsMgr.asClarks('none:creator')
        with self.assertRaises(Exception): 
            self.nsMgr.asClarks('dc:creator:invalidQname')
        print(". done")
        
    def testAsIri(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        print(str(self.nsMgr))
        # Success scenarios
        inpstr = 'dc:creator'
        expstr = '<http://purl.org/dc/elements/1.1/creator>'
        assert str(self.nsMgr.asIRI(inpstr)) == expstr, 'Expected: {}, got: {}'.format(expstr, str(self.nsMgr.asIRI(inpstr))) 
        inpstr = 'test:creator'
        expstr = '<http://ds.tno.nl/mediator/1.0/creator>'
        assert str(self.nsMgr.asIRI(inpstr)) == expstr, 'Expected: {}, got: {}'.format(expstr, str(self.nsMgr.asIRI(inpstr))) 
        inpstr = ':align'
        expstr = '<'+ self.base + 'align>'
        assert str(self.nsMgr.asIRI(inpstr)) == expstr, 'Expected: {}, got: {}'.format(expstr, str(self.nsMgr.asIRI(inpstr))) 
        inpstr = '{}align'
        expstr = '<'+ self.base + 'align>'
        assert str(self.nsMgr.asIRI(inpstr)) == expstr, 'Expected: {}, got: {}'.format(expstr, str(self.nsMgr.asIRI(inpstr))) 
        inpstr = '<http://purl.org/dc/elements/1.1/creator>'
        expstr = '<http://purl.org/dc/elements/1.1/creator>'
        assert str(self.nsMgr.asIRI(inpstr)) == expstr, 'Expected: {}, got: {}'.format(expstr, str(self.nsMgr.asIRI(inpstr))) 
        inpstr = '{http://purl.org/dc/elements/1.1/}creator'
        expstr = '<http://purl.org/dc/elements/1.1/creator>'
        assert str(self.nsMgr.asIRI(inpstr)) == expstr, 'Expected: {}, got: {}'.format(expstr, str(self.nsMgr.asIRI(inpstr))) 
        # Fail scenarios
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('<>')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri(':')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('<:>')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('{}')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('<{}>')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('{<>}')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('{}creator{}')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('{}{}creator')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('<none:creator>')
        with self.assertRaises(Exception): 
            self.nsMgr.asIri('<dc:creator:invalidQname>')
        print(". done")

    def testPrefix(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/mediator/1.0/')
        assert pf == 'med', "Expected {}, got {}".format('med', pf)
        # TestNSManager creation of new prefix
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/non-existent/1.0/')
        cntr = self.nsMgr._prefixCntr
        expectedPF = self.nsMgr.newPrefix()[:-1] + str(cntr)
        assert pf == expectedPF, "Expected {}, got {}".format(expectedPF, pf)
        # TestNSManager new prefix has been registered, i.e., no new prefix has been created again
        pf = self.nsMgr.getPrefix('http://ds.tno.nl/non-existent/1.0/')
        assert pf == expectedPF, "Expected {}, got {}".format(expectedPF, pf)
        print(". done")
        
    def testIsQName(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        assert self.nsMgr.isQName('appel:ei')
        assert self.nsMgr.isQName(':ei')
        assert not self.nsMgr.isQName('')
        assert not self.nsMgr.isQName(':')
        assert not self.nsMgr.isQName('appel:')
        assert not self.nsMgr.isQName(':appel:ei')
        assert not self.nsMgr.isQName('koe:appel:ei')
        assert not self.nsMgr.isQName('http://knowledgeweb.semanticweb.org/heterogeneity/alignment#egg')
        print(". done")
    
    def testIsClarks(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        assert self.nsMgr.isClarks('{appel}ei')
        assert self.nsMgr.isClarks('{}ei')
        assert not self.nsMgr.isClarks('')
        assert not self.nsMgr.isClarks('{}')
        assert not self.nsMgr.isClarks('{appel}')
        assert not self.nsMgr.isClarks('appel{}')
        assert not self.nsMgr.isClarks('appel{ei}')
        assert not self.nsMgr.isClarks('{}{appel}ei')
        assert not self.nsMgr.isClarks('{koe}{appel}ei')
        assert not self.nsMgr.isClarks('}appel}ei')
        assert not self.nsMgr.isClarks('{appel{ei')
        assert not self.nsMgr.isClarks('{appel}{ei')
        assert not self.nsMgr.isClarks('{appel{}ei')
        print(". done")
        
    def testIsIRI(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        assert self.nsMgr.isIRI('<preamb://authority.name/iri_expans/iri_path>')
        assert self.nsMgr.isIRI('<preamb://authority.org/iri_expans/iri_expans/iri_path>')
        assert self.nsMgr.isIRI('<preamb://authority.org/iri_expans#iri_path>')
        assert self.nsMgr.isIRI('<preamb://authority.org/iri_expans/iri_expans#iri_path>')
        assert self.nsMgr.isIRI('<http://knowledgeweb.semanticweb.org/heterogeneity/alignment#Alignment>')
        assert self.nsMgr.isIRI('<http://ds.tno.nl/mediator/1.0/Alignment>')
        assert self.nsMgr.isIRI('<preamb://authority.org/iri_expans/iri_expans#subpath/path>')
        
        assert not self.nsMgr.isIRI('preamb://authority.fives/iri_expans/iri_path')
        assert not self.nsMgr.isIRI('preamb://authority.name/iri_expans/iri_path>')
        assert not self.nsMgr.isIRI('<preamb://authority.name/iri_expans/iri_path')
        assert not self.nsMgr.isIRI('<preamb://authority.l/iri_expans/iri_path>')
        assert not self.nsMgr.isIRI('<preamb://authority./iri_expans/iri_path>')
        assert not self.nsMgr.isIRI('<preamb://authority/iri_expans/iri_path>')
        assert not self.nsMgr.isIRI('<://authority.something/iri_expans/iri_path>')
        assert not self.nsMgr.isIRI('<preamb:authority.something/iri_expans/iri_path>')
        assert not self.nsMgr.isIRI('<preamb:authority>')
        assert not self.nsMgr.isIRI('<{preamb://authority.org/iri_expans/iri_expans#}iri_path>')
        assert not self.nsMgr.isIRI('<{preamb://authority.org/iri_expans/iri_expans/}iri_path>')
        assert not self.nsMgr.isIRI('<preamb://authority.org/iri_expans/iri_expan/iri_path#>')
        assert not self.nsMgr.isIRI('<preamb://authority.org/iri_expans/iri_expans#iri_path/>')
        assert not self.nsMgr.isIRI('<preamb://authority.org/iri_expans/iri_expans/iri_path/>')
        print(". done")
        

    def testSplit(self):
        print('Testcase {}\n\ttesting {} ..'.format(self.__class__.__name__,inspect.currentframe().f_code.co_name), end="", flush=True)
        # Success scenarios
        pf, prefix_expansion, iri_path = self.nsMgr.splitIri('dc:path')
        assert pf == 'dc' and prefix_expansion == 'http://purl.org/dc/elements/1.1/' and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        pf, prefix_expansion, iri_path = self.nsMgr.splitIri(':path')
        assert pf == '' and prefix_expansion == 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#' and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        pf, prefix_expansion, iri_path = self.nsMgr.splitIri('{http://purl.org/dc/elements/1.1/}path')
        assert pf == 'dc' and prefix_expansion == 'http://purl.org/dc/elements/1.1/' and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        pf, prefix_expansion, iri_path = self.nsMgr.splitIri('{}path')
        assert pf == '' and prefix_expansion == 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#' and iri_path == 'path', "Got pf:{}, expansion:{}, path:{}".format(pf,prefix_expansion, iri_path)
        # Fail scenarios
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('path:')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a*a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a!a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a@a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a$a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a%a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a^a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a&a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a(a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a)a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a_a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a-a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a+a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a=a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a[a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a]a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a|a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a;a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a"a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri("a'a")
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a~a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a`a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a,a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a<a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a>a')
        with self.assertRaises(NotImplementedError): 
            pf, prefix_expansion, iri_path = self.nsMgr.splitIri('a?a')
        print(". done")

        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testAsClarks']
    unittest.main()