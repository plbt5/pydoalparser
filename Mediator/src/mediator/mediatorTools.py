'''
Created on 18 apr. 2016

@author: brandtp
'''

from utilities.namespaces import NSManager
from mediator.sparqlTools import Context
from transformations import unitconversion
import os.path



#TODO: Remove tight coupling - create x-ref (in EDOALparser) between EDOAL and MEDIATOR constants

from parsertools.parsers import sparqlparser
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


class _EntityConstruction():
    '''
    Superclass, representing an operator on entities to construct complex entities, e.g., and, or, not, union, etc.
    '''
    SQRSUBOF  = chr(8849)   # Square subset of
    SQRSUPOF  = chr(8850)   # Square superset of
    SQRINTSCT = chr(8851)   # Square intersection
    SQRUNION  = chr(8852)   # Square union
    SQRMBROF  = chr(8959)   # Square contains as member
    SQRELOF   = chr(8960)   # Square element of
    NOTSYMBOL = chr(172)    # Not symbol
    
    def __init__(self, constr_type=None, constr_entities=None, ent_type=None):
        assert ent_type in [ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['CLASS'], ParseAlignment.EDOAL['RELN'], ParseAlignment.EDOAL['INST']], \
            "Entity type out of range: Got {}".format(ent_type)
        assert constr_type in [self.SQRINTSCT, self.SQRUNION, self.NOTSYMBOL], \
            "Construction type out of range: Got {}".format(constr_type)
        self.setType(constr_type)
        self.setEntType(ent_type)
        self._entities = []
        if constr_entities != None:
            if constr_type in [self.SQRINTSCT, self.SQRUNION]:
                # Found binary construction 
                assert isinstance(constr_entities, list) and len(constr_entities) == 2, \
                    "Cannot create '{}' with other than 2 entities (although it would remove the recursion), got {}.".format(constr_type, len(constr_entities))
                assert (isinstance(constr_entities[0], _Entity) or isinstance(constr_entities[0], _EntityConstruction)) and \
                    (isinstance(constr_entities[1], _Entity) or isinstance(constr_entities[1], _EntityConstruction)), \
                    "Can only create '{}' between Entity's and/or EntityConstruction's, got {} and {}".format(constr_type, type(constr_entities[0]), type(constr_entities[1]))
                assert constr_entities[0].getType() == constr_entities[1].getType(), \
                    "Cannot create '{}' between two different entity-types, got {} and {}".format(constr_type, constr_entities[0].getType(), constr_entities[1].getType())
                assert constr_entities[0].getType() != ParseAlignment.EDOAL['INST'] and constr_entities[1].getType() != ParseAlignment.EDOAL['INST'], \
                    "Cannot create {} with Instance(s) ({} and/or {})".format(constr_type.encode('utf8'), constr_entities[0].getType(), constr_entities[1].getType())
                # Add both entities
                for iri in constr_entities:
                    self.addEntity(iri)
            elif constr_type in [self.NOTSYMBOL]:
                # Found unary construction 
                if isinstance(constr_entities, list):
                    assert len(constr_entities) == 1, "Negation expects single entity only, got {}".format(len(constr_entities))
                    assert isinstance(constr_entities[0], _Entity) or isinstance(constr_entities[0], _EntityConstruction), \
                        "Negation expects single entity of type Entity or EntityConstruction only, got '{}'".format(type(constr_entities[0]))
                    self.addEntity(constr_entities[0])
                else: 
                    assert isinstance(constr_entities, _Entity) or isinstance(constr_entities, _EntityConstruction),\
                        "Negation expects single entity of type Entity or EntityConstruction only, got '{}'".format(type(constr_entities))
                    self.addEntity(constr_entities)
            else: raise RuntimeError("Illegal construction type ({})".format(constr_type))

    def setType(self, constr_type=None):
        assert constr_type in [self.SQRINTSCT, self.SQRUNION, self.NOTSYMBOL, 'dom', 'range'], \
            "Construction type out of range: Got {}".format(constr_type)
        self._type = constr_type

    def setEntType(self, entity_type=None):
        assert entity_type in [ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['CLASS'], ParseAlignment.EDOAL['RELN'], ParseAlignment.EDOAL['INST']], \
            "Entity_type out of range: Got {}".format(entity_type)
        self._entType = entity_type
    
    def addEntity(self, entity_iri=None):
        assert isinstance(entity_iri, _Entity) and entity_iri != "", "Cannot add entity to entity construction that has empty iri"
        assert len(self.getEntities()) < 2, "Entity constructions with more than 2 entities are not allowed (although it would remove recursion)"
        assert NSManager.isIRI(entity_iri.getIriRef()), "Cannot add invalid iri as entity to entity construction, got {}".format(entity_iri.getIriRef())
        self._entities.append(entity_iri)
        
    def getEntities(self):
        return self._entities
    def getEntType(self):
        return self._entType
    def getType(self):
        return self._type
    
    

from mediator.EDOALparser import ParseAlignment
class _Entity():
    '''
    Superclass, representing a single entity, i.e., a Class, Property, Relation, Instance. As BNF:
    <E>  ::= 'Class' | 'Property' | 'Relation' | 'Instance'
    '''
    def __init__(self, entity_iri=None, entity_type=None, nsMgr=None):
        '''
        Contains: 
        * _iriref:     the entity value, which always represents an iri
        * _type:    the entity type, i.e., one out of: 
            ParseAlignment.EDOAL['PROP'], 
            ParseAlignment.EDOAL['CLASS'], 
            ParseAlignment.EDOAL['RELN'], 
            ParseAlignment.EDOAL['INST']
        '''
        assert isinstance(entity_iri, str) and entity_iri != "", "Cannot create entity from empty iri"
        assert entity_type in [ParseAlignment.EDOAL['PROP'], ParseAlignment.EDOAL['CLASS'], ParseAlignment.EDOAL['RELN'], ParseAlignment.EDOAL['INST']], \
            "Entity_type out of range: Got {}".format(entity_type)
        self._iriref = nsMgr.asIRI(entity_iri)
        self._type = entity_type

    def getIriRef(self):
        return self._iriref
    
    def getType(self):
        return self._type
        
    def __str__(self):
        return self.getIriRef() + ' (' + self.getType() +')'

class EClass(_Entity):
    def __init__(self, entity_iri=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string that cannot be turned into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=ParseAlignment.EDOAL['CLASS'])
 
class EProperty(_Entity):
    def __init__(self, entity_iri=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string and cannot turn that into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=ParseAlignment.EDOAL['PROP'])

class ERelation(_Entity):
    def __init__(self, entity_iri=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string and cannot turn that into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=ParseAlignment.EDOAL['RELN'])

class EInstance(_Entity):
    def __init__(self, entity_iri=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string and cannot turn that into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=ParseAlignment.EDOAL['INST'])

class Transformation():
    '''
    A transformation specification contains all information that pertains to the creation of a function. Currently, only python functions can be supported.
    '''
    def __init__(self, python_module=None, method_name=None, operands=None, condition=None):
        '''
        A transformation specification contains:
        1. pmodule: (module) the python module that contains the function
        2. fname: (string) the name of the method/function that is to be called
        3. operands[]: a list of operands
        4. condition(): a boolean function that returns true when all conditions are met that guarantee a valid environment for the function to be executed.
        '''
#         assert isinstance(condition, function), "Cannot instantiate python function without accessible python module"
        #TODO: (jeroen) determine how to assert for callable method
        
        if python_module and method_name: self.registerPyMethod(python_module=python_module, method_name=method_name)
        else:
            self._pmodule = ''
            self._mname = ''
            
        if operands: self.registerOperands(operands)
        else: self._operands = []
        
        self.setCondition(condition=condition)
    
    def registerPyMethod(self, python_module=None, method_name=None):
        '''
        Register the python module and method for this function.
        '''
        assert isinstance(python_module, str), "Cannot instantiate python function without a specified python module"
        assert os.path.isfile('../transformations/' + python_module + '.py'), \
            "Cannot find specified python module '{}' in lib '{}'".format(python_module, 'transformations/')
        assert isinstance(method_name, str), "Cannot instantiate python function without a specified python method"
        assert method_name in dir(unitconversion), \
            "Cannot find specified method '{}' in python module '{}'".format(method_name, python_module)
        
        if python_module == 'unitconversion': self._pmodule = unitconversion
        else: self._pmodule = None
        self._mname = method_name
    
    def registerOperands(self, operands=None):
        '''
        Register the operands
        '''
        assert isinstance(operands, list), "Cannot instantiate python function without accessible list of operands"
        self._operands = operands

    def setCondition(self, condition=None):
        if condition: self._condition = condition
        else: self._condition = lambda x: True

    def makeTransform(self, result):
        '''
        Factory to create a transformation function.  
        '''
        def transform(self, value_logic_node):
            '''
            Transform a sparql ValueLogic node according to the specified operation, but only when the specified condition is met. 
            Otherwise, return None
            '''
            #TODO: include translation from source entity_iriref to target entity_iriref (result) 
            assert isinstance(value_logic_node, ParseStruct)
            if self._condition(value_logic_node):
                # Get all values that are necessary to perform the transformation
                values = []
                for operand in self._operands:
                    
                    if operand.isLiteral():
                        val, val_type = operand.getLiteral()
                        values.append(val)
                    elif operand.isIndividual() or operand.isAttrExpression():
                        # Find the value that belongs to this iriref in the value_logic node
                        nodes = value_logic_node.searchElements(element_type=operand)
                        print("="*20)
                        print("WARNING - Here Be Dragons\n\t Unexploited territory")
                        print("="*20)
                        values.append(operand.getAttrExpression())
                    elif operand.isComputable():
                        raise NotImplementedError("Cannot handle processing of recursive operation definitions (yet, please implement).")
                    else: raise RuntimeError("This should be dead code, apparently it isn't; got {} unexpectedly".format(operand.getEntityType()))

                    
                    if operand.isLiteral():
                        nodes = value_logic_node.searchElements(element_type=operand)
                    if nodes == []: raise RuntimeError("Cannot find the operand [{}] to transform".format(operand))
                    for node in nodes:
                        for itemValue in node.getItems():
                            if operand in [sparqlparser.DECIMAL, sparqlparser.INTEGER, sparqlparser.DOUBLE]:
                                value = float(itemValue)
                            else: value = str(itemValue)
                            values.append(value)
                
                # Assure that we have precisely sufficient arguments
                assert len(self._operands) == len(values), "Cannot perform operation: expected {} arguments, got {}.".format(len(self._operands), len(values))
                # Call the actual function with the found values as its arguments 
                resultValue = getattr(self.getModule(), self.getMethod())(*values)
                return resultValue
            else: return None
            
        self.transform = transform
            
class Union(_EntityConstruction):
    def __init__(self, ee1=None, ee2=None):
        assert ee1 != None
        super().__init__(constr_type=_EntityConstruction.SQRUNION, constr_entities=[ee1, ee2], ent_type=ee1.getType())
        
    def __str__(self):
        return '( {} {} {} )'.format(self.getEntities()[0], _EntityConstruction.SQRUNION.encode('utf8'), self.getEntities()[1])
 
class Intersection(_EntityConstruction):
    def __init__(self, ee1=None, ee2=None):
        super().__init__(constr_type=_EntityConstruction.SQRINTSCT, constr_entities=[ee1, ee2], ent_type=ee1.getType())
        
    def __str__(self):
        return '( {} {} {} )'.format(self.getEntities()[0], _EntityConstruction.SQRINTSCT.encode('utf8'), self.getEntities()[1])

class Neg(_EntityConstruction):
    def __init__(self, ee1=None):
        super().__init__(constr_type=_EntityConstruction.NOTSYMBOL, constr_entities=ee1, ent_type=ee1.getType())
        
    def __str__(self):
        return '( {}{} )'.format(_EntityConstruction.NOTSYMBOL.encode('utf8'), self.getEntities()[0])

class Dom(_EntityConstruction):
    def __init__(self, ee1=None):
        assert isinstance(ee1, _Entity) or isinstance(ee1, _EntityConstruction), \
            "Cannot establish the domain of entities of type {}".format(type(ee1))
        assert not ee1.getType() in [ParseAlignment.EDOAL['INST'], ParseAlignment.EDOAL['CLASS']], "Cannot establish the domain of {}".format(ee1.getType())
        super().__init__(constr_type='dom', constr_entities=ee1, ent_type=ee1.getType())
        
    def __str__(self):
        return ' dom( {} )'.format(self.getEntities()[0])

class Range(_EntityConstruction):
    def __init__(self, ee1=None):
        assert isinstance(ee1, _Entity) or isinstance(ee1, _EntityConstruction), \
            "Cannot establish the range of entities of type {}".format(type(ee1))
        assert not type(ee1) in [ParseAlignment.EDOAL['INST'], ParseAlignment.EDOAL['CLASS']], "Cannot establish the range of {}".format(type(ee1))
        super().__init__(constr_type='range', constr_entities=ee1, ent_type=ee1.getType())
        
    def __str__(self):
        return ' range( {} )'.format(self.getEntities()[0])

    
class EntityExpression(_Entity, _EntityConstruction):
    '''
    An Entity Expression represents a construction of entities. In terms of an BNF:
    <EE> ::= <E> | <EC> 
    <EC> ::= 'Union' <EE> <EE> | 'Intersection' <EE> <EE> | 'Neg' <EE> | 'Dom' <EE> | 'Rng' <EE> | 'Inv' <EE> | 'Sym' <EE> | 'Trans' <EE> | 'Refl' <EE>
    An entity expression, therefore, can be one of:
    1. an entity, or
    2. a construction of Entity Expressions
    '''
    def __init__(self, ent_or_ent_constr=None):
        assert isinstance(ent_or_ent_constr, _Entity) or isinstance(ent_or_ent_constr, _EntityConstruction), \
            "Entity or EntityConstruction expected, got {}, cannot turn that into Entity Expression".format(type(ent_or_ent_constr))
        self._expr = ent_or_ent_constr

    def getType(self):
        return type(self._expr)
    
    def getExpression(self):
        return self._expr
    
    def __str__(self):
        return self.getExpression().__str__()

       
class Correspondence():
    '''
    A Correspondence specifies a single mapping from an entity expression in ontology A to a corresponding
    entity expression in ontology B. As such, a correspondence represents a language independent placeholder of the formal relationship that holds between 
    both entity expressions, i.e., the translation, as well as between their individuals, i.e., the transformation. The correspondence will maintain a 
    generic translation method that can be used to translate a data set conforming to ontoA, to a dataset conform ontoB. The correspondence can translate 
    in both directions, form A to B or vice versa, depending on the namespaces that is being applied by the data to translate.
    A Correspondence can only have one source and one target entity expression, one relation and one measure property, 
    though it may have several transformation and linkkey properties. (See also: http://alignapi.gforge.inria.fr/edoal.html)
    '''


    def __init__(self, *, nsMgr = None):
        '''
        A Correspondence represents the core element of an Alignment, since it specifies one of the mappings between
        the source entity_iriref expression and the target entity_iriref expression. A correspondence is a container for:
        (i) a translation between iri's, containing the two entity expressions and their relation
        (ii) an optional transformation that is to be applied to the instances of the iri's
        Each Correspondence provides for a translation method that will provide for a translation of a data instance, and the optional transformations.
        
        Typical use of a Correspondence object is that it (i) will be created by a parser, and (ii) used by a data translator.
        The information contained within its object is:
        - _name: (string)          : the name of the correspondence 
        - _ee1: (EntityExpression) : the first EntityExpression expression
        - _ee2: (EntityExpression) : the second EntityExpression expression
        - _msr: (Dict)             : the measure that is estimated to hold between the entity expressions: _msr['value'] and _msr['type']
        - _rel: (string)           : the relationship between the first and second EntityExpressions
        - _tfs: [](transform)      : (optional) List of transformations on ValueLogics 
        ''' 
        assert isinstance(nsMgr, NSManager), "Cannot create a Correspondence object without namespace manager"
        self.nsMgr = nsMgr
        self._name = None
        self._ee1 = ''
        self._ee2 = ''
        self._rel = ''
        self._msr = {}
        self._tfs = []

    def setName(self, *, name=None):
        assert isinstance(name, str) and name != '', "Cannot set a Correspondence's name without an input string"
        self._name = name
    
    def getName(self):
        return self._name        
        
    def setEE1(self, *, entity_expr=None):
        assert isinstance(entity_expr, _Entity) or isinstance(entity_expr, _EntityConstruction), \
            "First entity expression required, got {}".format(entity_expr)
        self._ee1 = EntityExpression(ent_or_ent_constr=entity_expr)
        
    def getEE1(self):
        return self._ee1
        
    def setEE2(self, *, entity_expr=None):
        assert isinstance(entity_expr, _Entity) or isinstance(entity_expr, _EntityConstruction), \
            "Second entity expression required, got {}".format(entity_expr)
        self._ee2 = EntityExpression(ent_or_ent_constr=entity_expr)
        
    def getEE2(self):
        return self._ee2   
    
    def setCorrRelation(self, *, relation=None):
        assert isinstance(relation, str) and relation in [MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI], \
            "To set a correspondence relation requires on of [{}, {}, {}, {}, {}], got '{}'".format(MEDRELEQ, MEDRELSUB, MEDRELSUP, MEDRELIN, MEDRELNI, relation)
        self._rel = relation
              
    def getCorrRelation(self):
        return self._rel  

    def setCorrMeasure(self, *, measure=None, measure_type=None):
        # Note: the measure_type is a string in iri format, representing an xsd:datatype; 
        # the measure is a string representation of its value
        assert measure!=None and measure!='' and measure_type!=None and measure_type!='', "To add a measure value to the correspondence requires a measure value and type, got {} and {}, resp.".format(measure,measure_type)
        if measure_type in [self.nsMgr.asIRI('xsd:float'), self.nsMgr.asIRI('xsd:double'), self.nsMgr.asIRI('xsd:decimal'), self.nsMgr.asIRI('xsd:integer')]:
            measure = float(measure) 
            assert measure >= 0.0 and measure <= 1.0, "Measure value should be in [0,1], got {}".format(measure)
        self._msr["value"] = measure
        self._msr["type"] = measure_type
        
    def getCorrMeasure(self):
        return self._msr["value"], self._msr["type"]
            
    def appendTransform(self, *, operands=None, operation=None, result=None):
        #TODO: JEROEN - assert isinstance(condition)
        assert isinstance(operands, list), "Adding a transformation requires operands as list, got {}".format(operands)
        assert callable(operation), "Adding a transformation requires a callable operation, got {}".format(operation)
        self._tfs.append(self.__class__.makeTransform(self, operands=operands, operation=operation, result=result))

    def getTransforms(self):
        return self._tfs
    
    def render(self):
        '''
        Produce a rendering of the Correspondence
        '''
        return self.getName() + ': '+ self.getEE1() +' --['+ self.getCorrRelation() +']--> '+ self.getEE2() 
    
    def __str__(self):
        return self.getName()
    
    
    def determineDirection(self, qTree):
        '''
        Determine the direction of the data flow, based on the namespaces of the query. That defines which
        transformation to use, and what entity expression (<entity1> or <2>) is the source and the target
        '''
        #TODO: Determine, based on the 
        assert qTree and isinstance(qTree, ParseStruct), "Parsed data required, got nothing"
        prefixDecls = qTree.searchElements(element_type=sparqlparser.PrefixDecl)
        for p in prefixDecls:
            pf, ns = str(p.prefix)[:-1], str(p.namespace)
            print("namespace: {} = {}".format(pf, ns))
        return self.getEE1(), self.getEE2()

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
        
        assert rq != [] and isinstance(rq,ParseStruct)
        
        # Determine the direction of the translation: from EE1 to EE2 or vice versa?
        srcEE, tgtEE = self.determineDirection()
        # Determine the sparql context for the source entity expression in the parsed sparql tree, determine:
        # the Node(s), their binding(s) and their constraining expression(s)
        context = Context(entity_expression=self.getEE1(), sparqlTree=rq, nsMgr=self.nsMgr)


        # Prepare the target for the translation, i.e., turn it into a pf:iri_path form
        tgt_prefix, tgt_pf_expansion, tgt_iri_path = self.nsMgr.split(self.getEE2().entity_iriref)
        tgt_prefix = tgt_prefix + ':'
        tgt_pf_expansion = '<' + tgt_pf_expansion + '>'
        tgt = tgt_prefix+tgt_iri_path
        
        # Translate ee1 into ee2. 
        # 1 - First the concepts in the Query Pattern part of the query.
        #     The ee1 can occur in multiple BGP's, and each qpNode represents a distinct BGP
        #     Besides the iri to translate, also translate the namespace of that iri
        for qpt in context.qpTriples:
            # Translate the iri
            for qpn in qpt.qptRefs:
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

            
        #     The _ee1 can be bound to more than one variable that can have more constraints.
        #     The qmNodes in the context is a dictionary for which the ee1 indexes a list of variables. 
        #     Each variable is represented by a qmNode; each constraint by a valueLogic.
        
        for var in context.constraints:
            for vc in context.constraints[var]:
                for vl in vc.valueLogics:
                    for tf in self._tfs:
                        tf(self, value_logic_node = vl)
        
        context.parsedQuery.render()
        return True



