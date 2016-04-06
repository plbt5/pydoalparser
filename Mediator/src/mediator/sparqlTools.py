'''
Created on 22 mrt. 2016

@author: brandtp

A sparql-query is structured as follows:

    Prefix Declarations:
        BASE
        PREFIX
    Dataset Definition:
        FROM
        FROM NAMED
    Result Clause:
        SELECT
        CONSTRUCT
        DESCRIBE
        ASK
    Query Pattern:
        WHERE
    Query Modifiers:
        ORDER BY
        LIMIT
        OFFSET
        DISTINCT
        REDUCED

This module provides tools to relate the various elements of a query to each other, as well as to the EDOAL correspondences.
'''

from parsertools.parsers.sparqlparser import parseQuery, parser
# from .mediator import EntityExpression
from builtins import str
from distutils.dist import warnings
from rdflib import Namespace, URIRef, BNode, Literal
from lib2to3.pytree import Node
from parsertools.base import ParseStruct



        

class Context():
    '''
    Represents the sparql context of <entity1> that is mentioned in the EDOAL correspondence.
    It builds the relationship between:
    1 - the <entity1> and the URIRef element(s) in the Query Pattern of the sparql tree, and 
    2 - and the restrictions that yield in the Query Modifiers of the sparql tree.
    * 
    '''
    mns = Namespace('http://ds.tno.nl/mediator/1.0/')
    uris = {
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


    class QueryPatternTriple():
        
        
        class QPNode():
            
            def __init__(self, about=None):
                self.about = ''      # (ParseInfo) the atomic node in the sparql tree representing the node
                self.type = ''       # (URIRef) the Basic Graph Pattern position of the node: <S|P|O>
                self.binds = []      # (String) a list of names of two (BGPType=p) or one (=s or =o) Vars that are bound by this node: <VAR1 | VAR2 | PNAME_LN>
                self.associates = {} # (Dict(uri, ParseInfo)) the (s,p,o) triple, each element being a QPNodeother two qpNodes in the triple
                self.partOfRDF = ''  #TODO: The RDF Triple Pattern (s,p,o) (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#defn_TriplePattern)
                                     #     that this node is part of (created)
                if about == None: raise RuntimeError("Cannot create QPNode from None")
                atom = about.descend()
                if atom.isAtom():
                    self.about = atom
                else: raise NotImplementedError("Creating QPNode from non-atom node ({}) is not implemented, and considered bad practice.".format(atom))
            
            def setType(self, bgp_type=None):
                self.type = URIRef(Context.mns[Context.uris[bgp_type]])
                self.addAssociate(self.type, self.about)
                
            def addAssociate(self, bgp_type=None, assoc_node=None):
                '''
                1 - This method adds to its subject QPNode this (associated) node that is part of the QPNode's BGP (s,p,o). To that end it will find 
                the terminal or atom node in this branch, and raise an error when there are more branches down the tree. 
                2 - In conjunction to this, it also checks whether the associated node represents a sparql variable. If so, it will add the 
                variable to the binding of its subject QPNode.
                3 - TODO: when the BGP becomes complete after this last addition, it will generate an RDF triple from it and store it in its
                subject QPNode (not a triple store).
                Input: 
                * assoc_node:    The associated node, which is considered to be on a tree vertice that has no other branches. The method will throw a Runtime error
                                when there are branches found lower in the tree.
                * bgp_type:      The position of the association node in the BGP triple. This can be either a string ('subject' | 'property' | 'object'), or
                                a full blown URIRef of identical nature.
                '''
                # First figure out the bgp type
                if bgp_type == None or assoc_node == None: 
                    raise RuntimeError('Cannot add empty querypattern qpNodes')
                if type(bgp_type) is URIRef: 
                    uri = bgp_type
                elif isinstance(bgp_type, str): 
                    uri = URIRef(Context.mns[Context.uris[bgp_type]])
                else: 
                    raise RuntimeError('Cannot turn type [{}] into a URIRef'.format(type(bgp_type)))
                
                # Now find the terminal/atom of the association node
                atom = assoc_node.descend()
                if atom.isAtom():
                    # Associate it with the main Node
                    if uri in self.associates:
                        raise RuntimeError('Position of <{}> in {} already taken'.format(uri, str(self)))
                    else: 
                        self.associates[uri] = atom
                    # In addition, this might represent a variable, hence consider to store the binding
                    self.considerBinding(atom)
                else: raise NotImplementedError("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings.".format(atom))
                
#                 print('[{}] determined as <{}> associate to <{}>'.format(str(assoc_node),uri,str(self.about)))

                # Lastly, generate an RDF triple and store it in its subject QPNode
                if len(self.associates) == 3:
                    #TODO: create three RDF Terms (each as Literal, URIRef or BNode), and formulate & store it as statement
                    self.partOfRDF = (URIRef(Context.mns[Context.uris['subject']]),URIRef(Context.mns[Context.uris['property']]),URIRef(Context.mns[Context.uris['object']]))
            
            def considerBinding(self, qpnode):
                # We assume that we only need to take into consideration the variables in order to be able to follow through with the translations, hence
                # the PNAME's, i.e., iri's that are bound to this entity, are assumed to be taken care of as another EDOAL alignment map
#                 if type(qpnode).__name__ in ['VAR1', 'VAR2', 'PNAME_LN']:
                if type(qpnode).__name__ in ['VAR1', 'VAR2']:
                    if (not str(qpnode) in self.binds) and (not qpnode == self.about):
                        self.binds.append(str(qpnode))
            
            def dump(self):
                result = "node:\n\tof type   : " + str(self.type) + "\n\tabout     : " + str(self.about)
                for a in self.associates:
                    result += "\n\tassociates: " + str(self.associates[a]) + " ( " + str(a) + " )"
                for b in self.binds:
                    result += "\n\tbinds     : " + str(b)
                return(result) 
            
            def __str__(self):
                result = '( ' + \
                    str(self.associates[URIRef(Context.mns[Context.uris['subject']])]) + ', ' + \
                    str(self.associates[URIRef(Context.mns[Context.uris['property']])]) + ', ' + \
                    str(self.associates[URIRef(Context.mns[Context.uris['object']])]) + ' )'
                return(result)
            
        def __init__(self, entity_expression = None, sparql_tree=None):
#             assert isinstance(entity_expression, EntityExpression) and isinstance(sparql_tree, ParseStruct)
            self.represents = '' # (EntityExpression) the EDOAL entity (Class, Property, Relation, Instance) name;
                                 # This is in fact unnecessary because this is already stored in the higher Context class
            self.qpNodes = []    # List of (QPNode)s, i.e., implicit Query Pattern nodes that address the Entity
            self.sparqlTree = '' # The sparql tree that this class uses to relate to
            
            # Now find the atom of the main Node, i.e., what this is all about, and store it
            if entity_expression == None or sparql_tree == None:
                raise RuntimeError("Require parsed sparql tree and sparql node, and edoal entity expression.")
            self.represents = entity_expression
            self.sparqlTree = sparql_tree
        
        def addNode(self, query_node=None):
            atom = query_node.descend()
            if atom.isAtom():
                theNode = self.QPNode(about=atom)
                self.qpNodes.append(theNode)
                print("> QP [{}] represents <{}> as:".format(str(atom), self.represents))
                # HERE WE CAN DO A TRANSLATION OF THE NODE!!! 
            #TODO: Recursive processing of branch when dumped into non-leaf branch 
            else: warnings.warn("Not Implemented Yet: recursive processing when stepped in non-leaf branch ([{}])".format(atom))

            # Identify the BGP position by searching the ancestor tree
            bgpPos = None
            pp = query_node.getAncestors()
            for p in pp:
                nType = type(p).__name__
                if len(p.getChildren()) == 1:
                    # This is ancestor is not a branching node. Skip to the next ancestor but remember this node as, eventually,
                    # the top node of this branch
                    topOfBranch = p
                elif nType == 'ObjectListPath':
                    # This Node represents an object
                    bgpPos = 'object'
                    print('[{}] determined as <{}>'.format(str(p),bgpPos))
                    theNode.setType(bgpPos)
#                     print("Found <{}>, type <{}>".format(p, nType))
                    # Continue, and find binding with its subject
                elif nType == 'VerbPath':
                    # This Node represents a property
                    bgpPos = 'property'
                    theNode.setType(bgpPos)
                    print('[{}] determined as <{}>'.format(str(p),bgpPos))
#                     print("Found <{}>, type <{}>".format(p, nType))
                    # Continue, and find binding with its subject and object
                elif nType == 'TriplesSameSubjectPath':
                    if bgpPos == None:
                        # We are in a TSSP leg, AND, we didn't determine the bgpPos yet, hence the main Node represents a subject
                        # and its children represent the rest of the triple.
                        bgpPos = 'subject'
                        theNode.setType(bgpPos)    
                        print('[{}] determined as <{}>'.format(str(p),bgpPos))
#                         print("Found <{}> (type [{}]) as (S, -, -)".format(p, nType))
                        # Now process the children, except itself, to form the triple
                        for plp in p.getChildren():
                            if type(plp).__name__ == 'VarOrTerm':
                                # This is the branch of itself, hence skip
                                pass
                            elif type(plp).__name__ == 'PropertyListPathNotEmpty':
                                for c in plp.getChildren():
                                    if type(c).__name__ == 'ObjectListPath':
                                        # This is the object to the triple, hence associate it with the main Node
                                        theNode.addAssociate(bgp_type='object', assoc_node=c)
                                    elif type(c).__name__ == 'VerbPath':
                                        # This is the predicate to the triple, hence associate it with the main Node
                                        theNode.addAssociate(bgp_type='property', assoc_node=c) 
                                    else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(plp, type(plp).__name__,c,type(c).__name__))
                            else: raise RuntimeError("Unexpectedly found [{}] as child of [{}], which was not anticipated".format(plp,p))
                        break
                    elif bgpPos == 'object':
                        # We are in a TSSP leg, AND, we did determine the bgpPos already, hence 
                        # this is the grandparent of the main Node (object), hence this subject might be
                        # 1 - either a variable or BNode to bind
                        # 2 - or a URIRef  
                        # and its children represent the rest of the triple.
                        #TODO: Check whether to discern between the type of TERM (BNode, URIREF, Literal)
                        for c in p.getChildren():
                            if type(c).__name__ == 'VarOrTerm':
                                # This is the subject to the triple, hence associate it with the main Node
                                theNode.addAssociate(bgp_type='subject', assoc_node=c) 
                            elif type(c).__name__ == 'PropertyListPathNotEmpty':
                                for plp in c.getChildren():
                                    if type(plp).__name__ == 'ObjectListPath':
                                        # Now in the branch leading to itself 
                                        pass
                                    elif type(plp).__name__ == 'VerbPath':
                                        # This is the predicate to the triple, hence associate it with the main Node
                                        theNode.addAssociate(bgp_type='property', assoc_node=plp) 
                                    else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(plp, type(plp).__name__,c,type(c).__name__))
                            else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(c,type(c).__name__,p,type(p).__name__))
                        break
                    elif bgpPos == 'property': 
                        # We are in a TSSP leg, AND, we did determine the bgpPos already, hence 
                        # this is the grandparent of the main Node (predicate).
                        # Hence, find the object and subject to the main Node, and associate them to the main Node 
                        for c in p.getChildren():
                            if type(c).__name__ == 'VarOrTerm':
                                # This is the subject to the triple, hence associate it with the main Node
                                theNode.addAssociate(bgp_type='subject', assoc_node=c) 
                            elif type(c).__name__ == 'PropertyListPathNotEmpty':
                                for plp in c.getChildren():
                                    if type(plp).__name__ == 'ObjectListPath':
                                        # This is the object to the triple, hence associate it with the main Node
                                        theNode.addAssociate(bgp_type='object', assoc_node=plp) 
                                    elif type(plp).__name__ == 'VerbPath':
                                        # Now in the branch leading to itself 
                                        pass
                                    else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(plp, type(plp).__name__,c,type(c).__name__))
                            else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(c,type(c).__name__,p,type(p).__name__))
                        break
                elif nType == 'PropertyListPathNotEmpty':
                    if bgpPos == None:
                        # We are in a PLPNE leg, WITHOUT bgpPos assigned already, hence determine
                        # whether the main node theNode represents either a property or an object
                        for c in p.getChildren():
                            if c == topOfBranch:
                                # This is the branch that carries the main node (theNode); we can now establish its type
                                if type(c).__name__ == 'ObjectListPath':
                                    bgpPos='object'
                                    theNode.setType(bgpPos)
                                    break
                                elif type(c).__name__ == 'VerbPath':
                                    # Now in the branch leading to itself 
                                    bgpPos='property'
                                    theNode.setType(bgpPos)
                                    break
                                else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(c, type(c).__name__,p,type(p).__name__))
                    elif bgpPos == 'property':
                        # We are in a PLPNE leg, AND, we did already determine the bgpPos (property), hence 
                        # process the object(s) that might be either:
                        # 1 - either a variable or BNode to bind, or
                        # 2 - a URIRef
                        #TODO: Check whether to discern between the type of TERM (BNode, URIREF, Literal)
                        #TODO: Implement the processing of the object of the triple
                        warnings.warn("Found <{}>: processing more object(s) not yet implemented.".format(p))
                    elif bgpPos == 'object':
                        # We are in a PLPNE leg, AND, we did already determine the bgpPos (object), hence 
                        # process the property
                        #TODO: Implement the processing of the property of the triple 
                        warnings.warn("Found [{}]: processing its property not yet implemented, if necessary.".format(p))
                    else: warnings.warn("Found PLPNE [{}], however with unexpected bgpPos <{}>. This is an unforeseen branch that requires further study. All hell will break loose?!".format(p, bgpPos))
                elif nType == 'TriplesBlock':
                    warnings.warn('We assumed this to be dead code, because the Query Pattern should had been processed by now. Found <{}> as ancestor to <{}>.'.format(nType, p))
                    # Since we are looking for the triple context of the main Node, we ASSUME we can stop here.
                    break
                else: warnings.warn("Unexpectedly found <{}> as ancestor to <{}>. This might be valid, but requires further study. All hell will break loose?!".format(nType, p))
    
        def getNode(self, about):
            for n in self.qpNodes:
                if n.about == about: return(n)
            return (None)
                   
        def __str__(self):
            result = ''
            for n in self.qpNodes:
                result += str(n)
            return(result)


    class VarConstraints():
                
        def isBoundBy(self, qp_node):
            '''
            Utility function to establish whether a sparql tree node that occurs as BGP in the Query Pattern subtree, binds a variable that is part 
            of a sparql tree node that occurs in the Filter subtree as value logic tuple. 
            '''
            return(self.boundVar in qp_node.binds)
                
        
        class ValueLogicNode():
            
            def __init__(self, valLogs, f):
                for v in valLogs:
#                     print("Elaborating on valueLogic: ", v)
                    pp = v.getAncestors()
                    prevP = None
                    operand = None
                    operation = None
                    varFirst = None
                    for p in pp:
                        cc = p.getChildren()
                        if len(cc) > 1:
                            # This is a relevant branch since this parent has more children.
                            pType = type(p).__name__
#                             print("<{}> is a [{}]".format(p, pType))
                            if pType == 'BuiltInCall':
                                warnings.warn("Ignoring constraint on [{}]: not yet implemented".format(p))
                                break
                            elif pType == 'RelationalExpression':
#                                 print('Build [{}]'.format(pType))
                                #TODO: Add the possibility for chained variables, i.e., [?t > ?v]
                                for c in cc:
#                                     print(">>\t<{}> is a [{}]".format(c, type(c).__name__))
                                    cType = type(c).__name__
                                    if c == prevP:
                                        # This child is itself, hence determine (var operation operand) versus 
                                        # (operand operation var) by determining if the operand has been addressed already
                                        varFirst = (operand == None)
                                    elif cType == 'NumericExpression':
                                        # This child is the top of branch leading to the operand; 
                                        # The operand is either a value, e.g., DECIMAL, or a variable
                                        atom = c.descend()
                                        if atom == None: 
                                            warnings.warn("QM node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))
                                        aType = type(atom).__name__
                                        if aType in ['INTEGER', 'DECIMAL', 'DOUBLE', 'HEX']:
                                            operand = c
                                        elif aType == 'VAR1' or aType == 'VAR1':
                                            warnings.warn('Chained variables in Query Modifiers not yet supported. Mediation will be bogus.')
                                            operand = c # although this is incorrect, make that the program will not crash as result of missing elements.
                                        else: RuntimeError("Did not expect [{}] node in Query Modifier ({}), VAR's or values only.".format(aType, atom))
                                    else: operation = c
                                self.append({'varFirst': varFirst, 'operation': operation, 'operand': operand})
                                break
                        prevP = p


        def __init__(self, sparql_tree, sparqle_var):
            #TODO: Consider the necessity of the two object variables boundVar & entity
            self.boundVar = ''       # (String) the name of the [Var] that has been bounded in the QueryPatternTriple; Necessary?? 
            self.entity = ''         # (String) the entity expression that this var has been bound to
            self.valueLogics = []    # list of (ValueLogicNode)s, each of them formulating one single constraint, e.g., (?var > DECIMAL)
            
            if sparql_tree == None or sparqle_var == None:
                raise RuntimeError("Both parsed sparql tree and sparql variable required.")
            filterElements = sparql_tree.searchElements(element_type=parser.Filter)
            if filterElements == []:
                raise NotImplementedError('Cannot find [FILTER] node in the sparql tree; constraint other than type <Filter> not yet implemented')
            
            # Find the [Var]-node as part of a [ValueLogical] in this part of the tree
            nodeType = parser.Var   
            for fe in filterElements:
                print("Searching for <{}> as type <{}> in {}: ".format(sparqle_var, nodeType, fe))
                varElements = fe.searchElements(element_type=nodeType, value=sparqle_var)
                if varElements == []:
                    warnings.warn('Cannot find <{}> as part of a [{}] expression in <{}>'.format(sparqle_var, nodeType, fe))
                else:
                    self.boundVar = sparqle_var
                    for v in varElements:
    #                     print("Elaborating on valueLogic: ", v)
                        pp = v.getAncestors()
                        topOfBranch = None
                        operand = None
                        operation = None
                        varFirst = None
                        for p in pp:
                            pType = type(p).__name__
                            children = p.getChildren()
                            if len(children) == 1:
                                # This is ancestor is not a branching node. Skip to the next ancestor but remember this node that becomes, eventually,
                                # the top node of this branch
                                topOfBranch = p
#                             print("<{}> is a [{}]".format(p, pType))
                            elif pType == 'BuiltInCall':
                                warnings.warn("Ignoring constraint on [{}]: not yet implemented".format(p))
                                break
                            elif pType == 'RelationalExpression':
#                                 print('Build [{}]'.format(pType))
                                #TODO: Add the possibility for chained variables, i.e., [?t > ?v]
                                self.valueLogics.append(p)
                                break
#                             elif pType == 'ConditionalAndExpression':
#                                 for c in children:
#                                     print(">>\t<{}> is a [{}]".format(c, type(c).__name__))
#                             else: 
#                                 for c in children:
#                                     print(">>\t<{}> is a [{}]".format(c, type(c).__name__))
                            else: raise NotImplementedError('Found [{}] ({}) as ancestor to [{}]; this needs further study...'.format(p,pType,v))
    #                         if pType == 'RelationalExpression':
    #                             pass
    #                         elif pType == 'ValueLogical':
    #                             print("<{}> is a [{}] with length <{}>".format(p, pType, len(p)))
    #                             pass
                if len(self.valueLogics) > 0:
                    self.render()
                else: print('No applicable Query Modifiers found for <{}>'.format(sparqle_var))

        def __str__(self):
            result = '( '
            for vl in self.valueLogics:
                result += str(vl) + " ) "
            return(result)

        def render(self):
            print('constraints: \n' + self.__str__())


    def __init__(self, entity_expression=None, sparqlData=None, *, entity_type=parser.iri):
        '''
        Generate the sparql context that is associated with the EntityExpression. If no entity_type is given, assume an IRI type.
        Returns the context, with attributes:
        * entity       : (mediator.Correspondence.EntityExpression) the subject EntityExpression
        * sparqlData   : the parsed sparql-query-tree
        * qpTriples    : the qpNodes from the sparql Query Pattern that are referred to in the EntityExpression
        * constraints   : the qpNodes from the sparql Query Pattern FILTER that constrain the variables bound in the qpTriples 
        
        '''
        self.entity = ''         # (EntityExpression) The EDOAL entity (Class, Property, Relation, Instance) name this context is about;
        self.parsedQuery = ''    # (parser.grammar.ParseInfo) The parsed query that is to be mediated
        self.qpTriples = []      # List of (QueryPatternTriple)s, representing the contextualised triples that are addressing the EDOAL entity (self.about)
        self.constraints = {}     # Dictionary, indexed by the bound variables that occur in the qpTriples, as contextualised Filters.
        
#         assert isinstance(entity_expression, EntityExpression) and isinstance(sparqlData, ParseStruct)
        if (entity_expression==None or sparqlData==None):
            raise ValueError("Edoal entity and sparqlData required")
        
        self.entity = entity_expression
        #TODO: process other sparqlData than sparql query, i.e., rdf triples or graph, and sparql result sets
        self.parsedQuery = parseQuery(sparqlData)
        if self.parsedQuery == []:
            raise RuntimeError("Cannot parse the query sparqlData")
        
        self.parsedQuery.render()
        #TODO: get the namespace from the sparqle query, don't assume 'ns:'
        uri, tag = entity_expression.entity[1:].split("}")
        val = 'ns:'+tag
        
        # 1: Find the qpNodes for which the context is to be build, matching the Entity1 Name and its Type
        srcNodes = self.parsedQuery.searchElements(element_type=entity_type, value=val)
        if srcNodes == []: 
            raise RuntimeError("Cannot find element <{}> of type <{}> in sparqlData".format(val, entity_type))
        
        # 2: Build the context
        self.qpTriples = []         # List of (QPNode)s that address the edoal entity.
#         self.qmNodes = {}           # a dictionary, indexed by the qp.about, i.e., the name of the EntityExpression, of lists of constraints 
                                    # that appear in the Query Modifiers clause, each list indexed by the variable name that is bound
        # 2.1: First build the Query Pattern Triples
        # 2.1.1: Find the top of the query's Query Pattern
#         qryPatterns = self.parsedQuery.searchElements(element_type=parser.WhereClause)
#         if qryPatterns == []:
#             raise RuntimeError("Cannot find WHERE-clause")
#         elif len(qryPatterns) > 1:
#             raise NotImplementedError("Cannot yet process more than one WHERE-clause")
#         
#         for p in qryPatterns: 
#             print(p.dump())
            
        # 2.1.2: For each node, find the qpTriples
        for qrySrcNode in srcNodes:
            # Find and store the QueryPatternTriple of the main Node
            print("Building context for <{}>".format(qrySrcNode))
            print('='*30)
            #TODO: Probably rq is too high in the tree - consider a lower node such as [WhereClause] (i.e., qryPatterns) or [GroupGraphPattern] 
            qpt = self.QueryPatternTriple(entity_expression=entity_expression, sparql_tree=self.parsedQuery)
            qpt.addNode(qrySrcNode)
            self.qpTriples.append(qpt)
            print("QP triple(s) determined: \n\t", str(qpt))
            print("Vars that are bound by these: ")
            for n in qpt.qpNodes:
                for b in n.binds:
                    print("\t<{}>".format(b))
                print("\n")
        
        # 2.2: Next, build the Query Modifiers that address the variables that are bound by the considered Query Pattern
        print('-+'*30)
        #TODO: We assume only one [WhereClause] (hence, qryPatterns[0])  
        # 2.2.1: Select the Query Modifiers top node in this Select Clause
        
#         filterTop = list(qryPatterns[0].searchElements(element_type=GraphPatternNotTriples))[0]
        #TODO: Assumed one [GraphPatternNotTriples] (hence, list(...)[0])  
        filterTop = self.parsedQuery.searchElements(element_type=parser.GraphPatternNotTriples)
        if filterTop == []:
            raise RuntimeError("Cannot find Query Modifiers clause (LIMIT, )")
#             print('Top for QM part of tree:')
#             print(filterTop.dump())
        # 2.2.2 - for each bound variable in the qp, collect the ValueLogics that represent its constraint
        for qpt in self.qpTriples:
            for qpNode in qpt.qpNodes:
                for var in qpNode.binds:
                    # Find the ValueLogicNode that addresses this variable
                    self.constraints[str(var)] = []
                    print("Elaborating on var <{}>".format(str(var)))
                    print('='*30)
                    # 3 - determine and store its value logics
                    # Cycle over every FILTER subtree
                    for filter in filterTop:
                        vc = self.VarConstraints(sparql_tree=filter, sparqle_var=str(var))
                        self.constraints[str(var)].append(vc)


    def __str__(self):
        result = "<entity1>: " + str(self.entity) + "\nhas nodes:"
        for qpt in self.qpTriples:
            result += "\n-> " + str(qpt) 
        result += "\n"
        for vc in self.constraints:
            result += str(vc) + ": "
            for vl in self.constraints[vc]:
                result += str(vl)
        return(result)
        
    def render(self):
        print(self.__str__())
            
    def getSparqlElements(self):
        result = []
        print("Searching for sparql elements that are associated with <{}>".format(self.entity))
        return(result)
  
