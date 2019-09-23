'''
Created on 17 apr. 2016

@author: brandtp
'''
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, ElementTree
from utilities.namespaces import NSManager
# from lxml import etree
# TODO: Omzetten naar lxml ipv xml.etree
import warnings
import os.path


class Alignment():
 
    '''
    This class represents an alignment that can be parsed from, in principle, multiple ways of representing alignments. 
    Currently, only EDOAL representations are supported. At this moment, the alignment is represented as xml.etree.ElementTree
            self.about   ::== string, representing the (unique) name of this alignment
            self._align   ::== xml.etree.ElementTree
            self.nsMgr   ::== utilities.namespaces.NSManager
    '''

    @classmethod
    def canonicalCorrRelation(cls, rel):
        from edoalparser.parserTools import MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI
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
        'CMPS'  : EDOAL_prefix + 'compose',
        
        # Attribute names
        'DRCTN' : EDOAL_prefix + 'direction'.lower(),
        'OPRTR' : EDOAL_prefix + 'operator'.lower(),
        'ARGS'  : EDOAL_prefix + 'arguments'.lower(),
        'LANG'  : EDOAL_prefix + 'lang'.lower(),
        'STRNG' : EDOAL_prefix + 'string'.lower(),
        'TYPE'  : EDOAL_prefix + 'type'.lower(),
        
        'COLL'  : 'Collection'.lower()
        }

    def __init__(self, fn='', nsMgr=None):
        '''
        Reads and parses the input file (argument 'fn') that contains the alignment (currently only 'EDOAL' alignments supported). Returns an object
        with a variety on methods to get the required elements from the alignment. It also carries a namespace manager that is 
        populated with (namespace, prefix) pairs that are addressed within this alignment, some universal namespaces, e.g., RDF, and
        some particular EDOAL namespaces. 
        '''
        assert isinstance(nsMgr, NSManager), "Proper namespace manager required for parsing an Alignment, got '{}'".format(nsMgr)
        self.nsMgr = nsMgr
        self.corrs = []
        self._addAlignment(fn, nsMgr)
        
    def _addAlignment(self, fn='', nsMgr=None):
        assert isinstance(nsMgr, NSManager), "Alignment._addAlignment(): Proper namespace manager required for parsing an Alignment, got '{}'".format(nsMgr)
        assert fn != '', "Alignment._addAlignment(): Didn't get a file name for the alignment"
        assert self.getAbout() == None, "Alignment._addAlignment(): cannot parse an alignment into existing object '{}'".format(self.getAbout())
        
        assert os.path.exists(fn), "Alignment._addAlignment():  Cannot parse alignment from non-existing file, got {}".format(fn)
        with open(fn, 'r') as f:
            element_tree = ET.parse(f)
        root = element_tree.getroot()
        # TODO: Support other alignment formats than EDOAL, e.g., SPIN: check the type of alignment (EDOAL, SPIN) here
        # Assume EDOAL for now
        self._parseEDOAL(root)

    def _parseEDOAL(self, edoal):
        '''
        The Mediator requires an alignment. To that end it currently parses an EDOAL alignment.  
        Input: 
        - edoal : ( xml.etree.cElementTree.Element ): an edoal expression 
        Result:
         - self._align (xml.etree.cElementTree.Element): the <Alignment> node
         - self.about (string): the name of the alignment as rdf:about attribute in the <Alignment> node
        '''
        assert (edoal != None) and (isinstance(edoal, ET.Element))

        # Get the Alignment
        self._align = edoal.find(NSManager.CLARKS_LABELS['ALIGNMENT'])
        if self._align == None: 
            raise RuntimeError('Alignment._parseEDOAL(): Cannot find required {} element in XML-tree'.format(NSManager.CLARKS_LABELS['ALIGNMENT']))
        assert self.getAbout() == None, "Alignment._parseEDOAL(): cannot parse an alignment into existing object '{}'".format(self.getAbout())
        t = self._align.get(NSManager.CLARKS_LABELS['RDFABOUT'], default='')
        if (t == '') or (t == None): 
            raise ValueError('Alignment._parseEDOAL(): Alignment id as {} attribute is required'.format(NSManager.CLARKS_LABELS['RDFABOUT']))
        else: self.about = t
 
    def getAbout(self):
        '''
        Reifies the IRI of this alignment. Returns None when the alignment has not yet been parsed from its source.
        '''
        if not hasattr(self, 'about'):
            return None
        return self.about
    
    def getLevel(self): 
        '''
        Characterises the type of the alignment, conform the specification in 'Euzenat & Shvaiko, Ontology Matching, 2nd ed., sect.10.1.5 Alignment Format, pp.329-331'
        '''   
        # TODO: Consider other EDOAL levels than 2EDOAL only
        if not hasattr(self, 'level'):
            t = self._align.find(str(self.nsMgr.asClarks('align:level')))
            if t == None: raise RuntimeError('Alignment.getLevel(): No alignment <level> element found in Alignment {}'.format(self.about))
            if not t.text in ['2EDOAL', '2']: 
                raise NotImplementedError('Alignment.getLevel(): Alignment level other than 2, e.g., EDOAL, not supported; found {}'.format(t.text))
            self.level = t.text
        return self.level
         
    def getCreator(self):
        if not hasattr(self, 'creator'):       
            c = self._align.find(str(self.nsMgr.asClarks('dc:creator')))
            if c == None: raise RuntimeError('Alignment.getCreator(): No <creator> element found in Alignment {}'.format(self.about))
            self.creator = c.text
        return self.creator
        
    def getDate(self):    
        # Date is not a required field  
        if not hasattr(self, 'date'): 
            d = self._align.find(str(self.nsMgr.asClarks('dc:date')))
            if d == None: self.date = None
            else: self.date = d.text
        return self.date

    def getMethod(self):    
        # Method is not a required field
        if not hasattr(self, 'method'): 
            m = self._align.find(str(self.nsMgr.asClarks('alext:method')))
            if m != None: self.method = m.text
            else: self.method = None
        return self.method
    
    def getPurpose(self):
        # Purpose is not a required field
        if not hasattr(self, 'purpose'): 
            p = self._align.find(str(self.nsMgr.asClarks('alext:purpose')))
            if p != None: self.purpose = p.text
            else: self.purpose = None
        return self.purpose
    
    def getType(self):
        if not hasattr(self, 'type'): 
            t = self._align.find(str(self.nsMgr.asClarks('align:type')))
            if t == None: raise RuntimeError('Alignment.getType(): Edoal element <edoal:type> required; none found')
            if not t.text in ['**', '?*', '*?', '??']:
                raise ValueError('Alignment.getType(): Incorrect value of element <:type> required, Expected {}, found {}'.format('**, ?*, *?, ??', t.text))
            else: self.type = t.text
        return self.type
    
    class OntoRef():
        '''
        This class implements only a reference to an ontology, not the actual ontology itself.
        '''

        def __init__(self, alignment_element=None, ns_mgr=None):
            assert isinstance(alignment_element, ET.Element), "Alignment.OntoRef.init(): Fatal: parsing ontology information from Alignment requires proper <Alignment> element, got {}".format(alignment_element)
            assert isinstance(ns_mgr, NSManager), "Alignment.OntoRef.init(): Fatal: Cannot parse ontology from Alignment without proper namespace manager, got {}".format(ns_mgr)
            o = alignment_element.find(str(ns_mgr.asClarks('align:Ontology')))
            if (o == None): 
                raise ValueError('Alignment.OntoRef.init(): Missing required ontology element ({})'.format(str(ns_mgr.asClarks('align:Ontology'))))
            # TODO: implement RFC3987 for namespaces and, particularly in this case, to create a valid iri as 'scheme ":" hier-part' (see https://tools.ietf.org/html/rfc3986#section-3)
            # Now, we settle for assuming the about label represents a valid iri, and enclosing that in an '< >' pair 
            self.name = '<' + o.get(NSManager.CLARKS_LABELS['RDFABOUT'], default='') + '>'
            if (self.name == ''): 
                raise ValueError('Alignment.OntoRef.init(): Ontology id as {} attribute is required'.format(NSManager.CLARKS_LABELS['RDFABOUT']))
            
            l = o.find(str(ns_mgr.asClarks('align:location')))
            if (l == '') or (l == None): self.location = None
            else: self.location = l.text
            
            path = str(ns_mgr.asClarks('align:formalism')) + '/' + str(ns_mgr.asClarks('align:Formalism'))
            f = o.find(path)
            if (f == '') or (f == None): 
                raise ValueError('Alignment.OntoRef.init(): Ontology id as {} attribute is required'.format(path))
            # TODO: implement RFC3987 for namespaces and, particularly in this case, to create a valid iri as 'scheme ":" hier-part' (see https://tools.ietf.org/html/rfc3986#section-3)
            # Now, we settle for assuming the about label represents a valid iri, and enclosing that in an '< >' pair 
            self.formalism_uri = '<' + f.get(str(ns_mgr.asClarks('align:uri')), default='') + '>'
            self.formalism_name = f.get(str(ns_mgr.asClarks('align:name')), default='')
        
        def __repr__(self):
            return "onto '{}' @ '{}' in formalism '{}' ({})".format(self.name, self.location, self.formalism_name, self.formalism_uri)
        
        def __str__(self):
            '''
            Reifies the iri of this ontology
            '''
            return self.name
        
    def getSrcOnto(self):
        if not hasattr(self, 'srcOnto'):
            o = self._align.find(str(self.nsMgr.asClarks('align:onto1')))
            if o == None: raise RuntimeError('Alignment.getSrcOnto(): Edoal element "{}" required; none found'.format(str(self.nsMgr.asClarks('align:onto1'))))
            self.srcOnto = self.OntoRef(o, self.nsMgr)
        return self.srcOnto

    def getTgtOnto(self):
        if not hasattr(self, 'tgtOnto'):
            o = self._align.find(str(self.nsMgr.asClarks('align:onto2')))
            if o == None: raise RuntimeError('Alignment.getTgtOnto(): Edoal element <edoal:onto2> required; none found')
            self.tgtOnto = self.OntoRef(o, self.nsMgr)
        return self.tgtOnto         

    def _parseBooleanExpression(self, el=None):
        '''
        Parse a boolean entity construction.
        Return:
        EE (of type _EntityConstruction), representing the boolean construction of entities or entity_expressions (hence, recursive)
        '''
        from edoalparser.parserTools import _EntityConstruction
        assert el.tag in ['and', 'or', 'not'], 'Alignment._parseBooleanExpression(): Illegal edoal entity construction: boolean combinations require "and", "or", or "not", but "{}" found'.format(el.tag)
        raise NotImplementedError('Alignment._parseBooleanExpression(): Boolean edoal entity constructions not supported (yet, please implement me)')

    def _parseComposeExpression(self, el=None):
        '''
        Parse a Composed entity construction (<compose rdf:parseType="Collection">). 
        A composed entity construction can represent either a property path construct, as follows:
        1: <compose> relexpr* propexpr </compose>
        or a relation path construct, as follows:
        2: <compose> relexpr* </compose>
        '''
        from edoalparser.parserTools import Path
        assert el.tag.lower() == Alignment.EDOAL['CMPS'], 'Alignment._parseComposeExpression(): Illegal edoal entity construction: compose-expression requires "compose", but "{}" found'.format(el.tag)
        print("Found <compose>")
        
        path = Path()
        if len(list(el)) == 0:
            # If a <compose> element has no children, an empty path construct remains;
            # An empty path is equivalent to the identity relation, hence, when applied to an object it has as unique value the object itself
            return path
        elif el[0].tag.lower() == Alignment.EDOAL['RELN'] or el[0].tag.lower() == Alignment.EDOAL['PROP']:
            # Assume a path expression, create the path
            print ("parsing {}".format(el[0]))
            if el[0].tag.lower() == Alignment.EDOAL['RELN']:
                for element in list(el[0]):
                    if element.tag.lower() == Alignment.EDOAL['RELN']:
                        rel = self._parseRelation(element)
                        path.append(rel)
                    elif element.tag.lower() == Alignment.EDOAL['PROP']:
                        # The final Property element, closing the path
                        break
                    else: 
                        # Found a complex path expression, i.e., the sibling is a (complex) reln-expression in its own right.
                        # Here, too, recursion is required      
                        raise NotImplementedError('Alignment._parseComposeExpression(): Complex edoal property constructions ({}) in paths not supported (yet, please implement me)'.format(element.tag))
            # Now the relation path has been exhausted, hence find the (optional) concluding property
            if len(path) == 0: 
                # Relation path was empty, hence make sure we address the right attribute
                element = el[0]
            if element.tag.lower() == Alignment.EDOAL['PROP']:
                # Add the concluding property to the path 
                prop = self._parseProperty(element)
                path.append(prop)
            return path        
        else: raise AssertionError('Alignment._parseComposeExpression(): Illegal entity element for path constructs: found "{}"'.format(el[0].tag))

    def _parseClosureOperator(self, el=None):
        '''
        Parse a closure operation on a Relation
        Return:
        EE (of type _EntityConstruction) that represents the closure operators 'inverse', 'symmetric', 'transitive', 'reflexive'
        '''
        assert el.tag in ['inverse', 'symmetric', 'transitive', 'reflexive'], 'Alignment._parseClosureOperator(): Illegal edoal entity construction: closure operator expected, but "{}" found'.format(el.tag)
        raise NotImplementedError('Alignment._parseClosureOperator(): Closure operator "{}" on Relations not supported (yet, please implement me)'.format(el.tag))

    def _parseConstructExpression(self, el=None):
        '''
        Parse an entity construction expression, i.e., an expression composed of a combination of entities
        '''
        if el.tag in ['and', 'or', 'not']:
            return self._parseBooleanExpression(el)
        elif el.tag.lower() == Alignment.EDOAL['CMPS']:
            return self._parseComposeExpression(el)
        elif el.tag in ['inverse', 'symmetric', 'transitive', 'reflexive']:
            return self._parseClosureOperator(el)
        else:
            raise AttributeError('Alignment._parseConstructExpression(): An entity expressions cannot contain a "{}" construct'.format(el.tag))

    def _parseAttribute(self, asIRI=True, *, element=None, el_attr=None):
        assert element != None and isinstance(element, Element), "Cannot get an attribute from an empty <element>"
        assert el_attr != None and isinstance(el_attr, str) and el_attr != '', "Cannot get an <element>'s attribute without its name"
        attr_value = element.get(el_attr)
        if attr_value == None: return None
        assert attr_value != '', 'Alignment._parseAttribute(): An Edoal <{}> element requires a value for its "{}" attribute.'.format(element.tag, el_attr)
        if asIRI:
            return self.nsMgr.asIRI(attr_value)
        else: return attr_value

    def _parseEntity(self, el=None):
        '''
        Parse the EDOAL XML <Entity> element and return the relevant parts. Internal use only! 
        '''
        # TODO: It might be better to return an EntityExpression here
        assert isinstance(el, Element), "Alignment._parseEntity(): Cannot parse edoal entity expression without proper type <Element>, got {}".format(type(el))

        if (el.tag.lower() in [Alignment.EDOAL['CLASS'], Alignment.EDOAL['CAOR'], Alignment.EDOAL['CADR'], Alignment.EDOAL['CATR'], Alignment.EDOAL['CAVR']]):
            # Found a CLASS expression
            return self._parseClass(el)
               
        elif (el.tag.lower() in [Alignment.EDOAL['PROP'], Alignment.EDOAL['PDR'], Alignment.EDOAL['PTR'], Alignment.EDOAL['PVR']]):
            # Found a PROPERTY expression
            return self._parseProperty(el)
        
        elif (el.tag.lower() in [Alignment.EDOAL['RELN'], Alignment.EDOAL['RDR'], Alignment.EDOAL['RCDR']]):
            # Found a RELATION expression
            return self._parseRelation(el)
        
        elif (el.tag.lower() == Alignment.EDOAL['INST']):
            # Found an INSTANCE expression
            return self._parseInstance(el)
        
        else: 
            # Checked for all possibilities. If code gets here, an illegal EDOAL construct was detected
            assert False, 'Alignment._parseEntity(): Illegal Edoal construction: found <{}> element within <entity> element, quitting'.format(el.tag)

    def _parseClass(self, cls_el):
        '''
        A <Class> element introduces either a simple Class, a Class Construction, or a Class Restriction
        '''
        from edoalparser.parserTools import EClass
        if cls_el.tag.lower() == Alignment.EDOAL['CLASS']:
            # <Class> element found
            iriref = self._parseAttribute(element=cls_el, el_attr=NSManager.CLARKS_LABELS['RDFABOUT'])
            if iriref == None:
                # Complex Class Construct found
                assert isinstance(cls_el, list), "Alignment._parseClass(): A <{}> element requires sub-elements, but none found".format(cls_el.tag)
                return self._parseConstructExpression(cls_el[0])
            else:
                # Simple Class Entity found.
                assert iriref != '', \
                    'Alignment._parseClass(): An Edoal Class expression requires a value for its "{}" attribute.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
                assert cls_el.text == None and len(list(cls_el)) == 0, \
                    'Alignment._parseClass(): A simple Edoal Class expression cannot contain other elements or values.'.format(cls_el)
                return EClass(entity_iri=iriref, nsMgr=self.nsMgr)
        else:
            assert cls_el.tag.lower() in [Alignment.EDOAL['CAOR'], Alignment.EDOAL['CADR'], Alignment.EDOAL['CATR'], Alignment.EDOAL['CAVR']], \
                'Alignment._parseClass(): Illegal Edoal construction: found <{}> element as part of <class> expression, quitting'.format(cls_el.tag)
            # Class Restriction found
            raise NotImplementedError('Alignment._parseClass(): Edoal Class Restriction constructs found ({}); not supported (yet, please implement me)'.format(cls_el.tag))
        
    def _parseProperty(self, prop_el):
        '''
        A <Property> element introduces either a simple Property, a Property Construction, or a Property Restriction
        '''
        from edoalparser.parserTools import EProperty
        if prop_el.tag.lower() == Alignment.EDOAL['PROP']:
            # <Property> element found
            iriref = self._parseAttribute(element=prop_el, el_attr=NSManager.CLARKS_LABELS['RDFABOUT'])
            if iriref == None:
                # Complex Property Construct found
                assert len(list(prop_el)) > 0, "Alignment._parseProperty(): A <{}> element requires sub-elements, but none found".format(prop_el.tag)
                return self._parseConstructExpression(prop_el[0])
            else:
                # Simple Property Entity found.
                assert iriref != '', \
                    'Alignment._parseProperty(): An Edoal Property expression requires a value for its "{}" attribute.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
                assert prop_el.text == None and len(list(prop_el)) == 0, \
                    'Alignment._parseProperty(): A simple Edoal Property expression cannot contain other elements or values.'.format(prop_el)
                # TODO: Language attribute in Property Entity currently ignored
                if prop_el.get(Alignment.EDOAL['LANG']) != None: 
                    warnings.warn('Alignment._parseProperty(): Not Implemented Yet: <Property> element has got language attribute ({}), ignored'.format(prop_el.get(Alignment.EDOAL['LANG'])))
                return EProperty(entity_iri=iriref, nsMgr=self.nsMgr)
        else: 
            assert prop_el.tag.lower() in [Alignment.EDOAL['PDR'], Alignment.EDOAL['PTR'], Alignment.EDOAL['PVR']], \
                'Alignment._parseProperty(): Illegal Edoal construction: found <{}> element as part of <property> expression, quitting'.format(prop_el.tag)
            # Property Restriction found
            raise NotImplementedError('Alignment._parseProperty(): Edoal Property Restriction construct ({}) not supported (yet, please implement me)'.format(prop_el.tag))
    
    def _parseRelation(self, reln_el):
        '''
        Relations correspond to object properties in OWL
        A <Relation> element introduces either a simple Relation, a Relation Construction, a Relation Closure, or a Relation Restriction
        '''
        from edoalparser.parserTools import ERelation
        if reln_el.tag.lower() == Alignment.EDOAL['RELN']:
            # <Relation> element found
            iriref = self._parseAttribute(element=reln_el, el_attr=NSManager.CLARKS_LABELS['RDFABOUT'])
            if iriref == None:
                # A Relation Construction or Closure found
                assert len(list(reln_el)) > 0, "Alignment._parseRelation(): A <{}> element requires sub-elements, but none found".format(reln_el.tag)
                return self._parseConstructExpression(reln_el[0])
            else:
                # Simple Relation Entity found.
                assert iriref != '', \
                    'Alignment._parseRelation(): A simple Edoal Relation expression requires a value for its "{}" attribute.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
                assert reln_el.text == None and len(list(reln_el)) == 0, \
                    'Alignment._parseRelation(): A simple Edoal Relation expression cannot contain other elements or values.'.format(reln_el)
                return ERelation(entity_iri=iriref, nsMgr=self.nsMgr)
        else: 
            assert reln_el.tag.lower() in [Alignment.EDOAL['RDR'], Alignment.EDOAL['RCDR']], \
                'Alignment._parseRelation(): Illegal Edoal construction: found <{}> element as part of <relation> expression, quitting'.format(reln_el.tag)
            # Relation Restriction entity found
            raise NotImplementedError('Alignment._parseRelation(): Edoal Relation Restriction construct ({}) not supported (yet, please implement me)'.format(reln_el.tag))
        
    def _parseInstance(self, inst_el=None):
        from edoalparser.parserTools import EInstance
        assert inst_el != None, 'Alignment._parseInstance(): Cannot create instance from Nothing'
        assert inst_el.tag.lower() == Alignment.EDOAL['INST'], "Alignment._parseInstance(): <Instance> element expected, got <{}>".format(inst_el.tag)
        assert len(inst_el) == 0, 'Alignment._parseInstance(): An Edoal Instance expression cannot have child elements, but found {} children'.format(len(inst_el))
        assert inst_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != None and inst_el.get(NSManager.CLARKS_LABELS['RDFABOUT']) != '', \
            'Alignment._parseInstance(): An Edoal Instance expression requires an "{}" attribute and value to specify its individual'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
        return EInstance(inst_el.get(NSManager.CLARKS_LABELS['RDFABOUT']), nsMgr=self.nsMgr)
    
    def _parseLiteral(self, lit_el=None):
        assert lit_el != None and lit_el.tag.lower() == Alignment.EDOAL['LIT'], 'Alignment._parseLiteral(): <Literal> element expected, got <{}>, quitting'.format(lit_el)
        value = lit_el.get(Alignment.EDOAL['STRNG'])
        assert value, 'Alignment._parseLiteral(): A <Literal> element requires an "edoal:string" attribute, but got <{}>'.format(lit_el)
        v_type = lit_el.get(Alignment.EDOAL['TYPE'])
        if v_type == None: value_type = str(Alignment.EDOAL['STRNG'])
        else: value_type = v_type
        return value, self.nsMgr.asIRI(value_type)

    def _parseOperation(self, operation_el=None):
        '''
        Parse the <edoal:Apply> or the <edoal:Aggregate> elements that specify the operation(s) that are implied by this transformation; 
        Store the results as an parserTools.Transformation object.
        '''
        from edoalparser.parserTools import Transformation
        from transformations import unitconversion
        
        assert isinstance(operation_el, ET.Element) and (operation_el.tag.lower() == Alignment.EDOAL['APPLY'] or operation_el.tag.lower() == Alignment.EDOAL['AGGR']), \
            "Alignment._parseOperation(): <Apply> or <Aggregate> element expected, got <{}>, quitting".format(operation_el)
        operator = operation_el.get(Alignment.EDOAL['OPRTR'])
        assert operator, "Alignment._parseOperation(): an <Apply> or <Aggregate> element requires an 'edoal:operator' attribute, but got '{}'".format(operator)
        # Since EDOAL does not prescribe a '< >' pair around XML attributes that represent an IRI, this is added here
        # TODO: (low) give warning for missing '<' or '>' in '< >' pair
        if operator[0] != '<': operator = '<' + operator
        if operator[-1] != '>': operator = operator + '>'
        if not self.nsMgr.isIRI(operator): raise AttributeError("Alignment._parseOperation(): Expected iri value for attribute edoal:operator, got {}".format(operator))
        # Get the operator
        pf, pf_expanded, functionName = self.nsMgr.splitIri(operator)
        # Turn the operator into a callable function
        if pf == 'op:' or pf_expanded in ['http://www.w3.org/2005/xpath-functions', 'http://www.w3.org/2001/XMLSchema']:
            # XPath function found
            raise NotImplementedError("Alignment._parseOperation(): XPath functions ({}) not supported (yet, please implement me).".format(operator))
        elif pf == 'http:':
            # Webservice found
            raise NotImplementedError("Alignment._parseOperation(): Webservice functions ({}) not supported (yet, please implement me).".format(operator))
        elif pf == 'java:':
            # Java method found
            raise NotImplementedError("Alignment._parseOperation(): Java method functions ({}) not supported (yet, please implement me).".format(operator))
        elif pf == 'medtfn:' or pf_expanded == self.nsMgr.expand('medtfn'):
            # Python method in own library found, check if it exists
#             print("Alignment._parseOperation(): Adding function name: {}".format(functionName))
            fpath, fname = functionName.split('/')
            libModule = NSManager.LOCAL_BASE_PATH + 'transformations/' + fpath + '.py'
            assert os.path.isfile(libModule), "Alignment._parseOperation(): Cannot find transformation library module '{}' from current directory {}".format(libModule, os.getcwd())
            if fpath == 'unitconversion': 
                assert fname in dir(unitconversion), "Alignment._parseOperation(): Cannot find operation '{}' in transformation library module '{}'".format(fname, libModule)
            else: raise NotImplementedError("Alignment._parseOperation(): Transformation library module '{}.py' is available but not supported/imported (yet, please implement me)".format(fpath))
            # Create a Transformation
            transformation = Transformation(python_module=fpath, method_name=fname)
        else: raise AttributeError("Alignment._parseOperation(): Unfamiliar notation for transformation operator: prefix '{}', expanded '{}', function '{}'".format(pf, pf_expanded, functionName))
            
        # Get the operands; note that 'operands' mean: ways to achieve the value(s)
        operands = []
        args = operation_el.find(Alignment.EDOAL['ARGS'])
        assert args != None, "Alignment._parseOperation(): Element <{}> requires subelement <{}:{}> but none found.".format(operation_el.tag, self.nsMgr.asQName(Alignment.EDOAL['ARGS']))
        if args.get(NSManager.CLARKS_LABELS['RDFPARSTP']).lower() == Alignment.EDOAL['COLL']:
            
            for value_el in args[0].iter():
#                 print("Alignment._parseOperation(): Adding operand '{}'".format(value_el.tag))
                if value_el.tag in [Alignment.EDOAL['APPLY'], Alignment.EDOAL['AGGR']]:
                    # Found another operation; resolve this by going recursive on this very same method, i.e., _parseOperation
                    # TODO: handle recursive operation definitions, i.e, operations that have operations as arguments
                    raise NotImplementedError("Alignment._parseOperation(): Cannot handle recursive definitions for operations, (yet, please implement me), found {}".format(str(value_el)))
                else:
                    operands.append(self.Value(el=value_el, parse_alignment=self))
        else: raise RuntimeError("Alignment._parseOperation(): <{}> expected as attribute to <{}> element, got <{}>".format(Alignment.EDOAL['COLL'], args.tag, args.get(NSManager.CLARKS_LABELS['RDFPARSTP'])))
        # Store the operands together with the operation
        transformation.registerOperands(operands)
        return transformation

    class Value():
        '''
        An EDOAL value expression, representing: 
        (1) a literal value
        (2) an individual (instance)
        (3) an attribute expression, i.e, a value that can be reached through application of a Property or Relation
        (4) a value computable by a function from arguments; the arguments are again values 
        
        BNF definition is (refer to http://alignapi.gforge.inria.fr/edoal.html):
        <value> value </value>
        value ::= <Literal {edoal:type=" URI "} edoal:string=" STRING " />
                | instexpr 
                | attrexpr 
                | <Apply edoal:operator=" URI "> <arguments rdf:parseType="Collection">value*</arguments> </Apply> 
                | <Aggregate edoal:operator=" URI "> <arguments rdf:parseType="Collection">value*</arguments> </Aggregate>
        
        instexpr ::= <Instance rdf:about=" URI "/>
        attexpr ::= propexpr | relexpr
        '''
        
        def __init__(self, el=None, parse_alignment=None):
            '''
            Input: 
            - el (xml.etree.ElementTree.Element): an <entity_expression> element that is, or contains, a <value> element 
            - parse_alignment (Alignment): 
            '''
            from edoalparser import parserTools
            assert isinstance(el, Element), "Alignment.Value.__init__(): Cannot parse non xml.tree elements, got [{}] of type [{}]".format(el, type(el))
            assert isinstance(parse_alignment, Alignment), "Alignment.Value.__init__(): Cannot parse a Value element without an alignment, got {}".format(type(parse_alignment))

            # Establish 'el' IS or CONTAINS a Value
            if len(list(el)) == 0:
                # 'el' IS value
                element = el
            else:    
                # 'el' CONTAINS value
                element = el[0]
            
            assert element.tag.lower() in [Alignment.EDOAL['LIT'], Alignment.EDOAL['APPLY'], Alignment.EDOAL['AGGR'], Alignment.EDOAL['INST'], Alignment.EDOAL['PROP'], Alignment.EDOAL['RELN']], "Alignment.Value.__init__(): Unexpected element: <{}>".format(element.tag)            
            # Do all verification on lowercase strings
            self._entity_type = element.tag.lower()
            
            if (self._entity_type == Alignment.EDOAL['LIT']):
                self.value, self.value_type = parse_alignment._parseLiteral(lit_el=element)
            
            elif (self._entity_type == Alignment.EDOAL['INST']):
                self._iriref = parse_alignment._parseInstance(inst_el=element).getIriRef()
                
            elif (self._entity_type == Alignment.EDOAL['PROP']):
                prop = parse_alignment._parseProperty(element)
                if isinstance(prop, parserTools.Path): self._path = prop
                else: self._iriref = prop.getIriRef()
                
            elif (self._entity_type == Alignment.EDOAL['RELN']):
                reln = parse_alignment._parseRelation(element)
                if isinstance(reln, parserTools.Path): self._path = reln
                else: self._iriref = reln.getIriRef()
                
            elif self._entity_type == Alignment.EDOAL['APPLY'] or self._entity_type == Alignment.EDOAL['AGGR']:
                self.operator = parse_alignment._parseOperation(element)

            else: 
                raise AttributeError('Alignment.Value.__init__(): A Value part can only contain a literal, instance, property, relation or a composed entity_expression (Apply or Aggregate), but found {}'.format(self._entity_type))

        def getEntityType(self):
            return self._entity_type
        
        def isLiteral(self):
            return self._entity_type == Alignment.EDOAL['LIT']

        def isIndividual(self):
            return self._entity_type == Alignment.EDOAL['INST']

        def isAttrExpression(self):
            return self._entity_type == Alignment.EDOAL['PROP'] or self._entity_type == Alignment.EDOAL['RELN']

        def isClass(self): 
            return self._entity_type == Alignment.EDOAL['CLASS']

        def isComputable(self):
            return self._entity_type == Alignment.EDOAL['APPLY'] or self._entity_type == Alignment.EDOAL['AGGR']

        def hasPath(self):
            return self.isAttrExpression() and hasattr(self, '_path')
        
        def getLiteral(self):
            if self._entity_type == Alignment.EDOAL['LIT']: 
                return self.value, self.value_type
            else: return None
        
        def getIndividual(self):
            if self._entity_type == Alignment.EDOAL['INST']: 
                return self.getIriRef()
            else: return None   
            
        def getAttrExpression(self):
            if self._entity_type in [Alignment.EDOAL['PROP'], Alignment.EDOAL['RELN']]: 
                return self.getIriRef()
            else: return None
        
        def getIriRef(self):
            if self._entity_type in [Alignment.EDOAL['INST'], Alignment.EDOAL['PROP'], Alignment.EDOAL['RELN']]:
                return self._iriref
            else: return None

        def getOperator(self):
            if self._entity_type in [Alignment.EDOAL['APPLY'], Alignment.EDOAL['AGGR']]: 
                return self.operator
            else: return None
        
        def getPath(self):
            if self.hasPath(): return self._path
            else: return None
            
        def __str__(self):
            if self.isLiteral(): result = self.getLiteral()
            elif self.isIndividual(): result = self.getIndividual()
            elif self.isAttrExpression(): result = self.getAttrExpression()
            elif self.isClass(): result = 'Error: found Class as impossible Value construct' 
            elif self.isComputable(): result = str(self.getOperator())
            else: return None
            result = str(result) + ' (' + self.getEntityType() + ')'
            return result 
        
        def __repr__(self):
            vl_repr = 'Object:' + str(type(self)) + ', entity type:' + self._entity_type
            vl_repr += '\n\tliteral value:' + str(self.getLiteral())
            vl_repr += '\n\tindividual value:' + str(self.getIndividual())
            vl_repr += '\n\tiri value:' + str(self.getIriRef())
            vl_repr += '\n\tpath:' + str(self.getPath())
            vl_repr += '\n\toperator value:' + str(self.getOperator())
            return vl_repr
            
    def _parseTransform(self, el):
        '''
        Build an parserTools.Transformation from the <edoal:Transformation> element.
        Returns:
        1 - An parserTools.Transformation, populated with all the relevant details
        2 - An EDOALparser.Value object that represents the target of the transformation
        '''
        TransformationElmnts = el.findall(str(self.nsMgr.asClarks('edoal:Transformation')))
        if len(TransformationElmnts) > 1: raise RuntimeWarning('Alignment._parseTransform(): One <edoal:Transformation> elements expected inside <edoal:transformation> element, found {} in stead. Only last one will remain!'.format(len(TransformationElmnts)))
        for TransformationElmnt in TransformationElmnts:
            direction = TransformationElmnt.get(Alignment.EDOAL['DRCTN'])
            if (direction == None) or not direction in ["o-", "-o"]:
                raise RuntimeError('Alignment._parseTransform(): Cannot parse a transformation without directional attribute, <Transformation edoal:direction=" STRING ">')
            # Parse the <edoal:entity1> and <edoal:entity2> elements that define the data transformation
            val1 = self.Value(el=TransformationElmnt.find(str(self.nsMgr.asClarks('edoal:entity1'))), parse_alignment=self)
            val2 = self.Value(el=TransformationElmnt.find(str(self.nsMgr.asClarks('edoal:entity2'))), parse_alignment=self)
            # Build from the parsed entities a valid and executable transformation, consisting of a source operation (incl. its operands) and the target tgtEntity entity
            if direction == 'o-':
                # This indicates that operation and its operands should be found in entity1
                if val1.getEntityType() in [Alignment.EDOAL['APPLY'], Alignment.EDOAL['AGGR']]:
                    operation = val1.getOperator()
                    if val2.getEntityType() in [Alignment.EDOAL['INST'], Alignment.EDOAL['PROP'], Alignment.EDOAL['RELN']]:
                        tgtEntity = val2
                    else: raise RuntimeError("Alignment._parseTransform(): Result of transformation cannot be another transformation or literal, got <{}>".format(val2.getEntityType()))
                else: raise RuntimeError("Alignment._parseTransform(): Direction attribute ({}) specifies operation on <entity1>, but no operation was found".format(direction))
            else: 
                # This indicates that operation and operands should be found in entity2
                assert direction == '-o', "Alignment._parseTransform(): Expected '-o' as direction of transformation, but got '{}'".format(direction)
                if val2.getEntityType() in [Alignment.EDOAL['APPLY'], Alignment.EDOAL['AGGR']]:
                    operation = val2.getOperator()
                    if val1.getEntityType() in [Alignment.EDOAL['INST'], Alignment.EDOAL['PROP'], Alignment.EDOAL['RELN']]:
                        tgtEntity = val1
                    else: raise RuntimeError("Alignment._parseTransform(): Result of transformation cannot be another transformation or literal, got <{}>".format(val1.getEntityType()))
                else: raise RuntimeError("Alignment._parseTransform(): Direction attribute ({}) specifies operation on <entity2>, but no operation was found".format(direction))

        return operation, tgtEntity
    
    def _parseCorrespondence(self, cell=None):
        '''
        Parse an alignment correspondence <align:Cell rdf:about=[name]> element
        Return it on success, or return None when duplicate found
        '''
        from edoalparser.parserTools import Correspondence
        assert isinstance(cell, Element), "Alignment._parseCorrespondence(): Expected xml.tree element, got type <{}>".format(type(cell))
        # Get the name, i.e., about attribute of <align:Cell rdf:about=[name]> element
        name = cell.get(NSManager.CLARKS_LABELS['RDFABOUT'])
        assert name != None and name != '', \
                'Alignment._parseCorrespondence(): An "{}" attribute requires a value, found empty string.'.format(NSManager.CLARKS_LABELS['RDFABOUT'])
        # Prevent duplicates to be added. Correspondences are identified by their rdf:about attribute
        if hasattr(self, '_corrs') and name in [c.getName() for c in self._corrs]:
            warnings.warn("Found duplicate correspondence '{}', skipping ...".format(name), category=UserWarning)
            return None
        # This is a new correspondence, hence create it and set its name
        corr = Correspondence(nsMgr=self.nsMgr)
        corr.setName(name=name)
        
        # Get the Translation part, i.e., the obligatory parts <entity1 & 2>, <measure> and <relation>
        # ... Get the source entity expression, i.e., the <align:entity1> element; validate that exactly 1 single <entity1> element is found
        srcs = cell.findall(str(self.nsMgr.asClarks(':entity1')))
        assert len(srcs) == 1, 'Alignment._parseCorrespondence(): Exactly 1 edoal entity expression <{}> required, found {}'.format(str(self.nsMgr.asClarks(':entity1')), len(srcs))
        src = srcs[0]
        assert src != None, 'Alignment._parseCorrespondence(): Edoal entity expression element <{}> required'.format(str(self.nsMgr.asClarks(':entity1')))
        assert len(src) > 0, 'Alignment._parseCorrespondence(): Empty edoal entity expression element <{}> found. Entity expression required'.format(str(self.nsMgr.asClarks(':entity1')))
        entityExpr = self._parseEntity(el=src[0])
        corr.setEE1(entity_expr=entityExpr)
        
        # ... Get the target entity expression, i.e., the <align:entity2> element; validate that exactly 1 single <entity2> element is found
        tgts = cell.findall(str(self.nsMgr.asClarks(':entity2')))
        assert len(tgts) == 1, 'Alignment._parseCorrespondence(): Exactly 1 edoal entity expression <{}> required, found {}'.format(str(self.nsMgr.asClarks(':entity2')), len(tgts))
        tgt = tgts[0]
        assert tgt != None, 'Alignment._parseCorrespondence(): Edoal entity expression required as <{}> element'.format(str(self.nsMgr.asClarks(':entity2')))
        assert len(tgt) > 0, 'Alignment._parseCorrespondence(): Empty edoal entity expression found ({}). Entity expression required'.format(str(self.nsMgr.asClarks(':entity2')))
        entityExpr = self._parseEntity(el=tgt[0])
        corr.setEE2(entity_expr=entityExpr)
        
        # Get the relation that holds between both entity expressions, i.e., <align:relation>
        rels = cell.findall(str(self.nsMgr.asClarks(':relation')))
        if rels == None or rels == []: raise RuntimeError('Alignment._parseCorrespondence(): Exactly one Edoal element <relation> required, but zero found in "{}"'.format(corr.getName()))
        elif len(rels) > 1: raise RuntimeError('Alignment._parseCorrespondence(): Exactly one Edoal element <relation> required, but found {} in "{}"'.format(len(rels), corr.getName()))
        corr.setCorrRelation(relation=self.canonicalCorrRelation(rels[0].text))
        
        # Get the measure with which the relation is estimated to hold between both entity expressions.
        msrs = cell.findall(str(self.nsMgr.asClarks(':measure')))
        if msrs == None or msrs == []: raise RuntimeError('Alignment._parseCorrespondence(): Exactly one Edoal element <measure> required, but zero found in "{}"'.format(corr.getName()))
        elif len(msrs) > 1: raise RuntimeError('Alignment._parseCorrespondence(): Exactly one Edoal element <measure> required, but found {} in "{}"'.format(len(msrs), corr.getName()))
        elif msrs[0].get(NSManager.CLARKS_LABELS['RDFDATATP']) == None: raise RuntimeError('Alignment._parseCorrespondence(): Cannot determine the type of the measure value: missing rdf.datatype attribute to <measure> element in {}'.format(corr.getName()))
        corr.setCorrMeasure(measure=msrs[0].text, measure_type=msrs[0].get(NSManager.CLARKS_LABELS['RDFDATATP']))
        
        # Get the optional Transformation parts, i.e., the <edoal:transformation> element; zero, one or more are acceptable
        tfs = cell.findall(str(self.nsMgr.asClarks('edoal:transformation')))
        for tf in tfs:
            operation, tgtEntity = self._parseTransform(tf)
            corr.appendTransform(transformation=operation, result_iri=tgtEntity)
        
        return corr

    def appendCorrespondence(self, corr):
        from edoalparser.parserTools import Correspondence            
        assert isinstance(corr, Correspondence), "Alignment.appendCorrespondence(): Expected a Correspondence to add, got {}".format(type(corr))
        self._corrs.append(corr)
        
    def getCorrespondences(self): 
        '''
        Extract from the EDOAL XML file all <map><Cell> ... </Cell></map> parts
        and populate a newly made Mediator.Correspondence class with the relevant information
        '''
        if not hasattr(self, '_corrs'):
            cells = self._align.findall(self.nsMgr.asClarks('align:map') + '/' + self.nsMgr.asClarks('align:Cell'))
            if len(cells) == 0:
                raise RuntimeError('Alignment.getCorrespondences(): An Edoal alignment requires at least one {} element, but zero found'.format(self.nsMgr.asClarks('align:map') + '/' + self.nsMgr.asClarks('align:Cell')))
            
            # Iterate over all <Cell>...</Cell> parts
            self._corrs = []
            for cell in cells:
                corr = self._parseCorrespondence(cell)
                self.appendCorrespondence(corr)
        return self._corrs
    
    def __str__(self):
        # for the time being, just return the raw representation
        return self.__repr__()
    
    def __repr__(self):
        result = "Alignment " + self.getAbout() + " aligns between:\n\t1: " + str(self.getSrcOnto()) + "\n\t2: " + str(self.getTgtOnto()) + "\n" + "with:\n" + \
            "\tlevel: {}\n\ttype: {}\n\tcreator: {} ({})\n\tmethod: {}\n\tpurpose: {}\n".format(self.getLevel(), self.getType(), self.getCreator(), self.getDate(), self.getMethod(), self.getPurpose()) + \
            "using namespaces:\n" + str(self.nsMgr) + "Correspondences:\n"
        for corr in self.getCorrespondences():
            result += str(corr)
        return result

        
if __name__ == '__main__':
    print('running main')

