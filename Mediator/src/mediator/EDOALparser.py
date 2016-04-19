'''
Created on 17 apr. 2016

@author: brandtp
'''
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element
from utilities.namespaces import NSManager
from mediator.mediatorTools import Correspondence, MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI
from rdflib.term import URIRef
 
class ParseAlignment():
    '''
    This class represents an alignment that can be parsed from, in principle, multiple ways of representing alignments. 
    Currently, only EDOAL representations are supported. At this moment, the alignment is represented as xml.etree.ElementTree
            self.about   ::== string, representing the (unique) name of this alignment
            self._align   ::== xml.etree.ElementTree
            self.nsMgr   ::== utilities.namespaces.NSManager
    '''
    @classmethod
    def canonicalCorrRelation(cls, rel):
        if rel.lower() in ['=', 'equivalence', 'eq']:
            return MEDRELEQ 
        elif rel.lower() in ['<', '<=', 'subsumption', 'lt', 'lower-than', 'le']:
            return MEDRELSUB 
        elif rel.lower() in ['>', '>=', 'subsumed', 'subsumedby', 'gt', 'greater-than', 'ge']:
            return MEDRELSUP
        elif rel.lower() in ['e', 'in', 'element_of', 'eo']:
            return MEDRELIN
        elif rel.lower() in ['3', 'ni', 'encompass', 'encompasses']:
            return MEDRELNI
        else: raise NotImplementedError('Correspondence relation {} not recognised'.format(rel))

    EDOALCLASS = '{http://ns.inria.org/edoal/1.0/#}Class'
    EDOALRELN = '{http://ns.inria.org/edoal/1.0/#}Relation'
    EDOALPROP = '{http://ns.inria.org/edoal/1.0/#}Property'
    EDOALINST = '{http://ns.inria.org/edoal/1.0/#}Instance'
    EDOALCAOR = '{http://ns.inria.org/edoal/1.0/#}AttributeOccurenceRestriction'
    EDOALCADR = '{http://ns.inria.org/edoal/1.0/#}AttributeDomainRestriction'
    EDOALCATR = '{http://ns.inria.org/edoal/1.0/#}AttributeTypeRestriction'
    EDOALCAVR = '{http://ns.inria.org/edoal/1.0/#}AttributeValueRestriction'
    
    EDOALDRCTN = '{http://ns.inria.org/edoal/1.0/#}direction'
    EDOALLIT   = '{http://ns.inria.org/edoal/1.0/#}Literal'
    EDOALAPPLY = '{http://ns.inria.org/edoal/1.0/#}Apply'
    EDOALOPRTR = '{http://ns.inria.org/edoal/1.0/#}operator' 
    EDOALAGGR  = '{http://ns.inria.org/edoal/1.0/#}Aggregate' 
    EDOALARGS  = '{http://ns.inria.org/edoal/1.0/#}arguments' 
    
    EDOALCOLL  = 'Collection' 


    def __init__(self, fn):
        '''
        Reads and parses the input file that contains the alignment (currently only EDOAL alignments supported). Returns an object
        with a variety on methods to get the required elements from the alignment. It also carries a namespace manager that is 
        populated with (namespace, prefix) pairs that are addressed within this alignment, some universal namespaces, e.g., RDF, and
        some particular EDOAL namespaces. 
        '''
        mediatorNSs = { 'med'   : 'http://ds.tno.nl/mediator/1.0/',
                        'dc'    : 'http://purl.org/dc/elements/1.1/',
                        'edoal' : 'http://ns.inria.org/edoal/1.0/#',
                        'align' : 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
                        'alext' : 'http://exmo.inrialpes.fr/align/ext/1.0/'
                         }
        self.nsMgr = NSManager(nsDict=mediatorNSs, base='http://knowledgeweb.semanticweb.org/heterogeneity/alignment#')
        
        #TODO: Support other alignment formats than EDOAL, e.g., SPIN: check the type of alignment (EDOAL, SPIN) here
        # Assume EDOAL for now
        with open(fn, 'r') as f:
            element_tree = ET.parse(f)
 
        root = element_tree.getroot()
        self._parseEDOAL(root)
        

    def _parseEDOAL(self, edoal):
        '''
        The Mediator requires an alignment. To that end it currently parses an EDOAL alignment.  
        Input: 
        - edoal : ( xml.etree.cElementTree.Element ): an edoal expression 
        '''
        assert (edoal != None) and (isinstance(edoal, ET.Element))

        # Get the Alignment
        self._align = edoal.find(NSManager.ALIGNMENT)
        if self._align == None: 
            raise RuntimeError('Cannot find required {} element in XML-tree'.format(NSManager.ALIGNMENT))
        self.about = ''
        t = self._align.get(NSManager.RDFABOUT, default='')
        if (t == '') or (t == None): 
            raise ValueError('Alignment id as {} attribute is required'.format(NSManager.RDFABOUT))
        else: self.about = t
 
    def getAbout(self):
        return self.about
    
    def getLevel(self):    
        #TODO: Consider other EDOAL levels than 2EDOAL only
        t = self._align.find(str(self.nsMgr.asClarks('align:level')))
        if t == None: raise RuntimeError('No alignment <level> element found in Alignment {}'.format(self.about))
        if not t.text in ['2EDOAL']: 
            raise NotImplementedError('Alignment level other than "2EDOAL" not supported; found {}'.format(t.text))
        return t.text
         
    def getCreator(self):       
        c = self._align.find(str(self.nsMgr.asClarks('dc:creator')))
        if c == None: raise RuntimeError('No <creator> element found in Alignment {}'.format(self.about))
        else: return c.text
        
    def getDate(self):    
        # Date is not a required field   
        d = self._align.find(str(self.nsMgr.asClarks('dc:date')))
        if d != None: return d.text
        else: return ''

    def getMethod(self):    
        # Method is not a required field
        m = self._align.find(str(self.nsMgr.asClarks('alext:method')))
        if m != None: return m.text
        else: return ''
    
    def getPurpose(self):
        # Purpose is not a required field
        p = self._align.find(str(self.nsMgr.asClarks('alext:purpose')))
        if p != None: return p.text
        else: return ''
    
    def getType(self):
        t = self._align.find(str(self.nsMgr.asClarks('align:type')))
        if t == None: raise RuntimeError('Edoal element <edoal:type> required; none found')
        if not t.text in ['**', '?*', '*?', '??']:
            raise ValueError('Incorrect value of element <:type> required, Expected {}, found {}'.format('**, ?*, *?, ??', t.text))
        else: return t.text
    
    class OntoRef():
        '''
        This class implements only a reference to an ontology, not the actual ontology itself.
        '''
        def __init__(self, et):
            o = et._align.find(str(self.nsMgr.asClarks('align:Ontology')))
            if (o == None): 
                raise ValueError('Missing required ontology element ({})'.format(str(self.nsMgr.asClarks('align:Ontology'))))
            self.name = o.get(NSManager.RDFABOUT, default='')
            if (self.name == '') or (self.name == None): 
                raise ValueError('Ontology id as {} attribute is required'.format(NSManager.RDFABOUT))
            
            f = o.find(str(self.nsMgr.asClarks('align:formalism/align:Formalism')))
            if (f == '') or (f == None): 
                raise ValueError('Ontology id as {} attribute is required'.format(str(self.nsMgr.asClarks('align:formalism/align:Formalism'))))
            self.formalism_uri = f.get(str(self.nsMgr.asClarks('align:uri')), default='')
            self.formalism_name = f.get(str(self.nsMgr.asClarks('align:name')), default='')
            
    def getSrcOnto(self):
        o = self._align.find(str(self.nsMgr.asClarks('align:onto1')))
        if o == None: raise RuntimeError('Edoal element <edoal:onto1> required; none found')
        else: return self.ontoRef(o)

    def getTgtOnto(self):
        o = self._align.find(str(self.nsMgr.asClarks('align:onto2')))
        if o == None: raise RuntimeError('Edoal element <edoal:onto2> required; none found')
        else: return self.ontoRef(o)         
    
    def _parseProperty(self, prop):
        assert prop.tag.lower() == self.EDOALPROP, "<Property> element expected, got <{}>".format(prop.tag)
        if (prop.get(NSManager.RDFABOUT) == None):
            # Complex Boolean Property Construct found
            raise NotImplementedError('Complex Boolean Edoal Property constructs not supported (yet, please implement me)')
        else:
            # Simple Class Entity found.
            return URIRef(prop.get(NSManager.RDFABOUT))
    
    def _parseRelation(self, reln):
        assert reln.tag.lower() == self.EDOALRELN, "<Relation> element expected, got <{}>".format(reln.tag)
        if (reln.get(NSManager.RDFABOUT) == None):
            # Complex Boolean Property Construct found
            raise NotImplementedError('Complex Boolean Edoal Relation constructs not supported (yet, please implement me)')
        else:
            # Simple Class Entity found.
            return URIRef(reln.get(NSManager.RDFABOUT))
        
    def _parseInstance(self, inst):
        assert inst.tag.lower() == self.EDOALINST, "<Instance> element expected, got <{}>".format(inst.tag)
        if (inst.get(NSManager.RDFABOUT) == None):
            # Complex Boolean Property Construct found
            raise RuntimeError('An Edoal Instance expression requires an <{}> attribute'.format(NSManager.RDFABOUT))
        else: return URIRef(inst.get(NSManager.RDFABOUT))
            
    def _parseEntity(self, el):
        '''
        Parse the EDOAL XML <Entity> element and return the relevant parts. Internal use only! 
        '''
        #TODO: It might be better to return an EntityExpression here
        if (el[0].tag.lower() == self.EDOALCLASS):
            # Found a CLASS expression
            if (len(list(el.iter())) > 1):
                assert el[0].tag.lower() in [self.EDOALCAOR, self.EDOALCADR, self.EDOALCATR, self.EDOALCAVR], 'Edoal Class restriction construct expected, but got {}'.format(el[0].tag)
            elif (el[0].get(NSManager.RDFABOUT) == None):
                # Complex Boolean Class Construct found
                raise NotImplementedError('Complex Boolean Edoal Class constructs not supported (yet, please implement me)')
            else:
                # Simple Class Entity found.
                return URIRef(el[0].get(NSManager.RDFABOUT)), self.EDOALCLASS
            
        elif (el[0].tag.lower() == self.EDOALPROP):
            # Found a PROPERTY expression
            p_iri = self._parseProperty(el[0])
            return p_iri, self.EDOALPROP
        
        elif (el[0].tag.lower() == self.EDOALRELN):
            # Found a RELATION expression
            if (el[0].get(NSManager.RDFABOUT) == None):
                # Complex Boolean Property Construct found
                raise NotImplementedError('Complex Boolean Edoal Relation constructs not supported (yet, please implement me)')
            else:
                # Simple Class Entity found.
                return URIRef(el[0].get(NSManager.RDFABOUT)), self.EDOALRELN
                    
        elif (el[0].tag.lower() == self.EDOALINST):
            # Found an INSTANCE expression
            return self._parseInstance(el[0])
        
        else: raise NotImplementedError('Restriction expression found, {}, but not supported (yet, please implement me)'.format(el[0].tag))

    class Value():
        '''
        An EDOAL value expression, representing: 
        (1) a literal value
        (2) an individual (instance)
        (3) a value that can be reached through application of a Property or Relation
        (4) a value computable by a function from arguments; the arguments are again values 
        '''
        def __init__(self, el):
            assert isinstance(el, Element), "Cannot parse non xml.tree elements, got [{}] of type [{}]".format(el, type(el))
            assert el[0].tag in [self.EDOALLIT, self.EDOALAPPLY, self.EDOALAGGR, self.EDOALINST, self.EDOALPROP, self.EDOALRELN], "Unexpected element: <{}>".format(el[0].tag)
            self.entity_type = el[0].tag
            
            if (self.entity_type == self.EDOALLIT):
                self.value = el[0].get(str(self.nsMgr.asClarks(('edoal:string'))))
                v_type = el[0].get(str(self.nsMgr.asClarks(('edoal:type'))))
                if v_type == None: self.value_type = str(self.nsMgr.asClarks(('xsd:string')))
                else: self.value_type = v_type
            
            if (self.entity_type == self.EDOALINST):
                self.iriref = self._parseInstance(el[0])
                
            if (self.entity_type == self.EDOALPROP):
                self.iriref = self._parseProperty(el[0])
                
            if (self.entity_type == self.EDOALRELN):
                self.iriref = self._parseRelation(el[0])
                
            if self.entity_type == self.EDOALAPPLY or self.entity_type == self.EDOALAGGR:
                self.operator = el[0].get(self.EDOALOPRTR)
                self.operands = []
                a = el[0].find(self.EDOALARGS)
                if a == None: raise RuntimeError("Element <{}> requires subelement <{}:{}> but none found.".format(self.entity_type, self.nsMgr.asQName(self.EDOALARGS)))
                if a.get(NSManager.RDFPARSTP) == self.EDOALCOLL:
                    for value_el in a.iter():
                        if value_el.tag in [self.EDOALAPPLY, self.EDOALAGGR]:
                            raise NotImplementedError("cannot handle recursive definitions for operations (yet, please implement me), found {}".format(str(value_el)))
                        else:
                            value = self.Value(value_el)
                            if value.entity_type == self.EDOALLIT:
                                self.operands.append(value.value)
                            elif value.entity_type in [self.EDOALINST, self.EDOALPROP, self.EDOALRELN]:
                                self.operands.append(value.iriref)
                            else: raise RuntimeError("This should be dead code, apparently it isn't, got {}".format(value.entity_type))
                else: raise RuntimeError("<{}> expected as attribute to <{}> element".format(self.EDOALCOLL, ))

        
    def _parseTransform(self, el):
        condition = lambda x: True
        result = ''
        operands = []
        operation = lambda x: x * 9 / 5 + 32
        
        Tfs = el.findall(str(self.nsMgr.asClarks('edoal:Transformation')))
        if len(Tfs) > 1: raise RuntimeWarning('One <edoal:Transformation> elements expected, found {} in stead. Only last one will remain active!'.format(len(Tfs)))
        for Tf in Tfs:
            direction = Tf.get(self.EDOALDRCTN)
            if (direction == None) or not direction in ["o-", "-o"]:
                raise RuntimeError('Cannot parse a transformation without directional attribute, <Transformation edoal:direction=" STRING ">')
            val1 = self.Value(Tf.find(str(self.nsMgr.asClarks('edoal:entity1'))))
            val2 = self.Value(Tf.find(str(self.nsMgr.asClarks('edoal:entity2'))))
            if direction == 'o-':
                # This indicates that operation and operands should be found in entity1
                if val1.entity_type in [self.EDOALAPPLY, self.EDOALAGGR]:
                    operation = val1.operator
                    operands = val1.operands
                    if val2.entity_type in [self.EDOALINST, self.EDOALPROP, self.EDOALRELN]:
                        result = val2.iriref
                    else: raise RuntimeError("Result of transformation cannot be another transformation or literal, got <{}>".format(val2.entity_type))
                else: raise RuntimeError("Direction attribute ({}) specifies operation on <entity1>, but no operation was found".format(direction))
            else: 
                # This indicates that operation and operands should be found in entity2
                if val2.entity_type in [self.EDOALAPPLY, self.EDOALAGGR]:
                    operation = val2.operator
                    operands = val2.operands
                    if val1.entity_type in [self.EDOALINST, self.EDOALPROP, self.EDOALRELN]:
                        result = val1.iriref
                    else: raise RuntimeError("Result of transformation cannot be another transformation or literal, got <{}>".format(val1.entity_type))
                else: raise RuntimeError("Direction attribute ({}) specifies operation on <entity2>, but no operation was found".format(direction))

        return condition, operands, operation, result
    
    def getCorrespondences(self): 
        '''
        Extract from the EDOAL XML file all <map><Cell> ... </Cell></map> parts
        and populate a newly made Mediator.Correspondence class with the relevant information
        '''
        cells = self._align.findall(self.nsMgr.asClarks('align:map') + '/' + self.nsMgr.asClarks('align:Cell'))
        if len(cells) == 0:
            raise RuntimeError('An Edoal alignment requires at least one {} element, but zero found'.format(self.nsMgr.asClarks('align:map') + '/' + self.nsMgr.asClarks('_align:Cell')))
        
        # Iterate over all <Cell>...</Cell> parts
        corrs = {}
        for cell in cells:
            
            corr = Correspondence(nsMgr=self.nsMgr)
            if (cell.get(NSManager.RDFABOUT) == None):
                # Complex Boolean Property Construct found
                raise NotImplementedError('An Edoal Instance expression requires an <{}> attribute'.format(NSManager.RDFABOUT))
            else:
                corr.setName(cell.get(NSManager.RDFABOUT))
            
            src = self._align.find(str(self.nsMgr.asClarks(':entity1')))
            #TODO: Validate that exactly 1 single <entity1> element can be found
            if src == None: raise RuntimeError('Edoal element <{}> required'.format(str(self.nsMgr.asClarks(':entity1'))))
            elif not (src[0].tag.lower() in [self.EDOALCLASS, self.EDOALPROP, self.EDOALRELN, self.EDOALINST]):
                raise NotImplementedError('Only edoal EntityExpression type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(src[0]))
            eIri, eType = self._parseEntity(src)
            corr.setSrcEE(src_entity=eIri, entity_type=self.xrefE2M[eType])
            
            tgt = self._align.find(str(self.nsMgr.asClarks(':entity2')))
            #TODO: Validate that exactly 1 single <entity2> element can be found
            if tgt == None: raise RuntimeError('Edoal element <{}> required'.format(str(self.nsMgr.asClarks(':entity2'))))
            elif not (tgt[0].tag.lower() in [self.EDOALCLASS, self.EDOALPROP, self.EDOALRELN, self.EDOALINST]):
                raise NotImplementedError('Only edoal EntityExpression type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(tgt[0]))
            eIri, eType = self._parseEntity(tgt)
            corr.setTgtEE(tgt_entity=eIri, entity_type=eType)
            
            rel = self._align.findall(str(self.nsMgr.asClarks('relation')))
            if rel == None or len(rel) > 1: raise RuntimeError('Exactly one Edoal element <relation> required, found {}'.format(len(rel)))
            corr.setCorrRelation(self.canonicalCorrRelation(rel))
            
            tfs = self._align.findall(str(self.nsMgr.asClarks('edoal:transformation')))
            for tf in tfs:
                corr.appendTransform(self._parseTransform(tf))
            
            corrs[corr.getName()] = corr
        return corrs

    
if __name__ == '__main__':
    print('running main')

