'''
Created on 26 feb. 2016

@author: brandtp
'''

# from EdoalParser.alignment import Alignment
from sparqlparser.grammar import *
import xml.etree.cElementTree as ET
import warnings

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
 
EDOALCLASS = '{http://ns.inria.org/edoal/1.0/#}class'
EDOALRELN = '{http://ns.inria.org/edoal/1.0/#}relation'
EDOALPROP = '{http://ns.inria.org/edoal/1.0/#}property'
EDOALINST = '{http://ns.inria.org/edoal/1.0/#}instance'
RDFABOUT = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'

ns = {
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'xmlns': 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
        'base': 'http://oms.omwg.org/wine-vin/',
        'dc': 'http://purl.org/dc/elements/1.1/',
#         'wine': 'http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#',
#         'vin': 'http://ontology.deri.org/vin#',
        'edoal': 'http://ns.inria.org/edoal/1.0/#'
    }
    
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
            - .src: (elementtree Element) : the source entity expression
            - .tgt: (elementtree Element) : the target entity expression
            - .rel: (string) : the EDOAL entity expression relation
            ''' 
            self.nme = el.get(RDFABOUT)
            if self.nme == None: raise ValueError('XML attribute {} expected in element {}'.format(RDFABOUT, el.tag))
            
            self.src = el.find('xmlns:entity1', ns)
            if self.src == None: raise RuntimeError('Edoal element <xmlns:entity1> required')
            elif not ((self.src[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST])):
                raise NotImplementedError('Only edoal entity type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.src[0].tag.lower()))

            self.tgt = el.find('xmlns:entity2', ns)
            if self.tgt == None: raise RuntimeError('Edoal element <xmlns:entity2> required')
            elif not ((self.tgt[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST])):
                raise NotImplementedError('Only edoal entity type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.tgt[0].tag.lower()))

            rel = el.find('xmlns:relation', ns)
            if rel == None: raise RuntimeError('Edoal element <xmlns:relation> required')
            else: self.rel = Mediator.canonical(rel.text)
            
        def render(self):
            '''
                Produce a rendering of the Correspondence as EDOAL Map
            '''
            #TODO: Produce a rendering of the Correspondence in EDOAL XML
            e1 = ''
            e2 = ''
            for el in self.src.iter():
                e1 += '\t' + el.tag + str(el.attrib) + '\n'
            for el in self.tgt.iter():
                e2 += '\t' + el.tag + str(el.attrib) + '\n'
            return self.getName() + '\n>>src:' + e1 + '>>tgt:' + e2 + '>>rel:' + self.rel
        
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
            
            if self.rel != 'EQ':
                #TODO: Translate entity expressions LT, GT and ClassConstraints
                raise NotImplementedError('Only entity expression relations of type "EQ" supported')
            elif (len(list(self.src.iter())) > 2):
                raise NotImplementedError('Only simple entity expressions supported')
            elif (len(list(self.tgt.iter())) > 2):
                raise NotImplementedError('Only simple entity expressions supported')
            elif not ((self.src[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST]) and \
                    (self.tgt[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST])):
                raise KeyError('Only edoal entity type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.src[0].tag.lower()))
            
        
            src = '<'+ list(self.src.iter())[1].get(RDFABOUT) + '>'
            tgt = '<'+ list(self.tgt.iter())[1].get(RDFABOUT) + '>'
            
            r = ParseQuery(data)
            q = r.searchElements(label='iriref', element_type=IRIREF, value=src)
            if q == []:
                warnings.warn('Cannot find {} as "iriref" in query: {}'.format(src, r.render()))
            else: q[0].updateWith(tgt)
            return r.render()
    
    def __init__(self, edoal):
        '''
        The Mediator can be initialized with an EDOAL alignment.  
        - edoal : edoal expression, represented as ET.Element
                
        The mediator represents one complete EDOAL Alignment, as follows:
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
            align = edoal.find('xmlns:Alignment', ns)
            
        if align == None: 
            raise RuntimeError('Cannot find required "xmlns:Alignment" element in XML-tree')
        else: t = align.get(RDFABOUT, default='')
        
        if (t == '') or (t == None): 
            raise ValueError('Alignment id as {} attribute expected'.format(RDFABOUT))
        else: self.about = t
        
        t = align.find('xmlns:level', ns)
        if t == None: raise RuntimeError('No alignment <level> element found in Alignment {}'.format(self.about))
        else: self.level = t.text
        if self.level != '2EDOAL': 
            raise NotImplementedError('Alignment level other than "2EDOAL" not supported; found {}'.format(self.level))
                
        self.creator = align.find('dc:creator', ns)
        self.date = align.find('dc:date', ns)
        self.method = align.find('xmlns:method', ns)
        self.purpose = align.find('xmlns:purpose', ns)
        t = align.find('xmlns:type', ns)
        
        if t == None: raise RuntimeError('Edoal element <xmlns:type> required; found {}'.format(t))
        else: self.type = t.text
        if not self.type in ['**', '?*', '*?', '??']:
            raise ValueError('Incorrect value of element <xmlns:type> required, Expected {}, found {}'.format('**, ?*, *?, ??', self.type))
        self.onto1 = align.find('xmlns:onto1', ns)
        self.onto2 = align.find('xmlns:onto2', ns)
        self.corrs = {}
        
        cells = align.findall('xmlns:map/xmlns:Cell', ns)

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
        return self.getName() + ' (onto1: ' + self.onto1.find('xmlns:Ontology', ns).get(RDFABOUT) + \
            ' onto2: ' + self.onto2.find('xmlns:Ontology', ns).get(RDFABOUT) + ')'
    
if __name__ == '__main__':
    print('running main')


    data = '''
        SELECT ?v WHERE 
    {
         ?v <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/TR/2003/CR-owl-guide-20030818/wine#VintageYear> .
    }
    '''
    
    with open("../test/resources/wine2_align.xml", 'r') as f:
        rdf = ET.parse(f)
    root = rdf.getroot()
    m = Mediator(root)
    print('len(m):', len(m))
    for nm in m.corrs:
        print(data)
        print(m.corrs[nm])
        try:
            print(m.corrs[nm].translate(data))
        except: print('no translation')
   
        
