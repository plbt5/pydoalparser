'''
Created on 18 apr. 2016

@author: brandtp
'''

from utilities.namespaces import NSManager

from transformations import unitconversion
import os.path
import warnings


#TODO: Remove tight coupling - create x-ref (in EDOALparser) between EDOAL and MEDIATOR constants

from parsertools.parsers import sparqlparser
from parsertools.base import ParseStruct

'''
A mediator currently can only apply <equivalence> correspondence relations between entity_expr expressions.
The correspondence relations <subsumption> and <subsumed by> between entity_expr expressions, and the 
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
    '''
    An Entity Expression represents a construction of entities. In terms of an BNF:
    <EE> ::= <E> | <EC> 
    <EC> ::= 'Union' <EE> <EE> | 'Intersection' <EE> <EE> | 'Neg' <EE> | 'Dom' <EE> | 'Rng' <EE> | 'Inv' <EE> | 'Sym' <EE> | 'Trans' <EE> | 'Refl' <EE>
    An entity expression, therefore, can be one of:
    1. an entity, or
    2. a construction of Entity Expressions
    '''
    def __init__(self, ent_or_ent_constr=None):
#         assert isinstance(ent_or_ent_constr, _Entity) or isinstance(ent_or_ent_constr, _EntityConstruction), \
#             "Entity or EntityConstruction expected, got {}, cannot turn that into Entity Expression".format(type(ent_or_ent_constr))
#         self._expr = ent_or_ent_constr
        pass

#     def getType(self):
#         print ('in EE ')
#         return type(self._expr).__name__

    def getType(self):
        return type(self)
    
    def isEntity(self):
        return type(self) == _Entity
    
    def isEntityExpression(self):
        return type(self) == _EntityConstruction


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
    
    def __init__(self, constr_type=None, ent_expressions=None, ent_type=None):
        assert ent_type in [Alignment.EDOAL['PROP'], Alignment.EDOAL['CLASS'], Alignment.EDOAL['RELN'], Alignment.EDOAL['INST']], \
            "Entity type out of range: Got {}, expected {}".format(ent_type, Alignment.EDOAL['CLASS'])
        assert constr_type in [self.SQRINTSCT, self.SQRUNION, self.NOTSYMBOL], \
            "Construction type out of range: Got {}".format(constr_type)
        self.setCType(constr_type)
        self.setEntType(ent_type)
        self._entities = []
        if ent_expressions != None:
            if constr_type in [self.SQRINTSCT, self.SQRUNION]:
                # Found binary construction 
                assert isinstance(ent_expressions, list) and len(ent_expressions) == 2, \
                    "Cannot create '{}' with other than 2 ent_expressions (although it would remove the recursion), got {}.".format(constr_type, len(ent_expressions))
                assert (isinstance(ent_expressions[0], _Entity) or isinstance(ent_expressions[0], _EntityConstruction)) and \
                    (isinstance(ent_expressions[1], _Entity) or isinstance(ent_expressions[1], _EntityConstruction)), \
                    "Can only create '{}' between Entity's and/or EntityConstruction's, got {} and {}".format(constr_type, type(ent_expressions[0]), type(ent_expressions[1]))
                assert ent_expressions[0].getType() == ent_expressions[1].getType(), \
                    "Cannot create '{}' between two different entity_expression-types, got {} and {}".format(constr_type, ent_expressions[0].getType(), ent_expressions[1].getType())
                assert ent_expressions[0].getType() != Alignment.EDOAL['INST'] and ent_expressions[1].getType() != Alignment.EDOAL['INST'], \
                    "Cannot create {} with Instance(s) ({} and/or {})".format(constr_type.encode('utf8'), ent_expressions[0].getType(), ent_expressions[1].getType())
                # Add both ent_expressions
                for ent_expr in ent_expressions:
                    self.addEntityExpr(ent_expr)
            elif constr_type in [self.NOTSYMBOL]:
                # Found unary construction 
                if isinstance(ent_expressions, list):
                    assert len(ent_expressions) == 1, "Negation expects single entity_expression only, got {}".format(len(ent_expressions))
                    assert isinstance(ent_expressions[0], _Entity) or isinstance(ent_expressions[0], _EntityConstruction), \
                        "Negation expects single entity_expression of type Entity or EntityConstruction only, got '{}'".format(type(ent_expressions[0]))
                    self.addEntityExpr(ent_expressions[0])
                else: 
                    assert isinstance(ent_expressions, _Entity) or isinstance(ent_expressions, _EntityConstruction),\
                        "Negation expects single entity_expression of type Entity or EntityConstruction only, got '{}'".format(type(ent_expressions))
                    self.addEntityExpr(ent_expressions)
            else: raise RuntimeError("Illegal construction type ({})".format(constr_type))
    
    def setCType(self, constr_type=None):
        assert constr_type in [self.SQRINTSCT, self.SQRUNION, self.NOTSYMBOL, 'dom', 'range'], \
            "Construction type out of range: Got {}".format(constr_type)
        self._type = constr_type

    def setEntType(self, entity_type=None):
        #TODO: Remove the dependency on the Alignment.EDOAL entity types, and create own types
        assert entity_type in [Alignment.EDOAL['PROP'], Alignment.EDOAL['CLASS'], Alignment.EDOAL['RELN'], Alignment.EDOAL['INST']], \
            "Entity_type out of range: Got {}".format(entity_type)
        self._entType = entity_type
    
    def addEntityExpr(self, ent_expr=None):
        assert isinstance(ent_expr, EntityExpression) and ent_expr != "", "Entity expression expected, got {}".format(type(ent_expr))
        assert len(self.getEntities()) < 2, "Entity constructions containing more than 2 entity expressions are not allowed (although it would remove recursion)"
        assert NSManager.isIRI(ent_expr.getIriRef()), "Cannot add invalid iri as ent_expr to ent_expr construction, got {}".format(ent_expr.getIriRef())
        self._entities.append(ent_expr)
            
#     def getExpression(self):
#         return self._expr

    def getEntities(self):
        return self._entities
    def getEntType(self):
        return self._entType
    def getCType(self):
        return self._type
  

class Union(_EntityConstruction):
    def __init__(self, ee1=None, ee2=None):
        assert ee1 != None
        super().__init__(constr_type=_EntityConstruction.SQRUNION, ent_expressions=[ee1, ee2], ent_type=ee1.getType())
        
    def __str__(self):
        return '( {} {} {} )'.format(self.getEntities()[0], _EntityConstruction.SQRUNION.encode('utf8'), self.getEntities()[1])
 
class Intersection(_EntityConstruction):
    def __init__(self, ee1=None, ee2=None):
        super().__init__(constr_type=_EntityConstruction.SQRINTSCT, ent_expressions=[ee1, ee2], ent_type=ee1.getType())
        
    def __str__(self):
        return '( {} {} {} )'.format(self.getEntities()[0], _EntityConstruction.SQRINTSCT.encode('utf8'), self.getEntities()[1])

class Neg(_EntityConstruction):
    def __init__(self, ee1=None):
        super().__init__(constr_type=_EntityConstruction.NOTSYMBOL, ent_expressions=ee1, ent_type=ee1.getType())
        
    def __str__(self):
        return '( {}{} )'.format(_EntityConstruction.NOTSYMBOL.encode('utf8'), self.getEntities()[0])

class Dom(_EntityConstruction):
    def __init__(self, ee1=None):
        assert isinstance(ee1, _Entity) or isinstance(ee1, _EntityConstruction), \
            "Cannot establish the domain of entities of type {}".format(type(ee1))
        assert not ee1.getType() in [Alignment.EDOAL['INST'], Alignment.EDOAL['CLASS']], "Cannot establish the domain of {}".format(ee1.getType())
        super().__init__(constr_type='dom', ent_expressions=ee1, ent_type=ee1.getType())
        
    def __str__(self):
        return ' dom( {} )'.format(self.getEntities()[0])

class Range(_EntityConstruction):
    def __init__(self, ee1=None):
        assert isinstance(ee1, _Entity) or isinstance(ee1, _EntityConstruction), \
            "Cannot establish the range of entities of type {}".format(type(ee1))
        assert not type(ee1) in [Alignment.EDOAL['INST'], Alignment.EDOAL['CLASS']], "Cannot establish the range of {}".format(type(ee1))
        super().__init__(constr_type='range', ent_expressions=ee1, ent_type=ee1.getType())
        
    def __str__(self):
        return ' range( {} )'.format(self.getEntities()[0])


from mediator.EDOALparser import Alignment
class _Entity(EntityExpression):
    '''
    Superclass, representing a single entity, i.e., a Class, Property, Relation, Instance. As BNF:
    <E>  ::= 'Class' | 'Property' | 'Relation' | 'Instance'
    '''
    def __init__(self, entity_iri=None, entity_type=None, nsMgr=None):
        '''
        Contains: 
        * _iriref:     the entity_expression value, which always represents an iri
        * _type:    the entity_expression type, i.e., one out of: 
            Alignment.EDOAL['PROP'], 
            Alignment.EDOAL['CLASS'], 
            Alignment.EDOAL['RELN'], 
            Alignment.EDOAL['INST']
        '''
        assert isinstance(entity_iri, str) and entity_iri != "", "Cannot create entity_expression from empty iri"
        assert isinstance(nsMgr, NSManager), "Requires a valid namespace mgr, got None"
        assert entity_type in [Alignment.EDOAL['PROP'], Alignment.EDOAL['CLASS'], Alignment.EDOAL['RELN'], Alignment.EDOAL['INST']], \
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
    def __init__(self, entity_iri=None, nsMgr=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string that cannot be turned into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=Alignment.EDOAL['CLASS'], nsMgr=nsMgr)
 
class EProperty(_Entity):
    def __init__(self, entity_iri=None, nsMgr=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string and cannot turn that into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=Alignment.EDOAL['PROP'], nsMgr=nsMgr)

class ERelation(_Entity):
    def __init__(self, entity_iri=None, nsMgr=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string and cannot turn that into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=Alignment.EDOAL['RELN'], nsMgr=nsMgr)

class EInstance(_Entity):
    def __init__(self, entity_iri=None, nsMgr=None):
        assert isinstance(entity_iri, str), "String expected, got {}, cannot turn that into valid IRI".format(type(entity_iri))
        assert entity_iri != '', "Value expected, got empty string and cannot turn that into valid IRI."
        super().__init__(entity_iri=entity_iri, entity_type=Alignment.EDOAL['INST'], nsMgr=nsMgr)


class Path(list):
    '''
    A Path represents a concatenation of zero or more atomic relations, with an optional final property. The purpose of the path is to be able to navigate to 
    either a property or a Range in the source ontology. For the resulting destination a constraint can then be defined.
    Refer to [KnowledgeWeb, D2.2.10, Expressive alignment language and implementation, formula 2.17 & 2.18], where 'Q' indicates a path, and 'r', 'p'
    a relation and property, respectively.
    Q  ::= Q' | p | Q'.p
    Q' ::= empty | r | Q'.r
    '''
    
    def __init__(self, *args):
        '''
        A path is implemented as a list of relations, possibly empty, and optionally a single property as final element.
        An empty path is similarly expressed as an empty list.
        '''
        list.__init__(self, *args)
        print("args:", args)
        if args: self._closed = isinstance(args[0], EProperty)
        else: self._closed = False
    
    def append(self, r_or_p):
        assert isinstance(r_or_p, ERelation) or isinstance(r_or_p, EProperty), "Only Relations are allowed in a path, got {}".format(type(r_or_p))
        if self._closed: raise AssertionError("Path already closed by a property ({}), cannot add other elements anymore".format(self.__getitem__(-1)))
        self._closed = isinstance(r_or_p, EProperty)
        super().append(r_or_p)
        
    def _prepend(self, r):
        assert isinstance(r, ERelation), "Only Relations can be prepended in a path, got {}".format(type(r))
        return self.insert(0, r)


class Transformation():
    '''
    A transformation is both a specification pertaining to the creation and use of a function, and, a method that can be called to perform an 
    actual transformation. Currently, only local (python) functions can be supported.
    A transformation represents one single conversion only and does not contain an inverse function, nor different functions for different 
    individuals. In terms of EDOAL, it represents a single <Transformation> clause.
    '''
    def __init__(self, python_module=None, method_name=None, operands=None, condition=None):
        '''
        Input: 
        - python_module (string): the name of the module in the lib, with or without the '.py' extension, e.g., unitconversion.py or unitconversion
        - method_name (string): the name of the method in the unitconversion that should be called when executing the transformation, e.g., TempConvertor
        - operands (list of Alignment.Value): the values that are used as operands to the transformation
        - condition (callable): a callable operation that returns True or False.
        A transformation specification contains:
        1. A callable function that performs the transformation. This function consists of:
            a: pmodule: (module) the python module that contains the function, and
            b: fname: (string) the name of the method/function that is to be called
        2. operands[]: list of Alignment.Value. Each operand is identified by its iri. The operand is related to the source entity_expression expression, 
            e.g., ontoA:TempInC ontoA:hasValue (with TempInC a Class and hasValue a Property). Consequently, in the sparql query these 
            two should be related, either directly as BGP (ontoA:TempInC ontoA:hasValue ?v) or indirectly with two BGPs with a shared variable.
        4. condition(): (Not Implementd Yet, always True) a boolean function that returns true when all conditions are met that guarantee 
            a valid environment for the function to be executed.
        5. transform(): The actual method to call in order to perform a transformation of an instance
        '''
        
        if python_module and method_name: self.registerLocalMethod(python_module=python_module, method_name=method_name)
        else:
            self._pmodule = ''
            self._mname = ''
            
        if operands: self.registerOperands(operands)
        else: self._operands = []
        
        self.setCondition(condition=condition)
        self.transform = lambda x: None
    
    def registerLocalMethod(self, python_module=None, method_name=None):
        '''
        Register the python module and method for this function.
        '''
        assert isinstance(python_module, str), "Cannot instantiate python function without a specified python module"
        mod_split = python_module.split(".")
        if len(mod_split)==1:
            python_module+= ".py"
        elif mod_split[1] != 'py': raise AssertionError("Got {}{} but can only process python operations (yet, please implement me)".format(mod_split[0], mod_split[1]))
        else: raise AttributeError("Ill-formed library module, expected module(.ext) but got {}".format(python_module))
        assert os.path.isfile(NSManager.LOCAL_BASE_PATH + 'transformations/' + python_module), \
            "Cannot find specified python module '{}{}'".format('transformations/', python_module)
        assert isinstance(method_name, str), "Cannot instantiate python function without a specified python method"
        
        if python_module == 'unitconversion.py':
            assert method_name in dir(unitconversion), \
                "Cannot find specified method '{}' in python module '{}'".format(method_name, python_module) 
            self._pmodule = unitconversion
        else: raise NotImplementedError("{} module not implemented or imported (yet, please implement me)".format(python_module))
        self._mname = method_name
    
    def getLocalMethod(self):
        return self._pmodule, self._mname
    
    def getOperationResult(self, *args,**kwargs):
        return getattr(self._pmodule, self._mname)(*args,**kwargs)
    
    def registerOperands(self, operands=None):
        '''
        Register the operands
        '''
        assert isinstance(operands, list), "Cannot register operands for python function without accessible list of operands"
        typesOfOperands = list(set([type(o) for o in operands]))
        assert len(typesOfOperands) == 1 and typesOfOperands[0] == Alignment.Value, "Cannot register operand; expected '{}', got '{}'".format(Alignment.Value, typesOfOperands[0])
        self._operands = operands

    def setCondition(self, condition=None):
        if condition: self._condition = condition
        else: self._condition = lambda x: True

    def hasValidCondition(self, *args):
        return self._condition(*args)

    def makeTransform(self, resultIRI=None):
        '''
        Factory to create a transformation function.  
        '''
        assert self._condition, "Specification of condition required before making the transform"
        assert self._pmodule and self._mname, "Specification of operation required before making the transform"
        
        def transform(var_constraints=None):
            from mediator.sparqlTools import Context
            '''
            Transform the variable constraints according to the specified operation, but only when the specified condition is met. 
            Return the resulting value on success, return None otherwise.
            '''

            #TODO: include translation from source entity_expr to target entity_expr (result) 
            assert isinstance(var_constraints, Context.VarConstraints), "Cannot perform a transformation without data args"
            # First, get all argument values that are necessary to perform the transformation
            #TODO: implement correct sequence of operands, by use of kwargs. Needs a x-ref between operands and method signature.
            args = []
            for valueLogicExpression in var_constraints.getValueLogicExpressions():
                # For each value, check whether the conditions are met that guarantee a valid transformation
#                 print("vle: {}\n\tis valid: {}".format(valueLogicExpression, self.hasValidCondition(valueLogicExpression)))
                if self.hasValidCondition(valueLogicExpression):
                    # Step 1 - Collect every necessary argument for the transformation. Every operand identifies some sort of transformation argument
                    for operand in self._operands:
                        # Establish the kind of argument that the operand represents
#                         print("operand: {}".format(operand))
                        if operand.isLiteral():
                            # A Literal *is* the argument, i.e., its actual value is the argument.
                            val, val_type = operand.getLiteral()
                            #TODO: We ignore the value type of the literal, this might increase the fault sensitivity
                            args.append(val)
                        elif operand.isAttrExpression():
                            # A Relation or Property *refer* to the argument, e.g., <edoal:Property rdf:about="&ontoB;hasTempInF" /> refers to a Property, the value
                            # of which is the argument for the transformation. Hence, find the value that belongs to the variable (in the value_logic node) that is bound by this iriref
                            # However, the relation or property might represent a path expression, hence distinguish between a path and a normal attr.expression
                            if operand.hasPath():
                                # the last element in the path is the one that bounds the variable
                                #TODO: implement path expression in the transform()
                                raise NotImplementedError("Path expression (on {}) cannot be elaborated in the Transform (yet, please implement me)".format(operand))
                            else: 
                                # Operand is a simple property or relation, hence add the value of its bound variable, IF the var_constraints's entity equals the operand
#                                 print("Comparing constraint entity ({}) with operand ({})".format(var_constraints.getEntity().getIriRef(), operand.getAttrExpression()))
                                if var_constraints.getEntity().getIriRef() == operand.getAttrExpression():
#                                     print("VLE restriction: ", valueLogicExpression['restriction'])
                                    args.append(str(valueLogicExpression['restriction']))
                                else: warnings.warn("Transform: got {} but was expecting to transform {}; ignored".format(operand.getAttrExpression, var_constraints.getEntity()))
                        elif operand.isIndividual():
                            # Instances are always single entities that refer to an individual through its URI. Find the var that belongs to this URI, and get its value
                            raise NotImplementedError("Cannot handle Individual operand ({}) definitions (yet, please implement).".format(operand))
                        elif operand.isComputable():
                            raise NotImplementedError("Cannot handle processing of recursive operation definitions (yet, please implement).")
                            #TODO: implement recursive operations, i.e., performing a secondary operation to get the value for the principle operation.
                            # The recursion call is simple, but where do we get the transformation information from? Hence, we must 
                            # refer to another transformation object, and perform its Transform() method to get the appropriate value.
                        else: raise RuntimeError("This should be dead code, apparently it isn't; got {} unexpectedly".format(operand.getEntityType()))
                        print("args: [ ", end="")
                        for arg in args: print("{} ".format(arg), end="")
                        print("]")
                    # Step 2 - Assure that we have precisely sufficient arguments
                    assert len(self._operands) == len(args), "Cannot perform operation: expected {} arguments, got {}.".format(len(self._operands), len(args))
                    # Step 3 - Call the actual function with the found values as its arguments 
                    resultValue = self.getOperationResult(*args)
                    return resultValue
    #                     if operand.isLiteral():
    #                         nodes = valueLogicExpression.searchElements(element_type=operand)
    #                     if nodes == []: raise RuntimeError("Cannot find the operand [{}] to transform".format(operand))
#                         for node in nodes:
#                             for itemValue in node.getItems():
#                                 if operand in [sparqlparser.DECIMAL, sparqlparser.INTEGER, sparqlparser.DOUBLE]:
#                                     value = float(itemValue)
#                                 else: value = str(itemValue)
#                                 args.append(value)
                else: 
                    warnings.warn("Cannot transform data because conditions for '{}' are not met".format(valueLogicExpression))
                    return None
            return None
            
        self.transform = transform
    
    def __str__(self):
        return str(self._mname)
    
    def __repr__(self):
        tf_repr="pmodule: " + str(self._pmodule) + ", method: " + str(self._mname) + " ( "
        tf_repr += str(self._operands)
        tf_repr += "), condition: " + str(self._condition) + ", function: " + str(self.transform)
        return tf_repr
        
       
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
        the source entity_expr expression and the target entity_expr expression. A correspondence is a container for:
        (i) a translation between iri's, containing the two entity_expression expressions and their relation
        (ii) an optional transformation that is to be applied to the instances of the iri's
        Each Correspondence provides for a translation method that will provide for a translation of a data instance, and the optional transformations.
        
        Typical use of a Correspondence object is that it (i) will be created by a parser, and (ii) used by a data translator.
        The information contained within its object is:
        - _name: (string)          : the name of the correspondence 
        - _ee1: (EntityExpression) : the first EntityExpression expression
        - _ee2: (EntityExpression) : the second EntityExpression expression
        - _msr: (Dict)             : the measure that is estimated to hold between the entity_expression expressions: _msr['value'] and _msr['type']
        - _rel: (string)           : the relationship between the first and second EntityExpressions
        - _tfs: [](Transformation)      : (optional) List of transformations on ValueLogics 
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
            "<entity1> entity expression required, got {}".format(entity_expr)
        self._ee1 = entity_expr
        
    def getEE1(self):
        return self._ee1
        
    def setEE2(self, *, entity_expr=None):
        assert isinstance(entity_expr, _Entity) or isinstance(entity_expr, _EntityConstruction), \
            "<entity2> entity expression required, got {}".format(entity_expr)
        self._ee2 = entity_expr
        
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
            
    def appendTransform(self, *, transformation=None, result_iri=None):
        assert isinstance(transformation, Transformation), "Expected transformation of type {}, got {}".format(Transformation, type(transformation))
        transformation.makeTransform(resultIRI=result_iri)
        self._tfs.append(transformation)

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
        from mediator.sparqlTools import Context
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
        srcEE, tgtEE = self.determineDirection(rq)
        # Determine the sparql context for the source entity expression in the parsed sparql tree, i.e., determine:
        # the Node(s), their binding(s) and their constraining expression(s)
        print("namespace: ", str(self.nsMgr))
        context = Context(entity_expression=srcEE, sparqlTree=rq, nsMgr=self.nsMgr)
        print("Created context:")
        context.render()

        # Prepare the target for the translation, i.e., turn it into a pf:iri_path form
        if tgtEE.isEntity(): raise NotImplementedError("cannot translate into an entity *expression* (yet, please implement me), got {}".format(str(tgtEE)))
        tgt_prefix, tgt_pf_expansion, tgt_iri_path = self.nsMgr.split(tgtEE.getIriRef())
        tgt_prefix = tgt_prefix + ':'
        tgt_pf_expansion = '<' + tgt_pf_expansion + '>'
        tgt = tgt_prefix+tgt_iri_path
        
        # Translate ee1 into ee2. 
        # 1 - Loop over the Query Patterns of the query, and find the concept that it addresses. Establish which of the correspondences apply to that concept.
        #     The source entity expression can occur in multiple BGP's, and each qpNode represents a distinct BGP
        #     Besides the iri to translate, also translate the namespace of that iri
        for qptAssoc in context.qptAssocs:
            # Translate the iri
            for qpn in qptAssoc.qptRefs:
                qpn.about.updateWith(tgt)
            # Translate the namespace that this iri lives in
            for epf in qptAssoc.pfdNodes:
                #TODO: translating a [PrefixDecl] for a prefix, is only valid if ALL iri's that are referenced
                # by that namespace, are translated. This is not guaranteed a priori. Hence, the code below might break the validity of the query
#                     print('Updating [PNAME_NS]: {}={} with {}={}'.format(epf,qptAssoc.pfdNodes[epf]['ns_iriref'],tgt_prefix,tgt_pf_expansion))
                if str(qptAssoc.pfdNodes[epf]['node'].namespace)[1:-1] == qptAssoc.pfdNodes[epf]['ns_iriref'] and str(qptAssoc.pfdNodes[epf]['node'].prefix)[:-1] == epf:
                    qptAssoc.pfdNodes[epf]['node'].prefix.updateWith(tgt_prefix)
                    qptAssoc.pfdNodes[epf]['node'].namespace.updateWith(tgt_pf_expansion)
                elif str(qptAssoc.pfdNodes[epf]['node'].namespace)[1:-1] == tgt_pf_expansion and str(qptAssoc.pfdNodes[epf]['node'].prefix)[:-1] == tgt_prefix:
                    # Already updated this [PNAME_NS] by an earlier entity_expression in the same namespace
                    pass
                else: raise KeyError("Expected ({},{}), got ({},{})".format(epf, qptAssoc.pfdNodes[epf]['ns_iriref'], qptAssoc.pfdNodes[epf]['node'].prefix, qptAssoc.pfdNodes[epf]['node'].namespace))
        
        # 2 - Then transform the constraints from the Query Modification part of the query.
        #     The _ee1 can be bound to more than one variable, and each variable can have more constraints.
        #     The nodes in the query modification part, i.e., the qmNodes in the context, is represented as a dictionary
        #     for which the ee1 indexes a list of variables. 
        #     Each variable is represented by a qmNode; each constraint by a valueLogic.
        
        print ("looping over vars: {}".format(context.constraints))
        for var in context.constraints:
            for vc in context.constraints[var]:
                print("var: '{}', var constraint: '{}'".format(var, vc))
                for vle in vc.getValueLogicExpressions():
                    for tf in self.getTransforms():
                        tf.transform(value_logic_expression = vle)
        
        context.parsedQuery.render()
        return True


