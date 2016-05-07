'''
Created on 17 apr. 2016

@author: brandtp
'''
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree
from utilities.namespaces import NSManager
# from lxml import etree
#TODO: Omzetten naar lxml ipv xml.etree
import warnings
import os.path
 
class ParseAlignment():
    '''
    This class represents an alignment that can be parsed from, in principle, multiple ways of representing alignments. 
    Currently, only EDOAL_prefix representations are supported. At this moment, the alignment is represented as xml.etree.ElementTree
            self.about   ::== string, representing the (unique) name of this alignment
            self._align   ::== xml.etree.ElementTree
            self.nsMgr   ::== utilities.namespaces.NSManager
    '''
    @classmethod
    def canonicalCorrRelation(cls, rel):
        from mediator.mediatorTools import MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI
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
        else: raise RuntimeError('Correspondence relation "{}" not recognised'.format(rel))

    EDOAL_NAMESPACE = 'http://ns.inria.org/edoal/1.0/#'
    EDOAL_prefix = '{%s}' % EDOAL_NAMESPACE
    EDOAL = {
        # Element tag names
        'CLASS'  : EDOAL_prefix + 'Class'.lower(),
            'CAOR' : EDOAL_prefix + 'AttributeOccurenceRestriction'.lower(),
            'CADR' : EDOAL_prefix + 'AttributeDomainRestriction'.lower(),
            'CATR' : EDOAL_prefix + 'AttributeTypeRestriction'.lower(),
            'CAVR' : EDOAL_prefix + 'AttributeValueRestriction'.lower(),
        'RELN'  : EDOAL_prefix + 'Relation'.lower(),
            'RDR'  : EDOAL_prefix + 'RelationDomainRestriction'.lower(),
            'RCDR' : EDOAL_prefix + 'RelationCoDomainRestriction'.lower(),
        'PROP'  : EDOAL_prefix + 'Property'.lower(),
            'PDR'  : EDOAL_prefix + 'PropertyDomainRestriction'.lower(),
            'PTR'  : EDOAL_prefix + 'PropertyTypeRestriction'.lower(),
            'PVR'  : EDOAL_prefix + 'PropertyValueRestriction'.lower(),
        'INST'  : EDOAL_prefix + 'Instance'.lower(),
        'LIT'   : EDOAL_prefix + 'Literal'.lower(),
        'VAL'   : EDOAL_prefix + 'value'.lower(),
        'APPLY' : EDOAL_prefix + 'Apply'.lower(),
        'AGGR'  : EDOAL_prefix + 'Aggregate'.lower(),
        
        # Attribute names
        'DRCTN' : EDOAL_prefix + 'direction'.lower(),
        'OPRTR' : EDOAL_prefix + 'operator'.lower(),
        'ARGS'  : EDOAL_prefix + 'arguments'.lower(),
        'LANG'  : EDOAL_prefix + 'lang'.lower(),
        'STRNG' : EDOAL_prefix + 'string'.lower(),
        'TYPE'  : EDOAL_prefix + 'type'.lower(),
        
        'COLL'  : 'Collection'.lower()
        }

    def __init__(self, fn):
        '''
        Reads and parses the input file that contains the alignment (currently only ' : alignments supported). Returns an object
        with a variety on methods to get the required elements from the alignment. It also carries a namespace manager that is 
        populated with (namespace, prefix) pairs that are addressed within this alignment, some universal namespaces, e.g., RDF, and
        some particular EDOAL_prefix namespaces. 
        '''
        mediatorNSs = { 'med'   : 'http://ts.tno.nl/mediator/1.0/',
                        'medtfn': 'http://ts.tno.nl/mediator/1.0/transformations/',
                        'dc'    : 'http://purl.org/dc/elements/1.1/',
                        'edoal' : ParseAlignment.EDOAL_NAMESPACE,
                        'align' : 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
                        'alext' : 'http://exmo.inrialpes.fr/align/ext/1.0/'
                         }
        self.nsMgr = NSManager(nsDict=mediatorNSs, base='http://knowledgeweb.semanticweb.org/heterogeneity/alignment#')
        self.corrs = []
        #TODO: Support other alignment formats than EDOAL_prefix, e.g., SPIN: check the type of alignment (EDOAL_prefix, SPIN) here
        # Assume EDOAL_prefix for now
        with open(fn, 'r') as f:
            element_tree = ET.parse(f)
 
        root = element_tree.getroot()
        self._parseEDOAL(root)
        

    def _parseEDOAL(self, edoal):
        '''
        The Mediator requires an alignment. To that end it currently parses an EDOAL_prefix alignment.  
        Input: 
        - edoal : ( xml.etree.cElementTree.Element ): an edoal expression 
        '''
        assert (edoal != None) and (isinstance(edoal, ET.Element))

        # Get the Alignment
        self._align = edoal.find(NSManager.CLARKS_LABELS['ALIGNMENT'])
        if self._align == None: 
            raise RuntimeError('Cannot find required {} element in XML-tree'.format(NSManager.CLARKS_LABELS['ALIGNMENT']))
        self.about = ''
        t = self._align.get(NSManager.CLARKS_LABELS['RDFABOUT'], default='')
        if (t == '') or (t == None): 
            raise ValueError('Alignment id as {} attribute is required'.format(NSManager.CLARKS_LABELS['RDFABOUT']))
        else: self.about = t
 
    def getAbout(self):
        return self.about
    
    def getLevel(self):    
        #TODO: Consider other EDOAL_prefix levels than 2EDOAL only
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
        def __init__(self, alignment=None, ns_mgr=None):
            assert isinstance(alignment, ET.Element) 
            assert isinstance(ns_mgr, NSManager), "Cannot parse ontology from Alignment, got {} and {}".format(alignment,ns_mgr)
            o = alignment.find(str(ns_mgr.asClarks('align:Ontology')))
            if (o == None): 
                raise ValueError('Missing required ontology element ({})'.format(str(ns_mgr.asClarks('align:Ontology'))))
            self.name = o.get(NSManager.CLARKS_LABELS['RDFABOUT'], default='')
            if (self.name == '') or (self.name == None): 
                raise ValueError('Ontology id as {} attribute is required'.format(NSManager.CLARKS_LABELS['RDFABOUT']))
            
            l = o.find(str(ns_mgr.asClarks('align:location')))
            if (l == '') or (l == None): self.location = None
            else: self.location = l.text
            
            path = str(ns_mgr.asClarks('align:formalism')) + '/' + str(ns_mgr.asClarks('align:Formalism'))
            f = o.find(path)
            if (f == '') or (f == None): 
                raise ValueError('Ontology id as {} attribute is required'.format(path))
            self.formalism_uri = f.get(str(ns_mgr.asClarks('align:uri')), default='')
            self.formalism_name = f.get(str(ns_mgr.asClarks('align:name')), default='')
            
    def getSrcOnto(self):
        o = self._align.find(str(self.nsMgr.asClarks('align:onto1')))
        if o == None: raise RuntimeError('Edoal element <edoal:onto1> required; none found')
        else: return self.OntoRef(o, self.nsMgr)

    def getTgtOnto(self):
        o = self._align.find(str(self.nsMgr.asClarks('align:onto2')))
        if o == None: raise RuntimeError('Edoal element <edoal:onto2> required; none found')
        else: return self.OntoRef(o, self.nsMgr)         

    def _parseBooleanExpression(self, el=None):
        '''
        Parse a boolean entity construction
        '''
        assert el.tag in ['and', 'or', 'not'], 'Illegal edoal entity construction: boolean combinations require "and", "or", or "not", but "{}" found'.format(el.tag)
        raise NotImplementedError('Boolean edoal entity constructions not supported (yet, please implement me)')
    
    def _parseComposeExpression(self, el=None):
        '''
        Parse a Composed entity construction (<compose rdf:parseType="Collection">)
        '''
        assert el.tag == 'compose', 'Illegal edoal entity construction: compose-expression requires "compose", but "{}" found'.format(el.tag)
        raise NotImplementedError('Composed edoal entity constructions not supported (yet, please implement me)')


    def _parseAttribute(self, asIRI=True, *, element=None, el_attr=None):
        assert element != None and isinstance(element,Element), "Cannot get an attribute from an empty <element>"
        assert el_attr != None and isinstance(el_attr, str) and el_attr != '', "Cannot get an <element>'s attribute without its name"
        attr_value = element.get(el_attr)
        if attr_value == None: return None
        assert attr_value != '', 'An Edoal <{}> element requires a value for its "{}" attribute.'.format(element.tag, el_attr)
        if asIRI:
            return self.nsMgr.asIRI(attr_value)
        else: return attr_value

    def _parseEntity(self, el=None):
        '''
        Parse the EDOAL XML <Entity> element and return the relevant parts. Internal use only! 
        '''
        #TODO: It might be better to return an EntityExpression here
        assert isinstance(el, Element), "Cannot parse edoal entity expression without proper type <Element>, got {}".format(type(el))

        if (el.tag.lower() in [ParseAlignment.EDOAL['CLASS'], ParseAlignment.EDOAL['CAOR'], ParseAlignment.EDOAL['CADR'], ParseAlignment.EDOAL['CATR'], ParseAlignment.EDOAL['CAVR']]):
            # Found a CLASS expression
            return self._parseClass(el)
               
        elif (el.tag.lower() in [ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['PDR'], ParseAlignment.EDOAL['PTR'], ParseAlignment.EDOAL['PVR']]):
            # Found a PROPERTY expression
            return self._parseProperty(el)
        
        elif (el.tag.lower() in [ParseAlignment.EDOAL['RELN'], ParseAlignment.EDOAL['RDR'], ParseAlignment.EDOAL['RCDR']]):
            # Found a RELATION expression
            if (el.get(NSManager.CLARKS_LABELS['RDFABOUT']) == None):
                # Complex Boolean Property Construct found
                raise NotImplementedError('Complex Boolean Edoal Relation constructs not supported (yet, please implement me)')
            else:
                # Simple Class Entity found.
                return self._parseRelation(el.get(NSManager.CLARKS_LABELS['RDFABOUT']))
                    
        elif (el.tag.lower() == ParseAlignment.EDOAL['INST']):
            # Found an INSTANCE expression
            return self._parseInstance(el)
        
        # Checked for all possibilities. If code gets here, an illegal EDOAL construct was detected
        assert False, 'Illegal Edoal construction: found <{}> element within <entity> element, quitting'.format(el.tag)

    def _parseClass(self, cls_el):
        from mediator.mediatorTools import EClass
        
        if cls_el.tag.lower() == ParseAlignment.EDOAL['CLASS']:
            # <Class> element found
            iriref = self._parseAttribute(element=cls_el, el_attr=NSManager.CLARKS_LABELS['RDFABOUT'])
            if iriref == None:
                # Complex Boolean Class Construct found
                return self._parseBooleanExpression(cls_el[0])
            else:
                # Simple Class Entity found.
                assert iriref != '', \
                    'An Edoal Class expression requires a value for its "{}" attribute.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
                return EClass(entity_iri=iriref)
        else:
            assert cls_el.tag.lower() in [ParseAlignment.EDOAL['CAOR'], ParseAlignment.EDOAL['CADR'], ParseAlignment.EDOAL['CATR'], ParseAlignment.EDOAL['CAVR']], \
                'Illegal Edoal construction: found <{}> element as part of <class> expression, quitting'.format(cls_el.tag)
            raise NotImplementedError('Edoal Class Restriction constructs found ({}); not supported (yet, please implement me)'.format(cls_el.tag))

        
    def _parseProperty(self, prop_el):
        from mediator.mediatorTools import EProperty
        if prop_el.tag.lower() == ParseAlignment.EDOAL['PROP']:
            # <Property> element found
            if prop_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != None:
                assert prop_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != '', \
                    'An Edoal Property expression requires a value for its "{}" attribute.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
                # Simple Property Entity found. 
                #TODO: Language attribute in Property Entity currently ignored
                if prop_el.get(ParseAlignment.EDOAL['LANG']) != None: warnings.warn('Not Implemented Yet: <Property> element has got language attribute ({}), ignored'.format(prop_el.get(ParseAlignment.EDOAL['LANG'])))
                return EProperty(prop_el.get(NSManager.CLARKS_LABELS['RDFABOUT']))
            else:
                assert len(prop_el) > 1, 'Illegal Edoal construction: found empty <property> expression without {}, quitting'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
                if prop_el[0].tag in ['and', 'or', 'not']:
                    # Boolean Property expression found
                    return self._parseBooleanExpression(prop_el[0])
                elif prop_el[0].tag == 'compose':
                    # Composite property expression found
                    return self._parseComposeExpression(prop_el[0])
                else: raise RuntimeError('Illegal Edoal construction: found <{}> element as part of <property> expression, quitting'.format(prop_el[0].tag))
        else: 
            assert prop_el.tag.lower() in [ParseAlignment.EDOAL['PDR'], ParseAlignment.EDOAL['PTR'], ParseAlignment.EDOAL['PVR']], \
                'Illegal Edoal construction: found <{}> element as part of <property> expression, quitting'.format(prop_el.tag)
            # Property Restriction entity found
            raise NotImplementedError('Edoal Property Restriction construct ({}) not supported (yet, please implement me)'.format(prop_el.tag))

    
    def _parseRelation(self, reln_el):
        from mediator.mediatorTools import ERelation
        if reln_el.tag.lower() == ParseAlignment.EDOAL['RELN']:
            # <Relation> element found
            if reln_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != None:
                assert reln_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != '', \
                    'An Edoal simple Relation expression requires a value for its "{}" attribute.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
                # Simple Relation Entity found. 
                return ERelation(reln_el.get(NSManager.CLARKS_LABELS['RDFABOUT']))
            else:
                # Boolean Relation expression found
                return self._parseBooleanExpression(reln_el[0])
        else: 
            assert reln_el.tag.lower() in [ParseAlignment.EDOAL['RDR'], ParseAlignment.EDOAL['RCDR']], \
                'Illegal Edoal construction: found <{}> element as part of <relation> expression, quitting'.format(reln_el.tag)
            # Property Restriction entity found
            raise NotImplementedError('Edoal Relation Restriction construct ({}) not supported (yet, please implement me)'.format(reln_el.tag))

        
    def _parseInstance(self, inst_el=None):
        from mediator.mediatorTools import EInstance
        
        assert inst_el != None, 'Cannot create instance from Nothing'
        assert inst_el.tag.lower() == ParseAlignment.EDOAL['INST'], "<Instance> element expected, got <{}>".format(inst_el.tag)
        assert len(inst_el) == 0, 'An Edoal Instance expression cannot have child elements, but found {} children'.format(len(inst_el))
        assert inst_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != None and inst_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != '', \
            'An Edoal Instance expression requires an "{}" attribute and value to specify its individual'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
        return EInstance(inst_el.get(NSManager.CLARKS_LABELS['RDFABOUT']))
    
    def _parseLiteral(self, lit_el=None):
        assert lit_el != None and lit_el.tag.lower() == ParseAlignment.EDOAL['LIT'], '<Literal> element expected, got <{}>, quitting'.format(lit_el)
        value = lit_el.get(ParseAlignment.EDOAL['STRNG'])
        assert value, 'A <Literal> element requires an "edoal:string" attribute, but got <{}>'.format(lit_el)
        v_type = lit_el.get(ParseAlignment.EDOAL['TYPE'])
        if v_type == None: value_type = str(ParseAlignment.EDOAL['string'])
        else: value_type = v_type
        return value, value_type

    def _parseOperation(self, operation_el=None):
        '''
        Parse the <edoal:Apply> or the <edoal:Aggregate> elements that specify the operation(s) that are implied by this transformation; 
        Store the results as an mediatorTools.Transformation object
        '''
        from mediator.mediatorTools import Transformation
        
        assert isinstance(operation_el, ET) and (operation_el.tag.lower() == ParseAlignment.EDOAL['APPLY'] or operation_el.tag.lower() == ParseAlignment.EDOAL['AGGR']), \
            "<Apply> or <Aggregate> element expected, got <{}>, quitting".format(operation_el)
        operator = operation_el.get(ParseAlignment.EDOAL['OPRTR'])
        assert operator, "an <Apply> or <Aggregate> element requires an 'edoal:operator' attribute, but got '{}'".format(operator)
        if not self.nsMgr.isClarks(operator): raise AttributeError("Expected iri value for attribute edoal:operator, got {}".format(operator))
        # Get the operator
        pf, pf_expanded, functionName = self.nsMgr.split(operator)
        # Turn the operator into a callable function
        if pf == 'op:' or pf_expanded in ['http://www.w3.org/2005/xpath-functions', 'http://www.w3.org/2001/XMLSchema']:
            # XPath function found
            raise NotImplementedError("XPath functions ({}) not supported (yet, please implement me).".format(operator))
        elif pf == 'http:':
            # Webservice found
            raise NotImplementedError("Webservice functions ({}) not supported (yet, please implement me).".format(operator))
        elif pf == 'java:':
            # Java method found
            raise NotImplementedError("Java method functions ({}) not supported (yet, please implement me).".format(operator))
        elif pf_expanded == self.nsMgr.expand('medtfn'):
            # Python method in own library found, check if it exists
            fpath, fname = functionName.split('/')
            assert os.path.isfile('../transformations/' + fpath + 'py'), "Cannot find transformationn lib {}".format('../transformations/' + fpath + 'py')
            assert fname in dir(fpath), "Cannot find operation {} in transformation lib {}".format(fname, fpath)
            # Create a Transformation
            transformation = Transformation(python_module=fpath, method_name=fname)
        else: raise AttributeError("Don't recognise the transformation operator '{}'".format(operator))
            
        # Get the operands; note that 'operands' mean: ways to achieve the value(s)
        operands = []
        args = operation_el.find(ParseAlignment.EDOAL['ARGS'])
        assert args != None, "Element <{}> requires subelement <{}:{}> but none found.".format(operation_el.tag, self.nsMgr.asQName(ParseAlignment.EDOAL['ARGS']))
        if args.get(NSManager.CLARKS_LABELS['RDFPARSTP']) == ParseAlignment.EDOAL['COLL']:
            for value_el in args.iter():
                if value_el.tag in [ParseAlignment.EDOAL['APPLY'], ParseAlignment.EDOAL['AGGR']]:
                    # Found another operation; resolve this by going recursive on this very same method, i.e., _parseOperation
                    #TODO: handle recursive operation definitions, i.e, operations that have operations as arguments
                    raise NotImplementedError("Cannot handle paths, i.e., recursive definitions for operations, (yet, please implement me), found {}".format(str(value_el)))
                else:
                    operands.append(self.Value(value_el))
        else: raise RuntimeError("<{}> expected as attribute to <{}> element".format(ParseAlignment.EDOAL['COLL'], args.tag))
        # Store the operands together with the operation
        transformation.registerOperands(operands)
        return transformation

    class Value():
        '''
        An EDOAL_prefix value expression, representing: 
        (1) a literal value
        (2) an individual (instance)
        (3) an attribute expression, i.e, a value that can be reached through application of a Property or Relation
        (4) a value computable by a function from arguments; the arguments are again values 
        '''
        
        def __init__(self, el=None):
            from mediator.mediatorTools import Transformation
            '''
            Input: an <entity> element, type xml.etree.ElementTree.Element, that contains a <value> element 
            '''
            assert isinstance(el, Element), "Cannot parse non xml.tree elements, got [{}] of type [{}]".format(el, type(el))
            assert len(list(el)) > 0, "Found empty element, cannot proceed"
            assert el[0].tag.lower() in [ParseAlignment.EDOAL['LIT'], ParseAlignment.EDOAL['APPLY'], ParseAlignment.EDOAL['AGGR'], ParseAlignment.EDOAL['INST'], ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['RELN']], "Unexpected element: <{}>".format(el[0].tag)
            
            # Do all verification on lowercase strings
            self._entity_type = el[0].tag.lower()
            
            if (self._entity_type == ParseAlignment.EDOAL['LIT']):
                self.value, self.value_type = ParseAlignment._parseLiteral(self, lit_el=el[0])
            
            elif (self._entity_type == ParseAlignment.EDOAL['INST']):
                self.iriref = ParseAlignment._parseInstance(self, inst_el=el[0]).getIriRef()
                
            elif (self._entity_type == ParseAlignment.EDOAL['PROP']):
                self.iriref = ParseAlignment._parseProperty(el[0]).getIriRef()
                
            elif (self._entity_type == ParseAlignment.EDOAL['RELN']):
                self.iriref = ParseAlignment._parseRelation(el[0]).getIriRef()
                
            elif self._entity_type == ParseAlignment.EDOAL['APPLY'] or self._entity_type == ParseAlignment.EDOAL['AGGR']:
                self.operator = ParseAlignment._parseOperation(el[0])
                
            else: raise RuntimeError('Assumed dead code: analyse why I am here, got {}'.format(self._entity_type))

        def getEntityType(self):
            return self._entity_type
        
        def isLiteral(self):
            return self._entity_type == ParseAlignment.EDOAL['LIT']
        def isIndividual(self):
            return self._entity_type == ParseAlignment.EDOAL['INST']
        def isAttrExpression(self):
            return self._entity_type == ParseAlignment.EDOAL['PROP'] or self._entity_type == ParseAlignment.EDOAL['RELN'] 
        def isComputable(self):
            return self._entity_type == ParseAlignment.EDOAL['APPLY'] or self._entity_type == ParseAlignment.EDOAL['AGGR']
        
        def getLiteral(self):
            if self._entity_type == ParseAlignment.EDOAL['LIT']: 
                return self.value, self.value_type
            else: return None
        
        def getIndividual(self):
            if self._entity_type == ParseAlignment.EDOAL['INST']: 
                return self.getIriRef()
            else: return None
            
        def getAttrExpression(self):
            if self._entity_type in [ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['RELN']]: 
                return self.getIriRef()
            else: return None
        
        def getIriRef(self):
            if self._entity_type in [ParseAlignment.EDOAL['INST'], ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['RELN']]:
                return self.iriref
            else: return None

        def getOperator(self):
            if self._entity_type in [ParseAlignment.EDOAL['APPLY'], ParseAlignment.EDOAL['AGGR']]: 
                return self.operator
            else: return None

    def _parseTransform(self, el):
        '''
        Build an executable mediatorTools.Transformation from the <edoal:Transformation> element.
        '''
        Tfs = el.findall(str(self.nsMgr.asClarks('edoal:Transformation')))
        if len(Tfs) > 1: raise RuntimeWarning('One <edoal:Transformation> elements expected inside <edoal:transformation> element, found {} in stead. Only last one will remain!'.format(len(Tfs)))
        for Transformation in Tfs:
            direction = Transformation.get(ParseAlignment.EDOAL['DRCTN'])
            if (direction == None) or not direction in ["o-", "-o"]:
                raise RuntimeError('Cannot parse a transformation without directional attribute, <Transformation edoal:direction=" STRING ">')
            # Parse the <edoal:entity1> and <edoal:entity2> elements that define the data transformation
            val1 = self.Value(Transformation.find(str(self.nsMgr.asClarks('edoal:entity1'))), self.nsMgr)
            val2 = self.Value(Transformation.find(str(self.nsMgr.asClarks('edoal:entity2'))), self.nsMgr)
            # Build from the parsed entities a valid and executable transformation, consisting of a source operation (incl. its operands) and the target result entity
            if direction == 'o-':
                # This indicates that operation and its operands should be found in entity1
                if val1.getEntityType() in [ParseAlignment.EDOAL['APPLY'], ParseAlignment.EDOAL['AGGR']]:
                    operation = val1.getOperator()
                    if val2.getEntityType() in [ParseAlignment.EDOAL['INST'], ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['RELN']]:
                        result = val2.getIriRef()
                    else: raise RuntimeError("Result of transformation cannot be another transformation or literal, got <{}>".format(val2.getEntityType()))
                else: raise RuntimeError("Direction attribute ({}) specifies operation on <entity1>, but no operation was found".format(direction))
            else: 
                # This indicates that operation and operands should be found in entity2
                if val2.getEntityType() in [ParseAlignment.EDOAL['APPLY'], ParseAlignment.EDOAL['AGGR']]:
                    operation = val2.getOperator()
                    if val1.getEntityType() in [ParseAlignment.EDOAL['INST'], ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['RELN']]:
                        result = val1.getIriRef()
                    else: raise RuntimeError("Result of transformation cannot be another transformation or literal, got <{}>".format(val1.getEntityType()))
                else: raise RuntimeError("Direction attribute ({}) specifies operation on <entity2>, but no operation was found".format(direction))

        return operation, result
    
    
    def getCorrespondence(self, cell=None):
        from mediator.mediatorTools import Correspondence
        assert isinstance(cell, Element), "Expected xml.tree element, got type <{}>".format(type(cell))
        # Get the name, i.e., about attribute of <align:Cell rdf:about=[name]> element
        corr = Correspondence(nsMgr=self.nsMgr)
        if cell.get(NSManager.CLARKS_LABELS['RDFABOUT']) != None:
            assert cell.get(NSManager.CLARKS_LABELS['RDFABOUT']) != '', \
                'An "{}" attribute requires a value, found empty string.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
            # About attribute for <Cell> element is optional
            corr.setName(name=cell.get(NSManager.CLARKS_LABELS['RDFABOUT']))
        
        # Get the Translation part, i.e., the obligatory parts <entity1 & 2>, <measure> and <relation>
        # Get the source entity expression, i.e., the <align:entity1> element; validate that exactly 1 single <entity1> element is found
        srcs = cell.findall(str(self.nsMgr.asClarks(':entity1')))
        assert len(srcs) == 1, 'Exactly 1 edoal entity expression <{}> required, found {}'.format(str(self.nsMgr.asClarks(':entity1')), len(srcs))
        src = srcs[0]
        assert src != None, 'Edoal entity expression element <{}> required'.format(str(self.nsMgr.asClarks(':entity1')))
        assert len(src) > 0, 'Empty edoal entity expression element <{}> found. Entity expression required'.format(str(self.nsMgr.asClarks(':entity1')))
        entityExpr = self._parseEntity(el=src[0])
        corr.setEE1(entity_expr=entityExpr)
        
        # Get the target entity expression, i.e., the <align:entity2> element; validate that exactly 1 single <entity2> element is found
        tgts = cell.findall(str(self.nsMgr.asClarks(':entity2')))
        assert len(tgts) == 1, 'Exactly 1 edoal entity expression <{}> required, found {}'.format(str(self.nsMgr.asClarks(':entity2')), len(tgts))
        tgt = tgts[0]
        assert tgt != None, 'Edoal entity expression required as <{}> element'.format(str(self.nsMgr.asClarks(':entity2')))
        assert len(tgt) > 0, 'Empty edoal entity expression found ({}). Entity expression required'.format(str(self.nsMgr.asClarks(':entity2')))
        entityExpr = self._parseEntity(el=tgt[0])
        corr.setEE2(entity_expr=entityExpr)
        
        # Get the relation that holds between both entity expressions, i.e., <align:relation>
        rels = cell.findall(str(self.nsMgr.asClarks(':relation')))
        if rels == None or rels == []: raise RuntimeError('Exactly one Edoal element <relation> required, but zero found in "{}"'.format(corr.getName()))
        elif len(rels) > 1: raise RuntimeError('Exactly one Edoal element <relation> required, but found {} in "{}"'.format(len(rels),corr.getName()))
        corr.setCorrRelation(relation=self.canonicalCorrRelation(rels[0].text))
        
        # Get the measure with which the relation is estimated to hold between both entity expressions.
        msrs = cell.findall(str(self.nsMgr.asClarks(':measure')))
        if msrs == None or msrs == []: raise RuntimeError('Exactly one Edoal element <measure> required, but zero found in "{}"'.format(corr.getName()))
        elif len(msrs) > 1: raise RuntimeError('Exactly one Edoal element <measure> required, but found {} in "{}"'.format(len(msrs),corr.getName()))
        elif msrs[0].get(NSManager.CLARKS_LABELS['RDFDATATP']) == None: raise RuntimeError('Cannot determine the type of the measure value: missing rdf.datatype attribute to <measure> element in {}'.format(corr.getName()))
        corr.setCorrMeasure(measure=msrs[0].text, measure_type=msrs[0].get(NSManager.CLARKS_LABELS['RDFDATATP']))
        
        # Get the optional Transformation parts, i.e., the <edoal:transformation> element; zero, one or more are acceptable
        tfs = cell.findall(str(self.nsMgr.asClarks('edoal:transformation')))
        for tf in tfs:
            corr.appendTransform(self._parseTransform(tf))
        
        return corr

    def appendCorrespondence(self, corr):
        from mediator.mediatorTools import Correspondence            
        assert isinstance(corr, Correspondence), "Expected a Correspondence to add, got {}".format(type(corr))
        #TODO: Prevent to add double correspondences
        self._corrs.append(corr)
        
    def getCorrespondences(self): 
        '''
        Extract from the EDOAL_prefix XML file all <map><Cell> ... </Cell></map> parts
        and populate a newly made Mediator.Correspondence class with the relevant information
        '''
        
        cells = self._align.findall(self.nsMgr.asClarks('align:map') + '/' + self.nsMgr.asClarks('align:Cell'))
        if len(cells) == 0:
            raise RuntimeError('An Edoal alignment requires at least one {} element, but zero found'.format(self.nsMgr.asClarks('align:map') + '/' + self.nsMgr.asClarks('align:Cell')))
        
        # Iterate over all <Cell>...</Cell> parts
        self._corrs = []
        for cell in cells:
            corr = self.getCorrespondence(cell)
            #TODO: Maak van Corrs geen Dict maar een lijst
            self.appendCorrespondence(corr)
        return self._corrs

    
if __name__ == '__main__':
    print('running main')

