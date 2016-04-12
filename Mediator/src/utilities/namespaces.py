'''
Created on 1 apr. 2016

@author: brandtp
'''

# import elementtree.ElementTree as ET
import xml.etree.ElementTree as ET
from builtins import str


from rdflib import Graph
from rdflib.namespace import Namespace, NamespaceManager
from parsertools.base import ParseStruct
from parsertools.parsers.sparqlparser import parser
from rdflib.term import _is_valid_uri, URIRef

class NSManager(NamespaceManager):
    prefixN = 0
    RDFABOUT = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'
    ALIGNMENT = '{http://knowledgeweb.semanticweb.org/heterogeneity/alignment#}Alignment'
    EDOALCLASS = '{http://ns.inria.org/edoal/1.0/#}class'
    EDOALRELN = '{http://ns.inria.org/edoal/1.0/#}relation'
    EDOALPROP = '{http://ns.inria.org/edoal/1.0/#}property'
    EDOALINST = '{http://ns.inria.org/edoal/1.0/#}instance'
    EDOALCAOR = '{http://ns.inria.org/edoal/1.0/#}AttributeOccurenceRestriction'
    EDOALCADR = '{http://ns.inria.org/edoal/1.0/#}AttributeDomainRestriction'
    EDOALCATR = '{http://ns.inria.org/edoal/1.0/#}AttributeTypeRestriction'
    EDOALCAVR = '{http://ns.inria.org/edoal/1.0/#}AttributeValueRestriction'
    EDOALDIRECTION = '{http://ns.inria.org/edoal/1.0/#}direction'
    EDOALAPPLY = '{http://ns.inria.org/edoal/1.0/#}Apply'
    EDOALOPRTR = '{http://ns.inria.org/edoal/1.0/#}operator' 
       
    def __init__(self, nsDict={}, base=''):
        self.graph = Graph()
        self.base = base
        super().__init__(self.graph)
        self.bindPrefixes(nsDict)

    def split(self, string):
        if string[0] == '{':
            iri, local = string[1:].split("}")
            if iri=='': iri = self.base
            pf = self.getPrefix(iri)
        else: raise NotImplementedError("Cannot split iri {} yet; please implement me".format(string))
        return pf, iri, local
    
    def getPrefix(self, iri):
        if isinstance(iri, str) or isinstance(iri, Namespace):
            iri = URIRef(iri)
        for pf, ns in self.namespaces():
            if ns == iri: return pf
        # No getPrefix found, need to add a new getPrefix
        self.prefixN+=1
        pf = "mns" + str(self.prefixN)
        self.bind(pf, URIRef(iri))
        return pf
        
    def bindPrefixes(self, nsDict, **args):
        assert isinstance(nsDict,dict)
        for prefix in nsDict:
            self.bind(prefix, nsDict[prefix], **args)
            
    def bindPrefixesFrom(self, rq=None):
        if isinstance(rq, ParseStruct):
            prefixDecls = rq.searchElements(element_type=parser.PrefixDecl)
            nsDict = {}
            for p in prefixDecls:
                qry_prefix, qry_namespace = str(p.prefix)[:-1], str(p.namespace)[1:-1]
                nsDict[qry_prefix] = qry_namespace
            self.bindPrefixes(nsDict)
        else: raise Exception('Cannot bind prefixes from {}'.format(type(rq)))
        
    def asIRI(self, qname):
        assert isinstance(qname,str) 
        prefix, name = qname.split(":")
        if prefix == '':
            if self.base[-1] in ["/", "#"]:
                return self.base + name
            else: return self.base + "/" + name
        for nsPF, ns in self.namespaces():
            if nsPF == prefix:
                return "".join((ns, name))
        raise Exception('Cannot turn "{}" into IRI due to missing XMLNS getPrefix in registered namespaces'.format(qname))
    
    def asClarks(self, qname):
        assert isinstance(qname,str) 
        prefix, name = qname.split(":")
        if prefix == '':
            return "{" + self.base + "}" + name
        for nsPF, ns in self.namespaces():
            if nsPF == prefix:
                return "{"+ ns + "}" + name
        raise Exception('Cannot turn "{}" into IRI due to missing XMLNS getPrefix in registered namespaces'.format(qname))


'''
=====================================================================================
= BELOW THIS LINE, NO OPERATIONAL CODE. JUST SOME OLD STUFF MAYBE OF INTEREST LATER =
=====================================================================================
'''
        
        
class QualifiedName(tuple):
    '''
    Namespaces refer to the use of qualified names. This class represents a qualified name, and its 
    valid namespace conversions
    '''
    def __init__(self, args):
        '''
        A QN essentially represents a tuple (namespace URI, local part).
        '''
        if args == 0: 
            pass
        elif args == 1 and isinstance(args, tuple):
            self = args
        elif args == 1 and isinstance(args, str):
            self = args
        elif args == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            self.URI = args[0]
            self.localPart = args[1]
        else: raise RuntimeError("Can create Qualified Name from 2-tuple, Clark's notation or two strings only, got {}".format(args))

        
    def _isCN(self, name):
        ''' Clark's notation represents the format {uri}local
        '''
        if name[0] == '{':
            uri, tag = name[1:].split("}")
            if not (list(tag) in ['appelepap']):
                pass
            
    def fromClarksNotation(self, name):
        if self._isCN(name):
            uri, tag = name[1:].split("}")
            return (uri, tag)
        else: return None


class nsParserTool():


    def parse_and_get_ns(self, file):
        events = "start", "start-ns"
        root = None
        ns = {}
        for event, elem in ET.iterparse(file, events):
            if event == "start-ns":
                if elem[0] in ns and ns[elem[0]] != elem[1]:
                    # NOTE: It is perfectly valid to have the same getPrefix refer
                    #     to different URI namespaces in different parts of the
                    #     document. This exception serves as a reminder that this
                    #     solution is not robust.    Use at your own peril.
                    raise KeyError("Duplicate getPrefix with different URI found.")
                ns[elem[0]] = "{%s}" % elem[1]
            elif event == "start":
                if root is None:
                    root = elem
        return ET.ElementTree(root), ns
    
    NS_MAP = "xmlns:map"
    def parse_with_nsmap(self, file):
    
        events = "start", "start-ns", "end-ns"
    
        root = None
        ns_map = []
    
        for event, elem in ET.iterparse(file, events):
            if event == "start-ns":
                ns_map.append(elem)
            elif event == "end-ns":
                ns_map.pop()
            elif event == "start":
                if root is None:
                    root = elem
                elem.set(self.NS_MAP, dict(ns_map))
    
        return ET.ElementTree(root)
    
    def getNSMap(self):
        return(self.NS_MAP)
