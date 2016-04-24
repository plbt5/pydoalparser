'''
Created on 18 apr. 2016

@author: brandtp
'''

from utilities.namespaces import NSManager
from mediator.sparqlTools import Context
from rdflib import term


#TODO: Remove tight coupling - create x-ref (in EDOALparser) between EDOAL and MEDIATOR constants
from mediator.EDOALparser import ParseAlignment

from parsertools.parsers.sparqlparser import parser
from parsertools.base import ParseStruct

'''
A mediator currently can only apply <equivalence> correspondence relations between entity_iriref expressions.
The correspondence relations <subsumption> and <subsumed by> between entity_iriref expressions, and the 
correspondence relations <element of> and <encompasses> between individuals and class expressions are not 
supported yet.
'''
MEDRELEQ  = 'MREQ'
MEDRELSUB = 'MRLT'
MEDRELSUP = 'MRGT'
MEDRELIN  = 'MRIN'
MEDRELNI  = 'MRNI'
# MEDEPROP  = 'M_PROPERTY'
# MEDECLASS = 'M_CLASS'


class EntityExpression():
    def __init__(self, entity_iri='', entity_type=''):
        assert term._is_valid_uri(entity_iri), "Entity {} appears not a valid iri".format(entity_iri)
        assert entity_type in [NSManager.RDFABOUT, ParseAlignment.EDOALPROP, ParseAlignment.EDOALCLASS, ParseAlignment.EDOALINST, ParseAlignment.EDOALRELN], \
            "Entity_type out of range: Got {}".format(entity_type)
        self.entity_iriref = entity_iri
        self.entity_type = entity_type
    
    def getEntityIriRef(self):
        return self.entity_iriref
    
    def getEntityType(self):
        return self.entity_type
        
    def __str__(self):
        return self.entity_iriref + ' (' + self.entity_type +')'

       
class Correspondence():
    '''
    A Correspondence specifies a single mapping from an entity_iriref expression in ontology A to a corresponding
    entity_iriref expression in ontology B. Each correspondence provides for a transformation of sparql data that 
    is expressed in terms of ontology A, into its semantic equivalent in terms of ontology B.
    A Correspondence can only have one source and one target entity expression, one relation and one measure property, 
    though it may have several transformation and linkkey properties. (See also: http://alignapi.gforge.inria.fr/edoal.html)
    '''


    def makeTransform(self, condition, operands, operation, result):
        '''
        Factory to create a transformation function.  
        '''
        assert len(operands) == 1, "No support for more than 1 operand during value transformation (yet, please implement me), got {}".format(len(operands))
        def transform(self, value_logic_node):
            '''
            Transform a sparql ValueLogic node according to the specified operation, but only when the specified condition is met. 
            Otherwise, return None
            '''
            #TODO: include translation from source entity_iriref to target entity_iriref (result) 
            assert isinstance(value_logic_node, ParseStruct)
            if condition(value_logic_node):
                nodes = value_logic_node.searchElements(element_type=operands[0])
                if nodes == []: raise RuntimeError("Cannot find the operand [{}] to transform".format(operands))
                for node in nodes:
                    for itemValue in node.getItems():
                        if operands[0] in [parser.DECIMAL, parser.INTEGER, parser.DOUBLE]:
                            value = float(itemValue)
                        else: value = str(itemValue)
                        transfdValue = operation(value)
                        node.updateWith(str(transfdValue))
                return value_logic_node
            else: return None
            
        return transform
            
    def __init__(self, *, nsMgr = None):
        '''
        A Correspondence represents the core element of an Alignment, since it specifies one of the mappings between
        the source entity_iriref expression and the target entity_iriref expression, including the transformation that is to be applied.
        Each Correspondence provides for a translation method that will provide for a translation of a data instance.
        
        Typical use of a Correspondence object is that it (i) will be created by a parser, and (ii) used by a data translator.
        The information contained within its object is:
        - name: (string)          : the name of the correspondence 
        - src: (EntityExpression) : the source EntityExpression expression
        - tgt: (EntityExpression) : the target EntityExpression expression
        - msr: (Dict)             : the measure that is estimated to hold between the entity expressions: msr['value'] and msr['type']
        - rel: (string)           : the relationship between the source and target EntityExpressions
        - tfs: [](transform)      : (optional) List of transformations on ValueLogics 
        ''' 
        assert isinstance(nsMgr, NSManager), "Cannot create a Correspondence object without namespace manager"
        self.nsMgr = nsMgr
        #TODO: parse EDOAL transformation file
        self.name = ''
        self.src = ''
        self.tgt = ''
        self.rel = ''
        self.msr = {}
        self.tfs = []

    def setName(self, *, name=None):
        assert isinstance(name, str) and name != '', "Cannot set a Correspondence's name without an input string"
        self.name = name
    
    def getName(self):
        return self.name        
        
    def setSrcEE(self, *, src_entity=None, entity_type=None):
        assert isinstance(src_entity, str), "To set a source entity_iriref expression requires iri, got {}".format(src_entity)
        assert entity_type in [NSManager.RDFABOUT, ParseAlignment.EDOALPROP, ParseAlignment.EDOALCLASS, ParseAlignment.EDOALRELN, ParseAlignment.EDOALINST], "Setting a source entity_iriref expression requires its entity_type, got {}".format(entity_type)
        self.src = EntityExpression(src_entity, entity_type)
        
    def getSrcEE(self):
        return self.src
        
    def setTgtEE(self, *, tgt_entity=None, entity_type=None):
        assert isinstance(tgt_entity, str), "To set a source entity_iriref expression requires iri, got {}".format(tgt_entity)
        assert entity_type in [NSManager.RDFABOUT, ParseAlignment.EDOALPROP, ParseAlignment.EDOALCLASS, ParseAlignment.EDOALRELN, ParseAlignment.EDOALINST], "To set a source entity_iriref expression requires its entity_type, got {}".format(entity_type)
        self.tgt = EntityExpression(tgt_entity, entity_type)
        
    def getTgtEE(self):
        return self.tgt   
    
    def setCorrRelation(self, *, relation=None):
        assert isinstance(relation, str) and relation in [MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI], \
            "To set a correspondence relation requires on of [{}, {}, {}, {}, {}], got '{}'".format(MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI, relation)
        self.rel = relation
              
    def getCorrRelation(self):
        return self.rel  

    def setCorrMeasure(self, *, measure=None, measure_type=None):
        # Note: the measure_type is a string in iri format, representing an xsd:datatype; 
        # the measure is a string representation of its value
        assert measure!=None and measure!='' and measure_type!=None and measure_type!='', "To add a measure value to the correspondence requires a measure value and type, got {} and {}, resp.".format(measure,measure_type)
        if measure_type in [self.nsMgr.asIRI('xsd:float'), self.nsMgr.asIRI('xsd:double'), self.nsMgr.asIRI('xsd:decimal'), self.nsMgr.asIRI('xsd:integer')]:
            measure = float(measure) 
            assert measure >= 0.0 and measure <= 1.0, "Measure value should be in [0,1], got {}".format(measure)
        self.msr["value"] = measure
        self.msr["type"] = measure_type
        
    def getCorrMeasure(self):
        return self.msr["value"], self.msr["type"]
            
    def appendTransform(self, *, condition=None, operands=None, operation=None, result=None):
        #TODO: JEROEN - assert isinstance(condition)
        assert isinstance(operands, list), "Adding a transformation requires operands as list, got {}".format(operands)
        assert callable(operation), "Adding a transformation requires a callable operation, got {}".format(operation)
        self.tfs.append(self.__class__.makeTransform(self, condition=condition, operands=operands, operation=operation, result=result))

    def getTransforms(self):
        return self.tfs
    
    def render(self):
        '''
            Produce a rendering of the Correspondence as EDOAL Map
        '''
        #TODO: Produce a rendering of the Correspondence in EDOAL XML
        return self.getName() + ': '+ self.src +' --['+ self.rel +']--> '+ self.tgt 
    
    def __str__(self):
        return self.getName()
     
    def translate(self, rq):
        '''
        Translate the data according to the alignment from the Correspondence Class
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

        # Prepare the target for the translation, i.e., turn it into a pf:iri_path form
        tgt_prefix, tgt_pf_expansion, tgt_iri_path = self.nsMgr.split(self.tgt.entity_iriref)
        tgt_prefix = tgt_prefix + ':'
        tgt_pf_expansion = '<' + tgt_pf_expansion + '>'
        tgt = tgt_prefix+tgt_iri_path
        
        # Change the src into the tgt. 
        # 1 - First the concepts in the Query Pattern part of the query.
        #     The src can occur in multiple BGP's, and each qpNode represents a distinct BGP
        #     Besides the iri to translate, also translate the namespace of that iri
        for qpt in context.qpTriples:
#                 print("tgt:", self.tgt) 

            
#                 print("src:", str(qpt.represents))
#                 print("tgt:", tgt, " with {} as <{}>".format(tgt_prefix, tgt_pf_expansion))
            # Translate the iri
            for qpn in qpt.qpNodes:
                qpn.about.updateWith(tgt)
            # Translate the namespace that this iri lives in
            for epf in qpt.pfdNodes:
                #TODO: translating a [PrefixDecl] for a prefix, is only valid if ALL iri's that are referenced
                # by that namespace, are translated. This is not guaranteed a priori. Hence, the code below might break the validity of the query
#                     print('Updating [PNAME_NS]: {}={} with {}={}'.format(epf,qpt.pfdNodes[epf]['ns_iriref'],tgt_prefix,tgt_pf_expansion))
                if str(qpt.pfdNodes[epf]['node'].namespace)[1:-1] == qpt.pfdNodes[epf]['ns_iriref'] and str(qpt.pfdNodes[epf]['node'].prefix)[:-1] == epf:
                    qpt.pfdNodes[epf]['node'].prefix.updateWith(tgt_prefix)
                    qpt.pfdNodes[epf]['node'].namespace.updateWith(tgt_pf_expansion)
                elif str(qpt.pfdNodes[epf]['node'].namespace)[1:-1] == tgt_pf_expansion and str(qpt.pfdNodes[epf]['node'].prefix)[:-1] == tgt_prefix:
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



