'''
Created on 26 feb. 2016

@author: brandtp
'''

# from EdoalParser.alignment import Alignment
from sparqlparser.grammar import *
from .sparqlTools import Context
import xml.etree.cElementTree as ET
import warnings
from pprint import pprint

from turtle import __stringBody
import sys

# '''
# conflictType represents the different types of semantic conflict that can be distinguished:
# - None:    No conflict
# - Dinges:    Another conflict, no idea yet
# '''
# conflictType = ['None', 'Dinges']
# #TODO: Specifying the various conflictTypes
# 
# class SemanticConflict(object):
#     '''
#     An SemanticConflict object will be created during data translation whenever the translation cannot
#     guarantee the semantic correctness of the translation.  
#     '''
#     
#     def __init__(self):
#         self.type = {}
# 
# class VarBounding(object):
#     '''
#     '''
#     def __init__(self):
#         pass
# 
# class Query(SPARQLElement):
#     '''
#     '''
#     def __init__(self):
#         pass
 


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
   
        def __init__(self, el):
            '''
            Create a new Correspondence by copying the children from an EDOAL cell into the object's fields. 
            -> el (ET.element): should contain the 'xmlns:Cell' element of an EDOAL mapping
            Prerequisite: this EDOAL cell should contain the elements: <xmlns:entity1>, <xmlns:entity2>, and <xmlns:relation>
            
            Returns an object with fields:
            - .nme: (string) : the name of the correspondence (reification of rdf:about in <Cell>)
            - .src: (elementtree Element) : the source edoalEntity expression
            - .tgt: (elementtree Element) : the target edoalEntity expression
            - .rel: (string) : the EDOAL edoalEntity expression relation
            - .tfn: []       : List of translations for individuals of this source
                * {'direction'} : direction if this transformation
                * {'entity1'}   : (elementtree Element) : transformation details
                * {'entity2'}   : (elementtree Element) : transformation details
            ''' 
            self.nme = el.get(RDFABOUT)
            if self.nme == None: raise ValueError('XML attribute {} expected in element {}'.format(RDFABOUT, el.tag))
            
            self.src = el.find('xmlns:entity1', ns)
            if self.src == None: raise RuntimeError('Edoal element <xmlns:entity1> required')
            elif not (self.src[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST]):
                raise NotImplementedError('Only edoal edoalEntity type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.src["edoalEntity"]))

            self.tgt = el.find('xmlns:entity2', ns)
            if self.tgt == None: raise RuntimeError('Edoal element <xmlns:entity2> required')
            elif not ((self.tgt[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST])):
                raise NotImplementedError('Only edoal edoalEntity type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.tgt[0].tag.lower()))

            rel = el.find('xmlns:relation', ns)
            if rel == None: raise RuntimeError('Edoal element <xmlns:relation> required')
            else: self.rel = Mediator.canonical(rel.text)
            
            self.tfn = []
            tfns = el.findall('xmlns:transformation', ns)
            if tfns != None: # This part of the alignment is optional.
                for tfn in tfns:
                    Tfn = tfn.find('xmlns:Transformation', ns)
                    if Tfn == None: raise RuntimeError('Edoal element <xmlns:Transformation> expected')
                    self.tfn.append({'direction': Tfn.get(EDOALDIRECTION), 'entity1': Tfn.find('xmlns:entity1', ns) , 'entity2': Tfn.find('xmlns:entity2', ns)})
            
        def render(self):
            '''
                Produce a rendering of the Correspondence as EDOAL Map
            '''
            #TODO: Produce a rendering of the Correspondence in EDOAL XML
            e1 = ''
            e2 = ''
            t = ''
            for el in self.src.iter():
                e1 += '\t' + el.tag + str(el.attrib) + '\n'
            for el in self.tgt.iter():
                e2 += '\t' + el.tag + str(el.attrib) + '\n'
            for el in self.tfn:
                t += '\t' + str(el['direction']) + '\n\tentity1: ' + str(el['entity1']) + '\n\tentity2: ' + str(el['entity2']) + '\n'
            return self.getName() + '\n>>src:' + e1 + '>>tgt:' + e2 + '>>rel:' + self.rel + '\n>>tfn:' + t
        
        def getName(self):
            return self.nme
        
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
            
            print(self.render())
            if self.rel != 'EQ':
                #TODO: Translate entity expressions LT, GT and ClassConstraints
                raise NotImplementedError('Only entity expression relations of type "EQ" supported')
            elif (len(list(self.src.iter())) > 2):
                # Classrestriction: <AttributeValueRestriction> onatt comp val </AttributeValueRestriction>
                
                if (self.src[0].tag.lower() == EDOALCLASS):
                    if (self.src[0].get(RDFABOUT) == None):
                        # Complex Boolean Class Construct found
                        raise NotImplementedError('Complex Boolean Edoal Class constructs not supported')
                    else:
                        # Simple Class Entity found; hand over to the simple entity EQ translation
                        print("Implementation required to translate {}".format(self.src[0].tag))
                        
                elif (self.src[0].tag.lower() in [EDOALCAOR, EDOALCADR, EDOALCATR, EDOALCAVR]):
                    # Complex Class Restriction found
                    
                    raise NotImplementedError('Complex Class Restriction found, under construction')
                else: raise NotImplementedError('For complex entity expressions, only class restrictions supported')
            
            elif (len(list(self.tgt.iter())) > 2):
                raise NotImplementedError('Only simple entity2 expressions supported')
            elif not ((self.src[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST]) and \
                    (self.tgt[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST])):
                raise KeyError('Only edoal entity type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.src[0].tag.lower()))
            
            # EQ relation for simple entities found. 
            # Since this is a simple entity expression, get name of src (entity1) and tgt (entity2)
            src = list(self.src.iter())[1].get(RDFABOUT)
            tgt = list(self.tgt.iter())[1].get(RDFABOUT)
#             at = AssociationGraph(edoalEntity=src, sparqlData=data)
#             print("Association graph has {} statements:".format(len(at)))
#             print ((at.serialize(format='turtle')).decode("utf-8"))
            
            # Determine the sparql context for the src, i.e., in the parsed sparql tree, determine:
            # the Node(s), their binding(s) and their constraining expression(s)
            rq = parseQuery(data)
            context = Context(edoalEntity=src, sparqlData=data)
            
            print(context.render())
            print("translating {} ---> {}".format(src, tgt))

            # Change the src into the tgt. 
            # 1 - First the concepts in the Query Pattern part of the query.
            #     The src can occur in multiple BGP's, and each qpNode represents a distinct BGP
            for qp in context.qpNodes:
                print("tgt:", tgt)
                #TODO: Namespace problem, resolve
                tgt = 'ToDoNS:'+tgt.split("#")[-1]
                print("src:", str(qp.about))
                print("tgt:", tgt)
                qp.about.updateWith(tgt)
            # 2 - Then transform the constraints from the Query Modification part of the query.
            # 2.1 - Determine the edoal spec of the transformation; ASSUME simple transformation
            for transformation in self.tfn:
                for element in list(transformation['entity1']):    # TODO: better parser for EDOAL transformations/values et.al.
                    if element.tag == EDOALAPPLY:
                        operator = element.get(EDOALOPRTR)
                        value = operator.find('edoal:arguments/edoal:Property', ns).get(RDFABOUT)
                    else: warnings.warn("Do not yet support other transformation specifications than <{}>".format(EDOALAPPLY))
            #     The src can be bound to more than one variable that can have more constraints.
            #     The qmNodes in the context is a dictionary for which the src indexes a list of variables. 
            #     Each variable is represented by a qmNode; each constraint by a valueLogic.
            
            for key in context.qmNodes:
                for qm in context.qmNodes[key]:
                    for vl in qm.valueLogic:
                        vl['operand'].updateWith('100.0')
            
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
        Calulates the length of the Mediator as the amount of Correspondences it contains.
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


