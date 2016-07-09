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

from parsertools.base import ParseStruct
from parsertools.parsers.sparqlparser import SPARQLParser

from builtins import str
from distutils.dist import warnings
from utilities.namespaces import NSManager        
from mediator import mediatorTools
import json
from json.decoder import JSONDecodeError
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError

    
class Context():
    '''
    Represents the sparql context of (source) <entity>s (a single entity, NOT an entity *expression*) that is mentioned in the EDOAL correspondence.
    It builds the relationship between:
    1 - the source <entity> and the URIRef element(s) in the Query Pattern of the sparql tree, and 
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
            A QPTripleRef represents a single query pattern, i.e., an {s,p,o} BGP triple, which is referred to by an entity that is mentioned in a Correspondence.  
            To that end it contains (i) the node in the parsed sparql tree that represents the edoal entity, (ii) its position in the triple, (iii) the nodes that form the triple, including their position in the triple, and (iv) the variables that are bound in this triples, if any.
            Indeed, (i) and (ii) are repeated in (iii), however, (i) and (ii) underline its function as entity.
            '''
            #TODO: Extend this structure to enable the inclusion of more than one node as vehicle for an edoal entity. The current implementation only allows a triple to contain one edoal entity, which is an unnecessary limitation
            def __init__(self, about=None):
                '''
                Input: a node in the parsed sparql (ParseInfo) that is either a node or can be traced to a node, representing the entity element of interest.
                '''
                self.about = None      # (ParseInfo): the atomic node in the sparql tree that is referred to by the Edoal Entity Element
                self.type = ''       # (String, canonical as Context.localLabels): the Basic Graph Pattern position of this node: <S|P|O>
                self.binds = []      # (List of String)(optional): a list of names of two, one or zero (when BGPType=p) or one or zero (=s or =o) Vars that are bound by this node: <VAR1 | VAR2 | PNAME_LN>
                self.associates = {} # (Dict{S|P|O, ParseInfo}): the annotated (s,p,o) triple, each of which refers to a QPNode in the triple and is annotated with its BGP position.
                self.partOfRDF = ''  #TODO: The RDF Triple Pattern (s,p,o) (https://www.w3.org/TR/2013/REC-sparql11-query-20130321/#defn_TriplePattern)
                                     #     that this node is part of (created)
                #TODO: register our own namespace for mediator, and use its prefix to local labels, in order to prevent label mangling
                if about == None: raise RuntimeError("Cannot create QPTripleRef from None")
                atom = about.descend()
                if atom.isAtom():
                    self.about = atom
                else: raise NotImplementedError("Creating QPTripleRef from non-atom node ({}) is not implemented, and considered bad practice.".format(atom))
            
            def setType(self, bgp_type=None):
                assert bgp_type != None, "Wrong type: Cannot add BGP position as None"
                if bgp_type in ['subject','property','object']:
                    self.type = Context.localLabels[bgp_type]
                elif bgp_type in [Context.localLabels['subject'], Context.localLabels['property'], Context.localLabels['object']]:
                    self.type = bgp_type
                else:
                    raise AttributeError("Expected a BGP position, but got {}".format(bgp_type))
                self.addAssociate(bgp_type=self.type, assoc_node=self.about)
                
            def addAssociate(self, bgp_type=None, assoc_node=None):
                '''
                1 - This method adds to its subject QPTripleRef this (associated) node that is part of the QPTripleRef's BGP (s,p,o). To that end it will find 
                the terminal or atom node in this branch, and raise an error when there are more branches down the tree. 
                2 - In conjunction to this, it also checks whether the associated node represents a sparql variable. If so, it will add the 
                variable to the binding of its subject QPTripleRef.
                3 - TODO: when the BGP becomes complete after this last addition, it will generate an RDF triple from it and store it in its
                subject QPTripleRef (not a triple store).
                Input: 
                * assoc_node:   The associated node, which is considered to be on a tree vertice that won't splitIri into other branches. The method will throw a Runtime error
                                when there are branches found lower in the tree.
                * bgp_type:     The position of the association node in the BGP triple. This can be either a string ('subject' | 'property' | 'object'), or
                                a full blown URIRef of identical nature.
                Return:
                * True:     When the QPTriple is complete, i.e., when the BGP (s,p,o) is all filled
                * False:    Otherwise.
                '''
                # First figure out the bgp type
                assert bgp_type != None and assoc_node != None, 'Cannot add empty querypattern qptRefs'
                if bgp_type in ['subject','property','object']: 
                    bgp_position = Context.localLabels[bgp_type]
                elif bgp_type in [Context.localLabels['subject'], Context.localLabels['property'], Context.localLabels['object']]:
                    bgp_position = bgp_type
                else:
                    raise AttributeError("Expected a BGP position, but got {}".format(bgp_type))
                
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
                    return True
                else: return False
            
            def considerBinding(self, qpnode):
                # We assume that we only need to take into consideration the variables in order to be able to follow through with the translations, hence
                # the PNAME's, i.e., iri's that are bound to this entity_expr, are assumed to be taken care of as another EDOAL alignment map
#                 if type(qpnode).__name__ in ['VAR1', 'VAR2', 'PNAME_LN']:
                if type(qpnode).__name__ in ['VAR1', 'VAR2']:
                    if (not str(qpnode) in self.binds) and (not qpnode == self.about):
                        self.binds.append(str(qpnode))
            
            def __repr__(self):
                result = "node:\n\tof type   : " + str(self.type) + "\n\tabout     : " + str(self.about)
                for a in self.associates:
                    result += "\n\tassociates: " + str(self.associates[a]) + " ( " + str(a) + " )"
                for b in self.binds:
                    result += "\n\tbinds     : " + str(b)
                return(result) 
            
            def __str__(self):
                result = str(self.type) + ' in BGP(' 
                if Context.localLabels['subject'] in self.associates:
                    result += str(self.associates[Context.localLabels['subject']])
                else: result += str(None)
                if Context.localLabels['property'] in self.associates:
                    result += ', ' + str(self.associates[Context.localLabels['property']])
                else: result += ', ' + str(None)
                if Context.localLabels['object'] in self.associates:
                    result += ', ' + str(self.associates[Context.localLabels['object']]) + ')'
                else: result += ', ' + str(None) + ')'
                return(result)
            
        def __init__(self, *, entity_expression, sparql_tree, nsMgr):
            self.represents = '' # (EntityExpression) the EDOAL entity_iri (Class, Property, Relation, Instance) name;
                                 # This is in fact unnecessary because this is already stored in the higher Context class
            self.qptRefs = []    # List of (QPTripleRef)s, i.e., Query Pattern nodes that address the Entity Expression
            self.pfdNodes = {}   # Temporary namespace dictionary. Dict of (ParseStruct)s indexed by prefix : the PrefixDecl nodes that this entity_iri relates to
            self.sparqlTree = '' # The sparql tree that this class uses to relate to
            
            assert isinstance(entity_expression, mediatorTools.EntityExpression)
            assert isinstance(nsMgr, NSManager)
            assert isinstance(sparql_tree, ParseStruct)
            # Now find the atom of the main Node, i.e., what this is all about, and store it
            if entity_expression == None or sparql_tree == None:
                raise RuntimeError("Require parsed sparql tree and sparql node, and edoal entity_iri expression.")
#             print("context: entity expression {}".format(entity_expression))
            self.represents = entity_expression
            self.sparqlTree = sparql_tree
            # Now find the [PrefixDecl] nodes
            #TODO: Remove this after refactoring to locally valid namespace expansion etc. in SPARQLStruct
            prefixDecls = sparql_tree.searchElements(element_type=SPARQLParser.PrefixDecl)
            _, src_iriref, _ = nsMgr.splitIri(entity_expression.getIriRef())
            for prefixDecl in prefixDecls:
                ns_prefix, ns_iriref = str(prefixDecl.prefix)[:-1], str(prefixDecl.namespace)[1:-1]
                if ns_iriref == src_iriref: 
                    self.pfdNodes[ns_prefix] = {}
                    self.pfdNodes[ns_prefix]['ns_iriref'] = '<' + ns_iriref + '>'
                    self.pfdNodes[ns_prefix]['node'] = prefixDecl
        
        def addQPTRef(self, query_node=None):
            assert isinstance(query_node, ParseStruct)
            atom = query_node.descend()
            if atom.isAtom():
                thisEEQPTriple = self.QPTripleRef(about=atom)
                self.qptRefs.append(thisEEQPTriple)
#                 print("> QP [{}] represents <{}> as:".format(str(atom), self.represents))
            #TODO: Recursive processing of branch when dumped into non-leaf branch 
            else: raise NotImplementedError("Not Implemented Yet: recursive processing when stepped in non-leaf branch ([{}])".format(atom))

            # Identify the BGP position by searching the ancestor tree
            bgpPos = None
            ancestors = query_node.getAncestors()
#             print("{} ancestors found".format(len(ancestors)))
            for ancestor in ancestors:
                # The stop criterion for this loop is not in its ancestors, but in having found all three BGP elements that this QPTriple is about.
                done = False
                nType = type(ancestor).__name__
                if len(ancestor.getChildren()) == 1:
                    # This is ancestor is not a branching node. Skip to the next ancestor but remember this node as, eventually,
                    # the top node of this branch
                    topOfBranch = ancestor
                elif nType == 'ObjectListPath':
                    # This Node represents an object
                    bgpPos = 'object'
#                     print('[{}] determined as <{}>'.format(str(ancestor),bgpPos))
                    thisEEQPTriple.setType(bgpPos)
                    # Continue, and find binding with its subject
                elif nType == 'VerbPath':
                    # This Node represents a property
                    bgpPos = 'property'
                    thisEEQPTriple.setType(bgpPos)
#                     print('[{}] determined as <{}>'.format(str(ancestor),bgpPos))
                    # Continue, and find binding with its subject and object
                elif nType == 'TriplesSameSubjectPath':
                    if bgpPos == None:
                        # We are in a TSSP leg, AND, we didn't determine the bgpPos yet, hence the main Node represents a subject
                        # and its children represent the rest of the triple.
                        bgpPos = 'subject'
                        thisEEQPTriple.setType(bgpPos)    
#                         print('[{}] determined as <{}>'.format(str(ancestor),bgpPos))
                        # Now process the children, except itself, to form the triple
                        for plp in ancestor.getChildren():
                            if type(plp).__name__ == 'VarOrTerm':
                                # This is the branch of itself, hence skip
                                pass
                            elif type(plp).__name__ == 'PropertyListPathNotEmpty':
                                for c in plp.getChildren():
#                                     print("assessing on node {}".format(c))
                                    if type(c).__name__ == 'ObjectListPath':
                                        # This is the object to the triple, hence associate it with the main Node
                                        done = thisEEQPTriple.addAssociate(bgp_type='object', assoc_node=c)
                                        if done: break
                                    elif type(c).__name__ == 'VerbPath':
                                        # This is the predicate to the triple, hence associate it with the main Node
                                        done = thisEEQPTriple.addAssociate(bgp_type='property', assoc_node=c) 
                                        if done: break
                                    else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(plp, type(plp).__name__,c,type(c).__name__))
                            else: raise RuntimeError("Unexpectedly found [{}] as child of [{}], which was not anticipated".format(plp,ancestor))
                        break
                    elif bgpPos == 'object':
                        # We are in a TSSP leg, AND, we did determine the bgpPos already, hence 
                        # this is the grandparent of the main Node (object), hence this subject might be
                        # 1 - either a variable or BNode to bind
                        # 2 - or a URIRef  
                        # and its children represent the rest of the triple.
                        #TODO: Check whether to discern between the type of TERM (BNode, URIREF, Literal)
                        for c in ancestor.getChildren():
                            if type(c).__name__ == 'VarOrTerm':
                                # This is the subject to the triple, hence associate it with the main Node
                                done = thisEEQPTriple.addAssociate(bgp_type='subject', assoc_node=c) 
                                if done: break
                            elif type(c).__name__ == 'PropertyListPathNotEmpty':
                                for plp in c.getChildren():
#                                     print("assessing on node {}".format(plp))
                                    if type(plp).__name__ == 'ObjectListPath':
                                        # Now in the branch leading to itself 
                                        pass
                                    elif type(plp).__name__ == 'VerbPath':
                                        # This is the predicate to the triple, hence associate it with the main Node
                                        done = thisEEQPTriple.addAssociate(bgp_type='property', assoc_node=plp) 
                                        if done: break
                                    else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(plp, type(plp).__name__,c,type(c).__name__))
                            else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(c,type(c).__name__,ancestor,type(ancestor).__name__))
                        break
                    elif bgpPos == 'property': 
                        # We are in a TSSP leg, AND, we did determine the bgpPos already, hence 
                        # this is the grandparent of the main Node that was a property.
                        # Hence, find the object and subject to the main Node, and associate them to the main Node 
                        for c in ancestor.getChildren():
                            if type(c).__name__ == 'VarOrTerm':
                                # This is the subject to the triple, hence associate it with the main Node
                                done = thisEEQPTriple.addAssociate(bgp_type='subject', assoc_node=c) 
                                if done: break
                            elif type(c).__name__ == 'PropertyListPathNotEmpty':
                                for plp in c.getChildren():
#                                     print("assessing on node {}".format(plp))
                                    if type(plp).__name__ == 'ObjectListPath':
                                        # This is the object to the triple, hence associate it with the main Node
                                        done = thisEEQPTriple.addAssociate(bgp_type='object', assoc_node=plp) 
                                        if done: break
                                    elif type(plp).__name__ == 'VerbPath':
                                        # Now in the branch leading to itself 
                                        pass
                                    else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(plp, type(plp).__name__,c,type(c).__name__))
                            else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(c,type(c).__name__,ancestor,type(ancestor).__name__))
                        break
                elif nType == 'PropertyListPathNotEmpty':
                    if bgpPos == None:
                        # We are in a PLPNE leg, WITHOUT bgpPos assigned already, hence determine
                        # whether the main node thisEEQPTriple represents either a property or an object
                        for c in ancestor.getChildren():
                            if c == topOfBranch:
                                # This is the branch that carries the main node (thisEEQPTriple); we can now establish its type
                                if type(c).__name__ == 'ObjectListPath':
                                    bgpPos='object'
                                    thisEEQPTriple.setType(bgpPos)
                                    break
                                elif type(c).__name__ == 'VerbPath':
                                    # Now in the branch leading to itself 
                                    bgpPos='property'
                                    thisEEQPTriple.setType(bgpPos)
                                    break
                                else: raise RuntimeError("Unexpectedly found [{}] ([{}]) as child of [{}] ([{}]).".format(c, type(c).__name__,ancestor,type(ancestor).__name__))
                    elif bgpPos == 'property':
                        # We are in a PLPNE leg, AND, we did already determine the bgpPos (property), hence 
                        # process the object(s) that might be either:
                        # 1 - either a variable or BNode to bind, or
                        # 2 - a URIRef
                        #TODO: Check whether to discern between the type of TERM (BNode, URIREF, Literal)
                        #TODO: Implement the processing of the object of the triple
                        warnings.warn("Found <{}>: processing more object(s) not yet implemented.".format(ancestor))
                    elif bgpPos == 'object':
                        # We are in a PLPNE leg, AND, we did already determine the bgpPos (object), hence 
                        # process the property
                        #TODO: Implement the processing of the property of the triple 
                        warnings.warn("Found [{}]: processing its property not yet implemented, if necessary.".format(ancestor))
                    else: warnings.warn("Found PLPNE [{}], however with unexpected bgpPos <{}>. This is an unforeseen branch that requires further study. All hell will break loose?!".format(ancestor, bgpPos))
                elif nType == 'TriplesBlock':
                    warnings.warn('We assumed this to be dead code, because the Query Pattern should had been processed by now. Found <{}> as ancestor to <{}>.'.format(nType, ancestor))
                    # Since we are looking for the triple context of the main Node, we ASSUME we can stop here.
                    break
                else: warnings.warn("Unexpectedly found <{}> as ancestor to <{}>. This might be valid, but requires further study. All hell will break loose?!".format(nType, ancestor))
    
        def getQPTRef(self, about):
            refs = []
            for n in self.qptRefs:
                if n.about == about:
                    refs.append(n)
            if len(refs) == 1: return refs[0]
            assert len(refs) == 0, "Did not expect more than one matches for {}".format(about)
            return None
                   
        def __str__(self):
            result = str(self.represents) + '\n\t'
            for n in self.qptRefs:
                result += str(n)
            return(result)

        def __repr__(self):
            result = str(self.represents) + '\n\t'
            for n in self.qptRefs:
                result += n.__repr__()
            return(result)
            

    class VarConstraints():
        '''
        The use of variables in the LIMIT clause of the sparql query is to bind constraints to the individuals of an entity. Constraints are specified
        by value logic expressions, the entity individuals by triple matches from the WHERE clause. This class VarConstraints is designed to relate, through
        the use of the variables, the entities with the constraints. Each class object represents the characteristics on how one variable is being bound to 
        the constraints. These characteristics are determined by inspection of the parsed tree.
        '''
                
        def isBoundBy(self, qp_node):
            '''
            Utility function to establish whether a sparql tree node that occurs as BGP in the Query Pattern subtree, binds a variable that is part 
            of a sparql tree node that occurs in the Filter subtree as value logic tuple. 
            '''
            return(self._boundVar in qp_node.binds)
                
        
        class ValueLogicExpression(dict):
            '''
            A value logic expression represents a single comparison as can be found in the FILTER clause, e.g., (?t > 36.0), or (?p = ?q). Consequently, 
            it has three attributes, the varRef, the comparator, and the restriction. From a Correspondence perspective, this clause is used to express
            the entity restriction, as follows: 
            1. varRef (string): the name of the variable that is being used. Note that the entity that the variable refers to, represents a Path
            2. comparator (string)  : the comparator that is being used to establish the truth value of the boolean expression. 
            3. restriction (string) : the value that acts as restriction for the varRef. This can either be a Value restriction, Type restriction or 
                Multiplicity restriction [formulae 2.23]. 
            '''
            
            def __init__(self, variable_node=None):
                '''
                Creating a ValueLogicExpression is achieved by parsing the query, starting at the [Var] node.  
                input: The node in the sparql tree that represents the variable
                The created object is a Dictionary with entries {'varRef': varRef, 'comparator': comparator, 'restriction': restriction}
                '''
                
                assert isinstance(variable_node, ParseStruct) and type(variable_node).__name__ == 'Var', \
                    "Cannot create a Value Logic Constraint without a 'Var' to start with, got '{}'".format(type(variable_node))
#                 print("Elaborating on valueLogic {} ({}) in tree: ".format(variable_node, type(variable_node)))
#                 print(variable_node.dump())
                # Get the list of ancestors of this node in the tree
                ancestors = variable_node.getAncestors()
                prevAncestor = None
                restriction = None
                comparator = None
                varRef = None
                for ancestor in ancestors:
                    # For each ancestor, consider all its children.
                    ChildNodes = ancestor.getChildren()
                    if len(ChildNodes) > 1:
                        # This is a relevant branch since this parent has more children.
                        pType = type(ancestor).__name__
#                         print("parent <{}> is of type [{}]".format(ancestor, pType))
#                         print(ancestor.dump())
                        if pType == 'BuiltInCall':
                            raise NotImplementedError("Found '{}', hence a Type Constraint, which is not implemented (yet: be my guest)".format(variable_node))
                            break
                        elif pType == 'RelationalExpression':
#                             print('Build [{}]'.format(pType))
                            #TODO: Add the possibility for chained variables, i.e., [?t > ?v]
                            for childNode in ChildNodes:
#                                 print(">>\t'{}' is a [{}]:".format(childNode, type(childNode).__name__))
#                                 print(childNode.dump())
                                cType = type(childNode).__name__
                                if childNode == prevAncestor:
                                    # Since we go up and down the branch, we found the original value_node itself, that, therefore, is the varRef
                                    atom = childNode.descend()
                                    if atom == None: 
                                        AttributeError("QM node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose, hence quitting".format(atom))
                                    varRef = atom
                                elif cType == 'NumericExpression':
                                    # This child is the top of branch leading to the restriction; 
                                    # The restriction is either a value, e.g., DECIMAL, or a variable
                                    atom = childNode.descend()
                                    if atom == None: 
                                        AttributeError("QM node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose, hence quitting".format(atom))
                                    aType = type(atom).__name__
                                    if aType in ['INTEGER', 'DECIMAL', 'DOUBLE', 'HEX']:
#                                         print("NumericExpression as {} found".format(aType)) 
                                        restriction = atom
                                    elif aType == 'VAR1' or aType == 'VAR1':
                                        raise NotImplementedError('Chained variables in Query Modifiers not supported (yet, please implement me).')
                                        # One aspect of implementing this feature is:
#                                         restriction = atom 
                                        #TODO: (Chained variables in constraint) However, the translation and transformation is much harder
                                    else: AttributeError("Did not expect [{}] node in Query Modifier ({}), VAR's or Values only.".format(aType, atom))
                                elif str(childNode) in ['<', '<=', '>', '>=', '=', '!=']:
#                                     print("Comparator {} found".format(childNode)) 
                                    comparator = childNode
                                else:
                                    # Unknown 
                                    raise AttributeError("Unknown attribute: '{}'".format(childNode))
#                             print("ValueLogicExpression complete: ({} {} {})".format(varRef, comparator, restriction))

                            super().__init__({'varRef': varRef, 'comparator': comparator, 'restriction': restriction})
#                             self.update({'varRef': varRef, 'comparator': comparator, 'restriction': restriction})
                            break
                        else:
                            warnings.warn("Found '{}' element unexpectedly, ignoring".format(pType))
                    # This parent has only one child, which makes it an irrelevant node: only atomic or branching nodes are relevant; those
                    #        in between are not. But this node may show to be an interesting one, hence store it temporarily and continue with next parent.
                    prevAncestor = ancestor


        def __init__(self, sparql_tree=None, sparql_var_name='', entity=None):
            from mediator import mediatorTools
            '''
            Input:
            - sparql_tree: (.ParseStruct) : The parsed tree must contain at least one 'FILTER' element, which must not be the tree root.
            - sparql_var_name: (string)    : The name of the sparql variable, including the question mark.
            - entity: ()    : the entity that this var is bound to
            Result: A class that contains the following attributes:
            - _boundVar: (string) : the name of the variable
            - _srcPath: the iriref of the path expression that leads to the Edoal <Property> or <Relation> element that this sparql variable is bound to
            - _valueLogicExprList: (list) : a list of (ValueLogicExpression) that represent the constraints that apply to this variable. Each element in the
                list represents a single constraint, e.g., "?var > 23.0", or "DATATYPE(?var) = '<iripath><class_name>'"
            '''
            
            #TODO: Consider the necessity of the two object variables _boundVar & entity_iri
            self._boundVar = ''       # (String) the name of the [Var] that has been bounded in the QueryPatternTripleAssociation; Necessary?? 
            self._entity = ''        # (mediatorTools._Entity) the entity that this var has been bound to
            self._valueLogicExprList = []    # list of (ValueLogicExpression)s, each of them formulating one single constraint, e.g., (?var > DECIMAL)
            
            assert isinstance(entity, mediatorTools._Entity), "Entity expected, got {}".format(type(entity))
            assert isinstance(sparql_tree, ParseStruct), "Parsed sparql tree expected, got {}".format(type(sparql_tree))
            assert sparql_tree != None or sparql_var_name != '', "Both parsed sparql tree and sparql variable required, but none found."
            filterElements = sparql_tree.searchElements(label="constraint")
            assert len(filterElements) == 1, "Do not support more than one FILTER clauses ({} found) in SPARQL (yet, please implement me)".format(len(filterElements))
            if filterElements == []:
                warnings.warn('Cannot find [FILTER] node in the sparql tree; constraint other than type <Filter> not yet implemented')
            else:
                self._entity = entity
                nodeType = SPARQLParser.Var   
                for fe in filterElements:
#                     print("Searching for <{}> as type <{}> in {}: ".format(sparql_var_name, nodeType, fe))
                    # Find the [ValueLogical](s) in this FILTER clause that address the variable, by searching for nodes: 
                    # 1 - of type 'SPARQLParser.Var', and 
                    # 2 - having a value that equals the variable name
                    # The variable can occur in more than one value logic expression, hence expect at least one node
                    varElements = fe.searchElements(element_type=nodeType, value=sparql_var_name)
                    if varElements == []:
                        warnings.warn('Cannot find <{}> as part of a [{}] expression in <{}>'.format(sparql_var_name, nodeType, fe))
                    else:
                        # We have found at least one such value logic expression, hence start to build it
                        self._boundVar = sparql_var_name
                        for ve in varElements:
#                             print ("var element:", ve)
                            vlExpr = self.ValueLogicExpression(variable_node=ve)
#                             print ("value logic expression: {}".format(vlExpr))
                            if vlExpr: self._valueLogicExprList.append(vlExpr)
        #                     print("Elaborating on valueLogic: ", v)
                    if len(self._valueLogicExprList) == 0:
                        warnings.warn('No applicable constraints (Query Modifiers) found for <{}>'.format(sparql_var_name))

        def getValueLogicExpressions(self):
            return self._valueLogicExprList
        
        def getBoundVar(self):
            return self._boundVar
        
        def getEntity(self):
            return self._entity
        
        def __str__(self):
            result = ''
            for vl in self.getValueLogicExpressions():
                #TODO: __str__() turn it into comma separated list of elements, as opposed to ( element ) ( element ) ...
                result += '( '+ str(vl) + ' ) '
            return(result)

        def render(self):
            print('constraints: \n' + self.__str__())


    def __init__(self, entity_type=SPARQLParser.IRIREF, *, entity_expression, sparqlTree, nsMgr ):
        '''
        Generate the sparql context that is associated with the EntityExpression. If no entity_type is given, assume an IRI type.
        Returns the context, contained in attributes:
        * entity_expr  : (mediator.mediatorTools.EntityExpression) the subject EntityExpression that this context is about (from input)
        * parsedQuery  : (ParseStruct) the parsed sparql-query-tree that requires translation (from input)
        * qptAssocs    : the query pattern triples in the sparql query that are associated by the subject EntityExpression
        * constraints  : a list of the bound variables that occur in the qptAssocs, and for which a constraint in the sparql Query Pattern FILTER exists
        
        '''
        self.entity_expr = ''    # (mediator.mediatorTools.EntityExpression) The EDOAL entity_expression, i.e., one of (Class, Property, Relation, Instance) or their combinations, this context is about;
        self.parsedQuery = ''    # (parser.grammar.ParseInfo) The parsed query that is to be mediated
        self.qptAssocs = []      # List of (QueryPatternTripleAssociation)s, representing the triples that are addressing the subject entity_expression
        self.constraints = {}    # Dictionary, indexed by the bound variables that occur in the qptAssocs, as contextualised Filters.
        self.nsMgr = None        # (namespaces.NSManager): the current nsMgr that can resolve any namespace issues of this mediator 
        
#         assert isinstance(entity_expression, Mediator.EntityExpression) and isinstance(sparqlTree, ParseStruct)
        assert isinstance(sparqlTree, ParseStruct) and isinstance(nsMgr, NSManager), "Context.VarConstraints.__init__(): Parsed sparql tree and namespace mgr required"
        assert isinstance(entity_expression, mediatorTools.EntityExpression), "Context.VarConstraints.__init__(): Cannot create context without subject entity expression"
        
        if not entity_expression.isAtomicEntity(): raise NotImplementedError("Context.VarConstraints.__init__(): Cannot process entity expressions yet, only simple entities. Got {}".format(entity_expression.getType()))

        self.nsMgr = nsMgr
#         print("Context.VarConstraints.__init__(): entity expr: {}".format(entity_expression))
        self.entity_expr = entity_expression
        #TODO: process other sparqlData than sparql query, i.e., rdf triples or graph, and sparql result sets
        self.parsedQuery = sparqlTree
        if self.parsedQuery == []:
            raise RuntimeError("Context.VarConstraints.__init__(): Cannot parse the query sparqlData")
        
        eePf, eeIri, eeTag = self.nsMgr.splitIri(self.entity_expr.getIriRef())
        src_qname = eePf + ':' + eeTag
#         print("Context.VarConstraints.__init__(): eeIri: {}".format(eeIri))
#         print("Context.VarConstraints.__init__(): eePf : {}".format(eePf))
#         print("Context.VarConstraints.__init__(): eeTag: {}".format(eeTag))
#         print("Context.VarConstraints.__init__(): eeOrg: {}".format(self.entity_expr.getIriRef()))
#         print("Context.VarConstraints.__init__(): entity type {}".format(entity_type))
        
        # 1: Find the qptRefs for which the context is to be build, matching the Entity1 Name and its Type
        srcNodes = self.parsedQuery.searchElements(element_type=entity_type, value=self.entity_expr.getIriRef())
        if srcNodes == []: 
            raise RuntimeError("Context.VarConstraints.__init__(): Cannot find element '{}' of type '{}' in sparqlData".format(self.entity_expr.getIriRef(), entity_type))
        
        # 2: Build the context
        self.qptAssocs = []         # List of (QPTripleRef)s that address the edoal entity_iri.
#         self.qmNodes = {}           # a dictionary, indexed by the qp.about, i.e., the name of the EntityExpression, of lists of constraints 
                                    # that appear in the Query Modifiers clause, each list indexed by the variable name that is bound
        # 2.1: First build the Query Pattern Triples
        # 2.1.1: Find the top of the query's Query Pattern

            
        # 2.1.2: For each node, find the qptAssocs
        for qrySrcNode in srcNodes:
            # Find and store the QueryPatternTripleAssociation of the main Node
#             print("Context.VarConstraints.__init__(): Building context for {}".format(qrySrcNode))
#             print('='*30)
            qpt = self.QueryPatternTripleAssociation(entity_expression=self.entity_expr, sparql_tree=self.parsedQuery, nsMgr=self.nsMgr)
            qpt.addQPTRef(qrySrcNode)
            self.qptAssocs.append(qpt)
#             print("Context.VarConstraints.__init__(): QP triple(s) determined: \n\t", self.qptAssocs.__repr__())
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
        filterTop = self.parsedQuery.searchElements(element_type=SPARQLParser.GraphPatternNotTriples)
        if filterTop == []:
            raise RuntimeError("Context.VarConstraints.__init__(): Cannot find Query Modifiers clause (Filter)")
#             print('Top for QM part of tree:')
#             print(filterTop.dump())
        # 2.2.2 - for each bound variable in the qp, collect the ValueLogics that represent its constraint
        for qpt in self.qptAssocs:
            for qpNode in qpt.qptRefs:
                for var in qpNode.binds:
                    # Find the ValueLogicExpression that addresses this variable
                    self.constraints[str(var)] = []
#                     print("Context.VarConstraints.__init__(): Elaborating on var <{}>".format(str(var)))
#                     print('='*30)
                    # 3 - determine and store its value logics
                    # Cycle over every FILTER subtree
                    for filter in filterTop:
                        vc = self.VarConstraints(sparql_tree=filter, sparql_var_name=str(var), entity = self.entity_expr)
                        self.constraints[str(var)].append(vc)


    def __str__(self):
        result = "<entity>: " + str(self.entity_expr) + "\n\thas nodes:"
        for qpt in self.qptAssocs:
            result += "\n\t-> " + str(qpt) 
        result += "\n\thas var constraints:"
        for vc in self.constraints:
            result += "\n\t-> " + str(vc) + ": "
            for vl in self.constraints[vc]:
                result += "\n\t\t " + str(vl)
        return(result)
        
    def render(self):
        print(self.__str__())
            
    def getSparqlElements(self):
        result = []
        print("Context.VarConstraints.getSparqlElements(): NOT IMPLEMENTED: Searching for sparql elements that are associated with <{}>".format(self.entity_expr))
        return(result)


class sparqlQueryResultSet(): 
    '''
    This class represents a sparql query result set, i.e., as specified by https://www.w3.org/TR/sparql11-overview/#sparql11-results
    In principle all four different formats should be supported (XML, JSON, CSV and TSV). Currently, only a JSON parser is supported.
    '''
    def __init__(self, result_set=None):
        '''
        Create a sparql result set object from the input string.
        * input: a string that represents a sparql result set. Currently only a JSON-formatted string is supported.
        '''
        if isinstance(result_set, dict):
            assert "head" in result_set, "sparqlTools.sparqlQueryResultSet(): Cannot parse unknown dictionary structure, got {}".format(result_set)
            # Assume dictionary is structured according to query-result-set specification
            self.qResult = result_set
        elif isinstance(result_set, str):
            # Establish format by trying XML and JSON parser
            try:
                root = ElementTree.fromstring(result_set)
                #TODO: Parse XML-format
                raise NotImplementedError("sparqlTools.sparqlQueryResultSet(): Cannot parse an XML-formatted result string (yet, please implement  me)")
            except ParseError:
                try:
                    self.qResult = json.loads(result_set)
                except JSONDecodeError as err:
                    raise NotImplementedError("sparqlTools.sparqlQueryResultSet(): Cannot parse query result set formatted as CSV or TSV (yet, please implement me")
        else:
            raise NotImplementedError("sparqlTools.sparqlQueryResultSet(): Cannot parse query result set formatted other than string or dict, got {}".format(type(result_set)))
        # Parse the (json) dict
        assert "head" in self.qResult, "sparqlTools.sparqlQueryResultSet(): label 'head' expected in sparql result set, none found"
#         print("sparqlQueryResultSet.init(): head reads '{}' ({})".format(self.qResult["head"], len(self.qResult["head"])))
        if len(self.qResult["head"]) > 0:
            # Result set is response from SELECT query
            self.qType = 'SELECT'
            self.vars = self.qResult["head"]["vars"]
            self.bindings = self.qResult["results"]["bindings"]
        else:
            # Result set is response from ASK query
            self.qType = 'ASK'
            self.boolean = self.qResult["boolean"]

    def __repr__(self):
        if self.qType == 'ASK':
            return str(self.qType, self.boolean)
        elif self.qType == 'SELECT':
            return str(self.qType, self.vars, self.bindings)
        else:
            # Unknown type, hence return what is known...
            return str(self.qType, self.qResult)
        
