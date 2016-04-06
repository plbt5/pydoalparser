'''
Created on 26 feb. 2016

@author: brandtp
'''

# from EdoalParser.alignment import Alignment
from parsertools.parsers.sparqlparser import parseQuery, parser
from .sparqlTools import Context
import xml.etree.cElementTree as ET
import warnings
from pprint import pprint

from turtle import __stringBody
import sys
from parsertools.base import ParseStruct


ns = {
#         'base'  : 'http://oms.omwg.org/wine-vin/',
#         'wine': 'http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#',
#         'vin': 'http://ontology.deri.org/vin#',
        'xml'   : 'http://www.w3.org/XML/1998/namespace',
        'rdf'   : 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs'  : 'http://www.w3.org/2000/01/rdf-schema#',
        'xmlns' : 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
        'dc'    : 'http://purl.org/dc/elements/1.1/',
        'myNS'  : 'http://ds.tno.nl/mediator/1.0/',
        'edoal' : 'http://ns.inria.org/edoal/1.0/#'
    }

EDOALCLASS = '{'+ ns['edoal'] + '}class'
EDOALRELN = '{'+ ns['edoal'] + '}relation'
EDOALPROP = '{'+ ns['edoal'] + '}property'
EDOALINST = '{'+ ns['edoal'] + '}instance'
EDOALCAOR = '{'+ ns['edoal'] + '}AttributeOccurenceRestriction'
EDOALCADR = '{'+ ns['edoal'] + '}AttributeDomainRestriction'
EDOALCATR = '{'+ ns['edoal'] + '}AttributeTypeRestriction'
EDOALCAVR = '{'+ ns['edoal'] + '}AttributeValueRestriction'
RDFABOUT = '{'+ ns['rdf'] + '}about'
EDOALDIRECTION = '{'+ ns['edoal'] + '}direction'
EDOALAPPLY = '{'+ ns['edoal'] + '}Apply'
EDOALOPRTR = '{'+ ns['edoal'] + '}operator'



class EntityExpression():
    def __init__(self, entity, entity_type):
        assert isinstance(entity, str) and entity_type in [EDOALPROP]
        self.entity = entity
        self.entity_type = entity_type
        
    def __str__(self):
        return self.entity + ' (' + self.entity_type +')'
 
class Mediator(object):
    '''
    The Mediator class performs translations of sparql queries or sparql variable bindings. This translation is based
    upon mappings from an alignment. Either a translation succeeds, resulting in a translated sparql query or variable binding, or
    fails. In the latter case the mediator provides information on the reason for failing, for other classes to proceed upon in
    a protocolised way of operation.
    '''
      
    @classmethod
    def canonical(cls, rel):
        if rel.lower() in ['=', 'equivalence', 'eq']:
            return 'EQ' 
        elif rel.lower() in ['<', '<=', 'subsumption', 'lt', 'lower-than', 'le']:
            return 'LT' 
        elif rel.lower() in ['>', '>=', 'subsumed', 'subsumedby', 'gt', 'greater-than', 'ge']:
            return 'GT'
        else: raise NotImplementedError('Entity expression relation {} not recognised'.format(rel))
             
    class Correspondence():
        '''
        A Correspondence specifies a single mapping from an entity expression in ontology A to a corresponding
        entity expression in ontology B. Each correspondence provides for a transformation of sparql data that 
        is expressed in terms of ontology A, into its semantic equivalent in terms of ontology B.
        '''
   
        def makeTransform(self, condition, operands, operation):
            '''
            Factory to create a transformation function.  
            '''
            def transform(self, value_logic_node):
                '''
                Transform a sparql ValueLogic node according to the specified operation, but only when the specified condition is met. 
                Otherwise, return None
                '''
                assert isinstance(value_logic_node, ParseStruct)
                if condition(value_logic_node):
                    nodes = value_logic_node.searchElements(element_type=operands)
                    if nodes == []: raise RuntimeError("Cannot find the operand [{}] to transform")
                    for node in nodes:
                        for itemValue in node.getItems():
                            if operands in [parser.DECIMAL, parser.INTEGER, parser.DOUBLE]:
                                value = float(itemValue)
                            transfdValue = operation(value)
                            node.updateWith(str(transfdValue))
                    return value_logic_node
                else: return None
                
            return transform
                
        def __init__(self, el):
            '''
            Create a new Correspondence by copying the children from an EDOAL cell into the object's fields. 
            -> el (ET.element): should contain the 'xmlns:Cell' element of an EDOAL mapping
            Prerequisite: this EDOAL cell should contain the elements: <xmlns:entity1>, <xmlns:entity2>, and <xmlns:relation>
            
            Returns an object with fields:
            - .name: (string)           : the name of the correspondence (reification of rdf:about in <Cell>)
            - .src: (EntityExpression) : the source EntityExpression expression
            - .tgt: (EntityExpression) : the target EntityExpression expression
            - .rel: (string)           : the EDOAL EntityExpression expression relation
            - .tfs: [](transform)      : (optional) List of transformations on ValueLogics 
                
            ''' 
            
            self.name = 'Mapping_Rule_0'
            self.src = EntityExpression('{http://ds.tno.nl/ontoA/}hasTemp', EDOALPROP)
            self.tgt = EntityExpression('{http://ds.tno.nl/ontoB/}hasT', EDOALPROP)
#             self.rel = canonical('equivalence')
            self.rel = 'EQ'
            self.tfs = []
            self.tfs.append(self.__class__.makeTransform(self, condition=lambda x: True, operands=(parser.DECIMAL), operation=lambda x: round(x/5 * 9 + 32,2) ))

            
        def render(self):
            '''
                Produce a rendering of the Correspondence as EDOAL Map
            '''
            #TODO: Produce a rendering of the Correspondence in EDOAL XML
            return self.getName() + ': '+ self.src +' --['+ self.rel +']--> '+ self.tgt 
        
        def getName(self):
            return self.name
        
        def __str__(self):
            return self.getName()
         
        def translate(self, data):
            '''
            Translate the data according to the EDOAL alignment from the Correspondence Class
            - data (string): the data to be translated; this data can represent one out of the following
                1: a sparql query (one of: SELECT, ASK, UPDATE, DESCRIBE)
                2: a sparql result set
                3: an RDF triple or RDF graph
            returns: the translated data, in the same rendering as received
            
            As of this moment, only data of type 1 is supported, and even then only SELECT
            '''
            
            # Determine the sparql context for the src, i.e., in the parsed sparql tree, determine:
            # the Node(s), their binding(s) and their constraining expression(s)
            rq = parseQuery(data)
            context = Context(entity_expression=self.src, sparqlData=data)
            
            context.render()
            print("translating {} ---> {}".format(self.src, self.tgt))

            # Change the src into the tgt. 
            # 1 - First the concepts in the Query Pattern part of the query.
            #     The src can occur in multiple BGP's, and each qpNode represents a distinct BGP
            for qpt in context.qpTriples:
                print("tgt:", self.tgt)
                #TODO: Namespace problem, resolve
                uri, tag = self.tgt.entity[1:].split("}")
                tgt = 'ToDoNS:'+tag
                print("src:", str(qpt.represents))
                print("tgt:", self.tgt)
                for qpn in qpt.qpNodes:
                    qpn.about.updateWith(tgt)
            
            # 2 - Then transform the constraints from the Query Modification part of the query.

                
            #     The src can be bound to more than one variable that can have more constraints.
            #     The qmNodes in the context is a dictionary for which the src indexes a list of variables. 
            #     Each variable is represented by a qmNode; each constraint by a valueLogic.
            
            for var in context.constraints:
                for vc in context.constraints[var]:
                    for vl in vc.valueLogics:
                        for tf in self.tfs:
                            tf(self, value_logic_node = vl)
            
            context.parsedQuery.render()
            return True
    
    def __init__(self, edoal):
        '''
        The Mediator can be initialized with an EDOAL alignment.  
        - edoal : edoal expression, represented as ET.Element
                
        The mediator represents one complete EDOAL Alignment, as follows:
            self.ns      ::== dict with uri's as key and prefix as value
            self.about   ::== string
            self.creator ::== xml.etree.Element
            self.date    ::== xml.etree.Element
            self.method  ::== xml.etree.Element
            self.purpose ::== xml.etree.Element
            self.level   ::== string
            self.type    ::== string
            self.onto1   ::== xml.etree.Element
            self.onto2   ::== xml.etree.Element
            self.corrs ::== List of Correspondence
        '''
        #TODO: Consider other EDOAL levels than 2EDOAL only
        #TODO: Consider other alignments than EDOAL only, e.g., SPIN
        if edoal == None:
            raise TypeError('EDOAL expression expected')
        elif type(edoal) != ET.Element:
            raise TypeError('EDOAL expression of type {} expected'.format(type(ET.Element)))
        else:
            # Get the namespaces first, and plug them reversed into self
            self.ns = ns
            # Get the Alignment
            align = edoal.find('xmlns:Alignment', self.ns)
        
        if align == None: 
            raise RuntimeError('Cannot find required "xmlns:Alignment" element in XML-tree')
        else: t = align.get(RDFABOUT, default='')
        
        if (t == '') or (t == None): 
            raise ValueError('Alignment id as {} attribute expected'.format(RDFABOUT))
        else: self.about = t
        
        t = align.find('xmlns:level', self.ns)
        if t == None: raise RuntimeError('No alignment <level> element found in Alignment {}'.format(self.about))
        else: self.level = t.text
        if self.level != '2EDOAL': 
            raise NotImplementedError('Alignment level other than "2EDOAL" not supported; found {}'.format(self.level))
                
        self.creator = align.find('dc:creator', self.ns)
        self.date = align.find('dc:date', self.ns)
        self.method = align.find('xmlns:method', self.ns)
        self.purpose = align.find('xmlns:purpose', self.ns)
        t = align.find('xmlns:type', self.ns)
        
        if t == None: raise RuntimeError('Edoal element <xmlns:type> required; found {}'.format(t))
        else: self.type = t.text
        if not self.type in ['**', '?*', '*?', '??']:
            raise ValueError('Incorrect value of element <xmlns:type> required, Expected {}, found {}'.format('**, ?*, *?, ??', self.type))
        self.onto1 = align.find('xmlns:onto1', self.ns)
        self.onto2 = align.find('xmlns:onto2', self.ns)
        self.corrs = {}
        
        cells = align.findall('xmlns:map/xmlns:Cell', self.ns)

#         print('#cells', len(cells))
        if len(cells) == 0:
            raise RuntimeError('An Edoal alignment requires at least one <xmlns:map><xmlns:Cell>...</xmlns:Cell></xmlns:map> element, but zero found')
        for el in cells:
            c = self.Correspondence(el)
            self.corrs[c.getName()] = c
       

    def __len__(self):
        '''
        Calculates the length of the Mediator as the amount of Correspondences it contains.
        '''
        return len(self.corrs)     
    
    def getName(self):
        '''
        Retrieves the name of this Mediator, which reifies the Alignment's "about" attribute.
        '''
        return self.about
     
    def render(self):
        '''
            Produce a rendering of the Mediator in EDOAL XML
        '''
        #TODO: Produce a rendering of the Mediator in EDOAL XML
        s = self.__str__()
        for k, v in sorted(self.corrs.items()):
            s += v.render()
        return s
    
    def __str__(self):
        return self.getName() + ' (onto1: ' + self.onto1.find('xmlns:Ontology', self.ns).get(RDFABOUT) + \
            ' onto2: ' + self.onto2.find('xmlns:Ontology', self.ns).get(RDFABOUT) + ')'
    
if __name__ == '__main__':
    print('running main')


