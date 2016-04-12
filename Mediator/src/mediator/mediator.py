'''
Created on 26 feb. 2016

@author: brandtp
'''

# from EdoalParser.alignment import Alignment
from parsertools.parsers.sparqlparser import parseQuery, parser
from parsertools.base import ParseStruct
from .sparqlTools import Context
from utilities.namespaces import NSManager
import xml.etree.cElementTree as ET
import warnings
from pprint import pprint

import sys
from parsertools.base import ParseStruct
from _elementtree import Element

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


    class EntityExpression():
        def __init__(self, entity='', entity_type=''):
            assert isinstance(entity, str) and entity_type in [NSManager.RDFABOUT, NSManager.EDOALPROP], "Entity_type error out of range: Got {}".format(entity_type)
            self.entity = entity
            self.entity_type = entity_type
            
        def __str__(self):
            return self.entity + ' (' + self.entity_type +')'
 
             
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
                
        def __init__(self, *, el = None, nsMgr = None):
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
            assert isinstance(el, Element) and isinstance(nsMgr, NSManager)
            self.nsMgr = nsMgr
            #TODO: parse EDOAL xml file
            self.name = 'Mapping_Rule_0'
            self.src = Mediator.EntityExpression('{http://ds.tno.nl/ontoA/}hasTemp', NSManager.EDOALPROP)
            self.tgt = Mediator.EntityExpression('{http://ds.tno.nl/ontoB/}hasT', NSManager.EDOALPROP)
            # Refactor as in http://stackoverflow.com/a/2278496/4270160
#             self.tgt = EntityExpression('{http://ds.tno.nl/ontoB/}hasT', EDOALPROP)
#TODO: (Jeroen) Pythonic way for referring to the EDOALPROP string and canonical method
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
         
        def translate(self, rq):
            '''
            Translate the data according to the EDOAL alignment from the Correspondence Class
            - rq (ParserTools.base.ParseStruct): the data to be translated; this data can represent one out of the following
                1: a sparql query (one of: SELECT, ASK, UPDATE, DESCRIBE)
                2: a sparql result set
                3: an RDF triple or RDF graph
            returns: the translated data, in the same rendering as received
            
            As of this moment, only data of type 1 is supported, and even then only SELECT
            '''
            
            # Determine the sparql context for the src, i.e., in the parsed sparql tree, determine:
            # the Node(s), their binding(s) and their constraining expression(s)
            assert rq != [] and isinstance(rq,ParseStruct)
            context = Context(entity_expression=self.src, sparqlTree=rq, nsMgr=self.nsMgr)
            
#             context.render()
#             print("translating {} ---> {}".format(self.src, self.tgt))

            # Change the src into the tgt. 
            # 1 - First the concepts in the Query Pattern part of the query.
            #     The src can occur in multiple BGP's, and each qpNode represents a distinct BGP
            #     Besides the iri to translate, also translate the namespace of that iri
            for qpt in context.qpTriples:
#                 print("tgt:", self.tgt) 
                tgt_prefix, tgt_iri, tgt_tag = self.nsMgr.split(self.tgt.entity)
                tgt_prefix = tgt_prefix + ':'
                tgt_iri = '<' + tgt_iri + '>'
                tgt = tgt_prefix+tgt_tag
                
#                 print("src:", str(qpt.represents))
#                 print("tgt:", tgt, " with {} as <{}>".format(tgt_prefix, tgt_iri))
                # Translate the iri
                for qpn in qpt.qpNodes:
                    qpn.about.updateWith(tgt)
                # Translate the namespace that this iri lives in
                for epf in qpt.pfdNodes:
                    #TODO: translating a [PrefixDecl] for a prefix, is only valid if ALL iri's that are referenced
                    # by that namespace, are translated. This is not guaranteed a priori. Hence, the code below might break the validity of the query
#                     print('Updating [PNAME_NS]: {}={} with {}={}'.format(epf,qpt.pfdNodes[epf]['ns_iriref'],tgt_prefix,tgt_iri))
                    if str(qpt.pfdNodes[epf]['node'].namespace)[1:-1] == qpt.pfdNodes[epf]['ns_iriref'] and str(qpt.pfdNodes[epf]['node'].prefix)[:-1] == epf:
                        qpt.pfdNodes[epf]['node'].prefix.updateWith(tgt_prefix)
                        qpt.pfdNodes[epf]['node'].namespace.updateWith(tgt_iri)
                    elif str(qpt.pfdNodes[epf]['node'].namespace)[1:-1] == tgt_iri and str(qpt.pfdNodes[epf]['node'].prefix)[:-1] == tgt_prefix:
                        # Already updated this [PNAME_NS] by an earlier entity_expression in the same namespace
                        pass
                    else: raise KeyError("Expected ({},{}), got ({},{})".format(epf, qpt.pfdNodes[epf]['ns_iriref'], qpt.pfdNodes[epf]['node'].prefix, qpt.pfdNodes[epf]['node'].namespace))
            
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

   
    def __init__(self):
        '''
        The mediator represents one complete EDOAL Alignment, as follows:
            self.nsMgr   ::== an rdflib NamespaceManager that can keep track of the namespaces in use
                                and can convert between prefix and qnames
            self.about   ::== string
            self.creator ::== xml.etree.Element
            self.date    ::== xml.etree.Element
            self.method  ::== xml.etree.Element
            self.purpose ::== xml.etree.Element
            self.level   ::== string
            self.type    ::== string
            self.onto1   ::== xml.etree.Element
            self.onto2   ::== xml.etree.Element
            self.corrs   ::== Dictionary of Correspondences, indexed by name
        '''

        mediatorNSs = { 'med'   : 'http://ds.tno.nl/mediator/1.0/',
                        'dc'    : 'http://purl.org/dc/elements/1.1/',
                        'edoal' : 'http://ns.inria.org/edoal/1.0/#'
                         }
        self.nsMgr = NSManager(nsDict=mediatorNSs, base='http://knowledgeweb.semanticweb.org/heterogeneity/alignment#')

        self.about   = ''
        self.creator = None
        self.date    = None
        self.method  = None
        self.purpose = None
        self.level   = ''
        self.type    = ''
        self.onto1   = None
        self.onto2   = None
        self.corrs   = {}
        
        
    def getNSs(self):
        result = ''
        for ns in self.nsMgr.namespaces():
            result += ns
        return(result)
        
    def parseEDOAL(self, edoal):
        '''
        The Mediator requires an alignment. To that end it currently parses an EDOAL alignment.  
        Input: 
        - edoal : ( xml.etree.cElementTree.Element ): an edoal expression 
        '''
        #TODO: Consider other EDOAL levels than 2EDOAL only
        #TODO: Consider other alignments than EDOAL only, e.g., SPIN
        assert (edoal != None) and (isinstance(edoal, ET.Element))

                    
        mediatorLabels = {
                'appearsAs' : 'AppearsAs',
                'binds'     : 'BINDS',
                'represents': 'REPR',
                'object'    : 'OBJ',
                'property'  : 'PROP',
                'subject'   : 'SUBJ',
                'criterion' : 'CRTN',
                'operation' : 'OPRTN',
                'limit'     : 'LMT',
                'binding'   : 'BNDNG'
                }
        

        # Get the Alignment
        align = edoal.find(NSManager.ALIGNMENT)
        
        if align == None: 
            raise RuntimeError('Cannot find required {} element in XML-tree'.format(NSManager.ALIGNMENT))
        else: t = align.get(NSManager.RDFABOUT, default='')
        
        if (t == '') or (t == None): 
            raise ValueError('Alignment id as {} attribute expected'.format(NSManager.RDFABOUT))
        else: self.about = t
        
        t = align.find(str(self.nsMgr.asClarks(':level')))
        if t == None: raise RuntimeError('No alignment <level> element found in Alignment {}'.format(self.about))
        else: self.level = t.text
        if self.level != '2EDOAL': 
            raise NotImplementedError('Alignment level other than "2EDOAL" not supported; found {}'.format(self.level))
                
        self.creator = align.find(str(self.nsMgr.asClarks('dc:creator')))
        self.date = align.find(str(self.nsMgr.asClarks('dc:date')))
        self.method = align.find(str(self.nsMgr.asClarks(':method')))
        self.purpose = align.find(str(self.nsMgr.asClarks(':purpose')))
        t = align.find(str(self.nsMgr.asClarks(':type')))
        
        if t == None: raise RuntimeError('Edoal element <xmlns:type> required; found {}'.format(t))
        else: self.type = t.text
        if not self.type in ['**', '?*', '*?', '??']:
            raise ValueError('Incorrect value of element <:type> required, Expected {}, found {}'.format('**, ?*, *?, ??', self.type))
        self.onto1 = align.find(str(self.nsMgr.asClarks(':onto1')))
        self.onto2 = align.find(str(self.nsMgr.asClarks(':onto2')))
        
        cells = align.findall(self.nsMgr.asClarks(':map') + '/' + self.nsMgr.asClarks(':Cell'))

#         print('#cells', len(cells))
        if len(cells) == 0:
            raise RuntimeError('An Edoal alignment requires at least one <xmlns:map><xmlns:Cell>...</xmlns:Cell></xmlns:map> element, but zero found')
        for el in cells:
            c = self.Correspondence(el=el, nsMgr=self.nsMgr)
            self.corrs[c.getName()] = c
            
    def translate(self,data):
        '''
        Translate the data according to the EDOAL alignment cells that are stored in correspondence objects
        - data (sparql query as string): the data to be translated; this data can represent one out of the following
            1: a sparql query (one of: SELECT, ASK, UPDATE, DESCRIBE)
            2: a sparql result set
            3: an RDF triple or RDF graph
        returns: the translated data, in the same rendering as received
        
        As of this moment, only data of type 1 is supported, and even then only SELECT
        '''
        # Process:
        # 1 - parse sparlq data
        # 2 - add namespaces that are used in the sparql query to the namespaceManager
        # 3 - translate the query, by changing, in place of the query, the iri's and data values as 
        #     specified in the correspondences
        assert data != None and data != '' and isinstance(data, str)
        rq = parseQuery(data)
        if rq == []:
            raise RuntimeError("Couldn't parse the following query:\n{}".format(data))
        self.nsMgr.bindPrefixesFrom(rq)
        rq.render()
        for nm in self.corrs:
#             print(self.corrs[nm])
            print(self.corrs[nm].translate(rq))
            
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
        return self.getName() + ' (onto1: ' + self.onto1.find(str(self.nsMgr.asClarks('xmlns:Ontology'))).get(str(self.nsMgr.asClarks('rdf:about'))) + \
            ' onto2: ' + self.onto2.find(str(self.nsMgr.asClarks('xmlns:Ontology'))).get(str(self.nsMgr.asClarks('rdf:about'))) + ')'
    
if __name__ == '__main__':
    print('running main')


