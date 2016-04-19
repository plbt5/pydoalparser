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
from rdflib import term

class NSManager(NamespaceManager):
    _prefixCntr = 0
    RDFABOUT = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'
    RDFPARSTP = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}parseType'
    ALIGNMENT = '{http://knowledgeweb.semanticweb.org/heterogeneity/alignment#}Alignment'
       
    def __init__(self, nsDict={}, base=''):
        self.graph = Graph()
        self.base = term.URIRef(base)
        super().__init__(self.graph)
        self.bindPrefixes(nsDict)

    def newPrefix(self, base_name='mns'):
        self._prefixCntr+=1
        return base_name + str(self._prefixCntr)

    def isQName(self,qname):
        '''
        Validity is defined by absence of invalid characters, and
        conforming to structure [(prefix)+ ':' local]
        '''
        if term._is_valid_uri(qname): # check for invalid characters
            parts = []
            parts = qname.split(':')
            if len(parts) == 2:
                return parts[1] != '' and parts[1][:2] != '//' 
            elif len(parts) == 1:
                return qname[0] == ':'
            else: return False
        return False

    def isClarks(self, string):
        curlyBs = set('{}')
        if term._is_valid_uri(''.join([c for c in string if c not in curlyBs])): # check for invalid characters, except the '{}'
            parts = []
            parts = string.split("}")
            if len(parts) == 2:
                return parts[1] != '' and term._is_valid_uri(parts[1]) and term._is_valid_uri(parts[0][1:])
            elif len(parts) == 1:
                return parts[0] == '{'
        return False
    
    def expand(self, prefix):
        assert term._is_valid_uri(prefix) , "Cannot expand illegal prefix ({})".format(prefix)
        result = []
        for nsPF, ns in self.namespaces():
            if nsPF == prefix:
                result.append(ns)
        if len(result) == 1: return result[0]
        assert len(result) == 0, "Did not expect more than one namespace matches for {}".format(prefix)
        return result
        
    def split(self, string):
        '''
        Split namespace notation into prefix, prefix_expansion, iri_path. 
        Currently only able to split from Clark's notation as input.
        Notations without '{}' part assumes to live in Base
        '''
        prefix = ''
        if self.isClarks(string):
            prefix_exp_string, iri_path = string[1:].split("}")
            prefix_expansion = term.URIRef(prefix_exp_string)
            if prefix_expansion==term.URIRef(''): prefix_expansion = self.base
            else: prefix = self.getPrefix(prefix_expansion)
        elif self.isQName(string):
            prefix, iri_path = string.split(':')
            if prefix == '': 
                prefix_expansion = self.base 
            else:
                prefix_expansion = self.expand(prefix)
        else: raise NotImplementedError("Cannot split prefix_expansion {} (yet; please implement me)".format(string))
        return prefix, prefix_expansion, iri_path
    
    def getPrefix(self, pf_expansion):
        if isinstance(pf_expansion, str) or isinstance(pf_expansion, Namespace):
            pf_expansion = term.URIRef(pf_expansion)
        pflist = []
        for pf, ns in self.namespaces():
            if ns == pf_expansion: pflist.append(pf)
        if len(pflist) == 1:
            return pflist[0]
        else:
            assert len(pflist) == 0, "More than one prefix found for namespace {}".format(ns)
            # No prefix found, check base
            pf = ''
            if pf_expansion != self.base:
                # need to add a new getPrefix, and register the (prefix,expanded_prefix) pair
                pf = self.newPrefix()
                self.bind(pf, pf_expansion)
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
        
    def asQName(self, string):
        assert term._is_valid_uri(string), 'Cannot make QName from invalid uri, got <{}>'.format(string)
        if self.isClarks(string):
            ns, lbl = string[1:].split("}")
            return self.getPrefix(ns), lbl
        elif self.isQName(string):
            return string.split(":")
        elif string.rsplit("#") != '':
            # Assume one '#' character only
            ns, lbl = string.rsplit('#')
            return self.getPrefix(ns), lbl
        elif string.rsplint('/') != '':
            ns, lbl = string.rsplint('/')
            return self.getPrefix(ns), lbl
        else: raise RuntimeWarning("Cannot convert ")
        
    def asIRI(self, qname):
        assert isinstance(qname,str) and self.isQName(qname)
        prefix, name = qname.split(":")
        if prefix == '':
            if self.base[-1] in ["/", "#"]:
                return self.base + name
            else: return self.base + "/" + name
        for nsPF, ns in self.namespaces():
            if nsPF == prefix:
                return "".join((ns, name))
        raise Exception('Cannot turn "{}" into IRI due to missing XMLNS prefix in registered namespaces'.format(qname))
    
    def asClarks(self, qname):
        assert isinstance(qname,str) and self.isQName(qname)
        prefix, name = qname.split(":")
        if prefix == '':
            return "{" + self.base + "}" + name
        for nsPF, ns in self.namespaces():
            if nsPF == prefix:
                return "{"+ ns + "}" + name
        raise Exception('Cannot turn "{}" into IRI due to missing XMLNS prefix in registered namespaces'.format(qname))

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
