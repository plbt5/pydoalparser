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

from parsertools.parsers import sparqlparser
from parsertools.base import ParseStruct

#TODO: ParseStruct wijzigen naar SPARQLStruct from parsertools.parsers.sparqlparser

from builtins import str
from distutils.dist import warnings
from utilities.namespaces import NSManager        

    
class Context():
    '''
    Represents the sparql context of <entity1> that is mentioned in the EDOAL correspondence.
    It builds the relationship between:
    1 - the <entity1> and the URIRef element(s) in the Query Pattern of the sparql tree, and 
    2 - and the restrictions that yield in the Query Modifiers of the sparql tree.
    * 
    '''
    
    mns = 'http://ts.tno.nl/mediator/1.0/'
    localLabels = {
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


    class QueryPatternTripleAssociation():
        '''
        A QPTAssoc contains the association between one Correspondence of an Alignment and: (i) the BGP patterns (as references, i.e., the QPTripleRef) 
        that are referred to by the correspondence; and (ii) the value logic patterns that are related to it through shared query variables. 
        The BGP patterns are part of the WHERE clause, while the value logic patterns are part of the FILTER clause.
        '''
        
        
        class QPTripleRef():
            '''
            A QPTripleRef contains the association between one Correspondence of an Alignment, and the sparql tree. From the latter,
            it contains (i) the triples that are to be translated, (ii) the position of the entity_iriref in question in the triple, and (iii) the
            variables that are bound in this triples.
            '''
            
            def __init__(self, about=None):
                self.about = ''      # (ParseInfo): the atomic node in the sparql tree that is referred to by the Edoal Entity Element
                self.type = ''       # (String): the Basic Graph Pattern position of this node: <S|P|O>
                self.binds = []      # (List of String)(optional): a list of names of two, one or zero (when BGPType=p) or one or zero (=s or =o) Vars that are bound by this node: <VAR1 | VAR2 | PNAME_LN>
                self.associates = {} # (Dict(iri, ParseInfo)): the annotated (s,p,o) triple, each of which refers to a QPNode in the triple and is annotated with its BGP position.
                self.partOfRDF = ''  #TODO: The RDF Triple Pattern (s,p,o) (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#defn_TriplePattern)
                                     #     that this node is part of (created)
                #TODO: register our own namespace for mediator, and use its prefix to local labels, in order to prevent label mangling
                if about == None: raise RuntimeError("Cannot create QPTripleRef from None")
                atom = about.descend()
                if atom.isAtom():
                    self.about = atom
                else: raise NotImplementedError("Creating QPTripleRef from non-atom node ({}) is not implemented, and considered bad practice.".format(atom))
            
            def setType(self, bgp_type=None):
                assert bgp_type in [Context.localLabels['subject'],Context.localLabels['property'],Context.localLabels['object']], "Wrong type: Cannot add BGP type <{}>".format(bgp_type)
                self.type = Context.localLabels[bgp_type]
                self.addAssociate(self.type, self.about)
                
            def addAssociate(self, bgp_type=None, assoc_node=None):
                '''
                1 - This method adds to its subject QPTripleRef this (associated) node that is part of the QPTripleRef's BGP (s,p,o). To that end it will find 
                the terminal or atom node in this branch, and raise an error when there are more branches down the tree. 
                2 - In conjunction to this, it also checks whether the associated node represents a sparql variable. If so, it will add the 
                variable to the binding of its subject QPTripleRef.
                3 - TODO: when the BGP becomes complete after this last addition, it will generate an RDF triple from it and store it in its
                subject QPTripleRef (not a triple store).
                Input: 
                * assoc_node:    The associated node, which is considered to be on a tree vertice that has no other branches. The method will throw a Runtime error
                                when there are branches found lower in the tree.
                * bgp_type:      The position of the association node in the BGP triple. This can be either a string ('subject' | 'property' | 'object'), or
                                a full blown URIRef of identical nature.
                '''
                # First figure out the bgp type
                assert bgp_type != None and assoc_node != None, 'Cannot add empty querypattern qptRefs'
                bgp_position = Context.localLabels[bgp_type]
                
                # Now find the terminal/atom of the association node
                atom = assoc_node.descend()
                if atom.isAtom():
                    # Associate it with the main Node
                    if bgp_position in self.associates:
                        raise RuntimeError('Position of <{}> in {} already taken'.format(bgp_position, str(self)))
                    else: 
                        self.associates[bgp_position] = atom
                    # In addition, this might represent a variable, hence consider to store the binding
                    self.considerBinding(atom)
                else: raise NotImplementedError("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings.".format(atom))
                
#                 print('[{}] determined as <{}> associate to <{}>'.format(str(assoc_node),bgp_position,str(self.about)))

                # Lastly, generate an RDF triple and store it in its subject QPTripleRef
                if len(self.associates) == 3:
                    #TODO: create three RDF Terms (each as Literal, URIRef or BNode), and formulate & store it as statement
                    self.partOfRDF = (self.associates[Context.localLabels['subject']], self.associates[Context.localLabels['property']], self.associates[Context.localLabels['object']])
            
            def considerBinding(self, qpnode):
                # We assume that we only need to take into consideration the variables in order to be able to follow through with the translations, hence
                # the PNAME's, i.e., iri's that are bound to this entity_iriref, are assumed to be taken care of as another EDOAL alignment map
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
                    str(self.associates[Context.localLabels['subject']]) + ', ' + \
                    str(self.associates[Context.localLabels['property']]) + ', ' + \
                    str(self.associates[Context.localLabels['object']]) + ' )'
                return(result)
            
        def __init__(self, *, entity_expression, sparql_tree, nsMgr):
#             assert isinstance(entity_expression, EntityExpression) and isinstance(sparql_tree, ParseStruct)
            self.represents = '' # (EntityExpression) the EDOAL entity_iri (Class, Property, Relation, Instance) name;
                                 # This is in fact unnecessary because this is already stored in the higher Context class
            self.qptRefs = []    # List of (QPTripleRef)s, i.e., implicit Query Pattern nodes that address the Entity Expression
            self.pfdNodes = {}   # Temporary namespace dictionary. Dict of (ParseStruct)s indexed by prefix : the PrefixDecl nodes that this entity_iri relates to
            self.sparqlTree = '' # The sparql tree that this class uses to relate to
            
            assert entity_expression.__class__.__name__ == 'EntityExpression' and isinstance(nsMgr, NSManager) and isinstance(sparql_tree, ParseStruct)
            # Now find the atom of the main Node, i.e., what this is all about, and store it
            if entity_expression == None or sparql_tree == None:
                raise RuntimeError("Require parsed sparql tree and sparql node, and edoal entity_iri expression.")
            self.represents = entity_expression
            self.sparqlTree = sparql_tree
            # Now find the [PrefixDecl] nodes
            #TODO: Remove this after refactoring to locally valid namespace expansion etc. in SPARQLStruct
            prefixDecls = sparql_tree.searchElements(element_type=sparqlparser.PrefixDecl)
            _, src_iriref, _ = nsMgr.split(entity_expression.entity_iriref)
            for prefixDecl in prefixDecls:
                ns_prefix, ns_iriref = str(prefixDecl.prefix)[:-1], str(prefixDecl.namespace)[1:-1]
                if ns_iriref == src_iriref: 
                    self.pfdNodes[ns_prefix] = {}
                    self.pfdNodes[ns_prefix]['ns_iriref'] = ns_iriref
                    self.pfdNodes[ns_prefix]['node'] = prefixDecl
        
        def addQPTRef(self, query_node=None):
            assert isinstance(query_node, ParseStruct)
            atom = query_node.descend()
            if atom.isAtom():
                theNode = self.QPTripleRefs(about=atom)
                self.qptRefs.append(theNode)
#                 print("> QP [{}] represents <{}> as:".format(str(atom), self.represents))
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
#                     print('[{}] determined as <{}>'.format(str(p),bgpPos))
                    theNode.setType(bgpPos)
                    # Continue, and find binding with its subject
                elif nType == 'VerbPath':
                    # This Node represents a property
                    bgpPos = 'property'
                    theNode.setType(bgpPos)
#                     print('[{}] determined as <{}>'.format(str(p),bgpPos))
                    # Continue, and find binding with its subject and object
                elif nType == 'TriplesSameSubjectPath':
                    if bgpPos == None:
                        # We are in a TSSP leg, AND, we didn't determine the bgpPos yet, hence the main Node represents a subject
                        # and its children represent the rest of the triple.
                        bgpPos = 'subject'
                        theNode.setType(bgpPos)    
#                         print('[{}] determined as <{}>'.format(str(p),bgpPos))
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
    
        def getQPTRef(self, about):
            refs = []
            for n in self.qptRefs:
                if n.about == about:
                    refs.append(n)
            if len(refs) == 1: return refs[0]
            assert len(refs) == 0, "Did not expect more than one matches for {}".format(about)
            return None
                   
        def __str__(self):
            result = ''
            for n in self.qptRefs:
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
            #TODO: Consider the necessity of the two object variables boundVar & entity_iri
            self.boundVar = ''       # (String) the name of the [Var] that has been bounded in the QueryPatternTripleAssociation; Necessary?? 
            self.entity_iriref = ''         # (String) the entity_iri expression that this var has been bound to
            self.valueLogics = []    # list of (ValueLogicNode)s, each of them formulating one single constraint, e.g., (?var > DECIMAL)
            
            if sparql_tree == None or sparqle_var == None:
                raise RuntimeError("Both parsed sparql tree and sparql variable required.")
            filterElements = sparql_tree.searchElements(element_type=sparqlparser.Filter)
            assert len(filterElements) > 1, "Do not support more than one FILTER clauses in SPARQL (yet, please implement me)"
            if filterElements == []:
                warnings.warn('Cannot find [FILTER] node in the sparql tree; constraint other than type <Filter> not yet implemented')
            else:
                # Find the [Var]-node as part of a [ValueLogical] in this part of the tree
                nodeType = sparqlparser.Var   
                for fe in filterElements:
    #                 print("Searching for <{}> as type <{}> in {}: ".format(sparqle_var, nodeType, fe))
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
    #                 if len(self.valueLogics) > 0:
    #                     self.render()
    #                 else: print('No applicable Query Modifiers found for <{}>'.format(sparqle_var))

        def __str__(self):
            result = '( '
            for vl in self.valueLogics:
                result += str(vl) + " ) "
            return(result)

        def render(self):
            print('constraints: \n' + self.__str__())


    def __init__(self, entity_type=sparqlparser.iri, *, entity_expression, sparqlTree, nsMgr ):
        '''
        Generate the sparql context that is associated with the EntityExpression. If no entity_type is given, assume an IRI type.
        Returns the context, with attributes:
        * entity_iri       : (mediator.Correspondence.EntityExpression) the subject EntityExpression
        * sparqlTree   : (ParseStruct) the parsed sparql-query-tree
        * qpTriples    : the qptRefs from the sparql Query Pattern that are referred to in the EntityExpression
        * constraints   : the qptRefs from the sparql Query Pattern FILTER that constrain the variables bound in the qpTriples 
        
        '''
        self.entity_iriref = ''  # (EntityExpression) The EDOAL entity (Class, Property, Relation, Instance) name (as IRI) this context is about;
        self.parsedQuery = ''    # (parser.grammar.ParseInfo) The parsed query that is to be mediated
        self.qpTriples = []      # List of (QueryPatternTripleAssociation)s, representing the contextualised triples that are addressing the EDOAL entity_iri (self.about)
        self.constraints = {}    # Dictionary, indexed by the bound variables that occur in the qpTriples, as contextualised Filters.
        self.nsMgr = None        # (namespaces.NSManager): the current nsMgr that can resolve any namespace issues of this mediator 
        
#         assert isinstance(entity_expression, Mediator.EntityExpression) and isinstance(sparqlTree, ParseStruct)
        assert isinstance(sparqlTree, ParseStruct) and entity_expression.__class__.__name__ == 'EntityExpression' and isinstance(nsMgr, NSManager)

        self.nsMgr = nsMgr
        self.entity_iriref = entity_expression
        #TODO: process other sparqlData than sparql query, i.e., rdf triples or graph, and sparql result sets
        self.parsedQuery = sparqlTree
        if self.parsedQuery == []:
            raise RuntimeError("Cannot parse the query sparqlData")
        
        eePf, eeIri, eeTag = self.nsMgr.split(entity_expression.entity_iriref)
        src_qname = eePf + ':' + eeTag
        
        # 1: Find the qptRefs for which the context is to be build, matching the Entity1 Name and its Type
        srcNodes = self.parsedQuery.searchElements(element_type=entity_type, value=src_qname)
        if srcNodes == []: 
            raise RuntimeError("Cannot find element <{}> of type {} in sparqlData".format(src_qname, entity_type))
        
        # 2: Build the context
        self.qpTriples = []         # List of (QPTripleRef)s that address the edoal entity_iri.
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
            # Find and store the QueryPatternTripleAssociation of the main Node
#             print("Building context for <{}>".format(qrySrcNode))
#             print('='*30)
            #TODO: Probably rq is too high in the tree - consider a lower node such as [WhereClause] (i.e., qryPatterns) or [GroupGraphPattern] 
            qpt = self.QueryPatternTripleAssociation(entity_expression=entity_expression, sparql_tree=self.parsedQuery, nsMgr=self.nsMgr)
            qpt.addQPTRef(qrySrcNode)
            self.qpTriples.append(qpt)
#             print("QP triple(s) determined: \n\t", str(qpt))
#             print("Vars that are bound by these: ")
#             for n in qpt.qptRefs:
#                 for b in n.binds:
#                     print("\t<{}>".format(b))
#                 print("\n")
        
        # 2.2: Next, build the Query Modifiers that address the variables that are bound by the considered Query Pattern
#         print('-+'*30)
        #TODO: We assume only one [WhereClause] (hence, qryPatterns[0])  
        # 2.2.1: Select the Query Modifiers top node in this Select Clause
        
#         filterTop = list(qryPatterns[0].searchElements(element_type=GraphPatternNotTriples))[0]
        #TODO: Assumed one [GraphPatternNotTriples] (hence, list(...)[0])  
        filterTop = self.parsedQuery.searchElements(element_type=sparqlparser.GraphPatternNotTriples)
        if filterTop == []:
            raise RuntimeError("Cannot find Query Modifiers clause (Filter)")
#             print('Top for QM part of tree:')
#             print(filterTop.dump())
        # 2.2.2 - for each bound variable in the qp, collect the ValueLogics that represent its constraint
        for qpt in self.qpTriples:
            for qpNode in qpt.qptRefs:
                for var in qpNode.binds:
                    # Find the ValueLogicNode that addresses this variable
                    self.constraints[str(var)] = []
#                     print("Elaborating on var <{}>".format(str(var)))
#                     print('='*30)
                    # 3 - determine and store its value logics
                    # Cycle over every FILTER subtree
                    for filter in filterTop:
                        vc = self.VarConstraints(sparql_tree=filter, sparqle_var=str(var))
                        self.constraints[str(var)].append(vc)


    def __str__(self):
        result = "<entity1>: " + str(self.entity_iriref) + "\nhas nodes:"
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
        print("NOT IMPLEMENTED: Searching for sparql elements that are associated with <{}>".format(self.entity_iriref))
        return(result)
  
