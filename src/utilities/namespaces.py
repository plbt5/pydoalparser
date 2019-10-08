'''
Created on 1 apr. 2016

@author: brandtp
'''

# TODO: gebruik lxml in plaats van xml.etree
# TODO: Vervang namespace DIY implementation by the rfc3987 package 
import xml.etree.ElementTree as ET
from builtins import str
import warnings
from rfc3987 import parse, match


class NSManager():
    _prefixCntr = 0
    _CLARKS = lambda x, y: '{' + x + '}' + y
    
    NS = {
          'xsd' : 'http://www.w3.org/2001/XMLSchema#',
          'rdf' : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
          'tno' : 'http://ts.tno.nl/mediator/1.0/',
          'align' : 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#'
    }
    
    CLARKS_LABELS = {
        # XSD names
        'XSDSTRING'  : _CLARKS(NS['xsd'], 'string'),
        # RDF names
        'RDFABOUT'   : _CLARKS(NS['rdf'], 'about'),
        'RDFDATATP'  : _CLARKS(NS['rdf'], 'datatype'),
        'RDFPARSTP'  : _CLARKS(NS['rdf'], 'parseType'),
        # Edoal Alignment names
        'ALIGNMENT'  : _CLARKS(NS['align'], 'Alignment')
    }
    
    LOCAL_BASE_PATH = 'C:/Users/brandtp/Documents/Git/Mediator/Mediator/src/'
    # TODO: Drop Quick & Dirty LOCAL_BASE_PATH name specification, and move it to external configuration. 
 
    @staticmethod
    def _valid_uri_chars(exclude=[], *, uri_string=''):
        # The following characters are reserved characters for URI's, hence invalid (https://tools.ietf.org/html/rfc3986#page-12)
        # Added the '{', '}' and '^' characters
        # TODO: Replace DIY namespace tooling for rfc3987 package
        for c in ["[", "]", "@", "!", "$", "&", "'", "(", ")", "*", "+", ",", ";", "=", "{", "}", "^"]:
            if c in uri_string: 
                if not c in exclude: return False
        return True

    @classmethod
    def isQName(cls, qname):
        '''
        Validity is defined by absence of invalid characters, and
        conforming to structure [(prefix)? ':' local]
        '''
        if qname != "":
            if cls._valid_uri_chars(uri_string=qname, exclude=[':']):  # check for invalid characters
                parts = []
                parts = qname.split(':')
                if len(parts) == 2:
                    return parts[1] != '' and parts[1][:2] != '//' 
                elif len(parts) == 1:
                    return qname[0] == ':'
                else: return False
        return False
    
    @classmethod
    def isIRI(cls, iri):
        '''
        Validity is defined by absence of invalid characters, and
        conforming to structure <some_text '://' authority '/' iri_expansion  ('/'|'#') iri_path>
        '''
        # TODO: Replace own code for available tooling from rfc3987 package
        if cls._valid_uri_chars(uri_string=iri, exclude=['/', ':']):  # check for invalid characters
            preamble = []
            # Check beginning '<' and closing '>', then strip these for less complex evaluation
            if iri[0] != '<' or iri[-1] != '>': return False
            iri = iri[1:-1]
            preamble = iri.split(':')
            if len(preamble) == 2 and preamble[0] != '':
                # Found exactly 1 ':', now check if it is part of '://'?
                if preamble[1][:2] == '//':
                    # Found the authority part, but does it end with a domain-code?
                    auth = preamble[1][2:].split('/', 1)
                    if auth[0] == '/' or auth[0] == '': return False 
                    dom = auth[0].rsplit('.', 1)
                    if len(dom) > 1:
                        if len(dom[1]) >= 2 and len(dom[1]) <= 4:
                            # Find the /iri_expansion?
                            iriparts = auth[1].rsplit('/', 1)
                            # Found an iri_path, if it's trailing it represents an invalid path
                            if iriparts[-1] == '': return False
                            hashparts = auth[1].rsplit('#')
                            if len(hashparts) == 1: return True
                            if len(hashparts) == 2:
                                # Only one '#' present
                                if '#' in iriparts[-1] and hashparts[-1] == '':
                                    # Found a trailing '#', which indicates an invalid iri_path
                                    return False
                                # Found one single '#', only when its last part doesn't carry a '/', it is a valid iri
                                # TODO: Check whether an iri cannot have a '/' after the '#', now ignore this rule
#                                 return not ('/' in hashparts[-1])
                                return True
        return False

    @classmethod
    def isClarks(cls, string):
        '''
        Validity is defined by absence of invalid characters, and
        conforming to structure ['{' (prefix_exp_string)+ '}' local]
        '''
        if cls._valid_uri_chars(uri_string=string, exclude=['{', '}']):  # check for invalid characters, except the '{}'
            parts = []
            parts = string.split("}")
            if len(parts) == 2:
                return parts[1] != '' and cls._valid_uri_chars(uri_string=parts[1]) and cls._valid_uri_chars(uri_string=parts[0][1:])
            elif len(parts) == 1:
                return parts[0] == '{'
        return False

    def __init__(self, nsDict={}, base=''):
        if base == '': base = self.NS['tno']
        self.base = base
        self.nsmap = {None: base}  # the default namespace (no prefix)
        self.nspam = {base: None}  # the reversed namespace map
        self.bindPrefixes(self.NS)  # Register the standard namespaces
        self.bindPrefixes(nsDict=nsDict)

    def newPrefix(self, base_name='mns_'):
        self._prefixCntr += 1
        return base_name + str(self._prefixCntr)
    
    def expand(self, prefix):
        assert self._valid_uri_chars(uri_string=prefix) , "Cannot expand illegal prefix ({})".format(prefix)
        if prefix == '': prefix = None
        if prefix in self.nsmap:
            return self.nsmap[prefix]
        else: return prefix
        
    def splitIri(self, iri_string):
        '''
        Split namespace notation into prefix, prefix_expansion, iri_path. 
        input: string, representing full IRI, in either:
            1 - Clark's notation;
            2 - Qualified Name;
            3 - Full expanded IRI
        Notations without '{}' part assumes to live in Base
        '''
        prefix = ''
        if self.isClarks(iri_string):
            prefix_exp_string, iri_path = iri_string[1:].split("}")
            prefix_expansion = prefix_exp_string
            if prefix_expansion == '': prefix_expansion = self.base
            else: prefix = self.getPrefix(prefix_expansion)
        elif self.isQName(iri_string):
            prefix, iri_path = iri_string.split(':')
            if prefix == '': 
                prefix_expansion = self.base 
            else:
                prefix_expansion = self.expand(prefix)
        elif self.isIRI(iri_string):
            prefix, iri_path = self._splitIRI(iri_string)
            prefix_expansion = self.expand(prefix)
        else: raise NotImplementedError("Cannot split prefix_expansion {} (yet; please implement me)".format(iri_string))
        return prefix, prefix_expansion, iri_path
    
    def getPrefix(self, pf_expansion):
        assert isinstance(pf_expansion, str), "Cannot find prefix in non-string {}, quitting".format(type(pf_expansion))
        if pf_expansion in self.nspam:
            return self.nspam[pf_expansion]
        else: 
            pf = self.newPrefix()
            self.bindPrefixes({pf: pf_expansion})
            return pf
        
    def bindPrefixes(self, nsDict):
        assert isinstance(nsDict, dict)
        for k in nsDict:
            try:
                self.nsmap[k] = nsDict[k]
                self.nspam[nsDict[k]] = k
            except: raise RuntimeError('Cannot register double prefixes {} or double namespaces {}'.format(k, nsDict[k]))
            
#     def bindPrefixesFrom(self, rq=None):
#         warnings.warn("Binding prefixes from sparql query to the namespace tabel is PLAIN WRONG!! because you need to unbind them as well")
#         if isinstance(rq, ParseStruct):
#             prefixDecls = rq.searchElements(element_type=sparqlparser.PrefixDecl)
#             nsDict = {}
#             for p in prefixDecls:
#                 qry_prefix, qry_namespace = str(p.prefix)[:-1], str(p.namespace)[1:-1]
#                 nsDict[qry_prefix] = qry_namespace
#             self.bindPrefixes(nsDict)
#         else: raise Exception('Cannot bind prefixes from {}'.format(type(rq)))
    
    def _splitIRI(self, in_string):
        '''
        Split an IRI and return its function_path and the advancing base-url, the latter in its prefix
        form as it can be found in the namespace table.
        '''
        assert self.isIRI(in_string), "Expected to split an IRI, but got <{}>".format(in_string)
        # Get rid of the '< >' pair
        if in_string[0] == '<': in_string = in_string[1:]
        if in_string[-1] == '>': in_string = in_string[:-1]
        if '#' in in_string:
            # Assume one '#' character only
            ns, lbl = in_string.rsplit('#', maxsplit=1)
            pf = self.getPrefix(ns + '#')
            return pf, lbl
        elif '/' in in_string:
            ns, lbl = in_string.rsplit('/', maxsplit=1)
            pf = self.getPrefix(ns + '/')
            return pf, lbl
        else: raise NotImplementedError('Cannot turn straight IRI ({}) into a QName notation (yet, please implement me with rfc3987 pkge).'.format(in_string))
    
    def asQName(self, in_string):
        assert isinstance(in_string, str), "Cannot turn {} into a QName notation".format(type(in_string))
        if self.isQName(in_string):
            return in_string.split(":")
        elif self.isClarks(in_string):
            ns, lbl = in_string[1:].split("}")
            return self.getPrefix(ns), lbl
        elif self.isIRI(in_string):
            ns, lbl = self._splitIRI(in_string)
            return self.getPrefix(ns), lbl
        else: raise RuntimeError('Can only process Clarks, IRI or QName notation, unknown notation ({})'.format(in_string))
        
    def nsConcat(self, ns, name):
        # Just concatenate the value in the nsmap and the name, but consider the use of a separator, and watch the '< >' pair
        hd = '<'
        sep = '/'
        if ns[-1] == '>': ns = ns[:-1]
        if ns[0] == '<': hd = ''
        if ns[-1] in ["/", "#"]: sep = ''
        return hd + sep.join((ns, name)) + '>'

    def asIRI(self, in_string):
        assert isinstance(in_string, str), "Cannot turn {} into an IRI notation".format(type(in_string))
        if self.isIRI(in_string): return in_string
        elif self.isQName(in_string):
            prefix, name = in_string.split(":")
            if prefix == '' or prefix == None:
                return self.nsConcat(self.base, name)
            elif prefix in self.nsmap:
                return self.nsConcat(self.nsmap[prefix], name)
            raise RuntimeError('Cannot turn "{}" into IRI due to missing XMLNS prefix in registered namespaces'.format(in_string))
        elif self.isClarks(in_string): 
            ns, lbl = in_string[1:].split("}")
            exp = self.expand(ns)
            return self.nsConcat(exp, lbl)
        elif self.isIRI('<' + in_string + '>'): return '<' + in_string + '>'
        else: raise RuntimeError('Can only process Clarks, IRI or QName notation, unknown notation ({})'.format(in_string))
    
    def asClarks(self, in_string):
        assert isinstance(in_string, str), "Cannot turn non-string {} into a Clark's IRI notation".format(type(in_string))
        if self.isClarks(in_string): return in_string
        elif self.isQName(in_string):
            prefix, name = in_string.split(":")
            if prefix == '': prefix = None
            if prefix in self.nsmap:
                return str("{" + self.nsmap[prefix] + "}" + name)
            print(str(self.nsmap))
            raise RuntimeError('Cannot turn "{}" into IRI due to missing XMLNS prefix in registered namespaces'.format(in_string))
        elif self.isIRI(in_string):
            ns, lbl = self._splitIRI(in_string)
            ns_exp = self.expand(ns)
            return str("{" + ns_exp + "}" + lbl)
        else: raise RuntimeError('Can only process Clarks, IRI or QName notation, unknown notation ({})'.format(in_string))
    
    def __str__(self):
        result = ''
        for k in self.nsmap:
            result += '{:<10}, {}\n'.format(str(k), str(self.nsmap[k]))
        return result
            
    def __repr__(self):
        result = ''
        for k in self.nsmap:
            result += str(k) + ' : ' + str(self.nsmap[k]) + ' : ' + str(self.nspam[self.nsmap[k]]) + '\n' 

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
            _, tag = name[1:].split("}")
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
