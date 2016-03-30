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

from sparqlparser.grammar import *
from builtins import str
from distutils.dist import warnings
from rdflib import Namespace, URIRef



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
        BGPPos = ''        # the Basic Graph Pattern position of the node: <S|P|O>
        about = ''         # the atomic node in the sparql tree representing the node
        binds = []         # a list of variables that are bound by this node: <VAR1 | VAR2>
        
        def __init__(self, sparql_tree=None, query_node=None):
            # Now find the atom of the main Node, i.e., what this is all about, and store it
            if sparql_tree == None or query_node == None:
                raise RuntimeError("Both parsed sparql tree and sparql node required.")
            atom = query_node.descend()
            if atom.isAtom():
                self.about = atom
                print('-'*20)
                print("QP subject:", atom)
                print('-'*20)
                # HERE WE CAN DO A TRANSLATION OF THE NODE!!! 
            else: warnings.warn("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))

            # Identify the BGP position by searching the ancestor tree
            bgpPos = None
            pp = query_node.getAncestors(sparql_tree)
            for p in pp:
                nType = type(p).__name__
                if nType == 'TriplesSameSubjectPath':
                    if bgpPos == None:
                        # We are in a TSSP leg, AND, we didn't determine the bgpPos yet, hence the main Node represents a subject
                        bgpPos = 'subject'
                        self.BGPPos = URIRef(Context.mns[Context.uris[bgpPos]])
                        print("Found <{}> (type [{}]) as (S, -, -)".format(p, nType))
                        # Now process the children, except itself
                        for plp in p.getChildren():
                            if type(plp).__name__ == 'PropertyListPathNotEmpty':
                                for c in plp.getChildren():
                                    if type(c).__name__ == 'ObjectListPath':
                                        # Now in the branch leading to the variable 
                                        atom = c.descend()
                                        if atom.isAtom():
                                            self.binds.append(atom) 
                                        else: warnings.warn("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))
                            else: warnings.warn("Ignoring [{}] as child of [{}].".format(plp,p))
                        # Continue, and find binding with its object
                    elif bgpPos == 'object':
                        # We are in a TSSP leg, AND, we did determine the bgpPos already, hence 
                        # this is the grandparent of the main Node (object), hence this subject might be
                        # 1 - either a variable or BNode to bind
                        # 2 - or a URIRef  
                        #TODO: Check whether to discern between the type of TERM (BNode, URIREF, Literal)
                        for c in p.getChildren():
                            if type(c).__name__ == 'VarOrTerm':
                                # Now in the branch leading to the variable 
                                atom = c.descend()
                                if atom.isAtom():
                                    self.binds.append(atom) 
                                else: warnings.warn("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))
                            else: warnings.warn("Ignoring [{}] as child of [{}].".format(c,p))
                        # Continue, and find binding with potential other object(s)
                    elif bgpPos == 'property': 
                        # We are in a TSSP leg, AND, we did determine the bgpPos already, hence 
                        # this is the grandparent of the main Node (predicate). We ASSUME this is IRRELEVANT.
                        #TODO: Check whether the TSSP/subject is relevant to consider when the main Node is a predicate
                        warnings.warn("Found <{}> as grandparent of property; considered irrelevant to include in the overlay Graph(?)".format(p))
                        # Continue, but probably no more interesting stuff will be found.
                elif nType == 'ObjectListPath':
                    bgpPos = 'object'
                    self.BGPPos = URIRef(Context.mns[Context.uris[bgpPos]])
                    print("Found <{}>, type <{}>".format(p, nType))
                    # Continue, and find binding with its subject
                elif nType == 'VerbPath':
                    bgpPos = 'property'
                    self.BGPPos = URIRef(Context.mns[Context.uris[bgpPos]])
                    print("Found <{}>, type <{}>".format(p, nType))
                    # Continue, and find binding with its subject and object
                elif nType == 'PropertyListPathNotEmpty':
                    if bgpPos == 'property':
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
                    else: warnings.warn("Found PLPNE [{}];, however with unexpected bgpPos <{}>. This is an unforeseen branch that requires further study. All hell will break loose?!".format(p, bgpPos))
                elif nType == 'TriplesBlock':
                    # Since we are looking for the triple context of the main Node, we ASSUME we can stop here.
                    break
                else: warnings.warn("Unexpectedly found <{}> as ancestor to <{}>. This might be valid, but requires further study. All hell will break loose?!".format(nType, query_node))

        def __str__(self):
            result = "node:\n\tin BGP as : " + str(self.BGPPos) + "\n\tabout     : " + self.about.__repr__()
            for b in self.binds:
                result += "\n\tbinds     : " + b.__repr__()
            return(result)
                
    class QueryModifiers():
        boundVar = ''       # the name of the VarOrTerm that has been bounded in the QueryPatternTriple
        entity = ''         # the entity expression that this var has been bound to
        valueLogic = []     # the atomic node(s) in the QueryModifiers that represent the ValueLogic Term(s)
        
        class ValueLogic():
            
            def __init__(self, valLogs, f):
                for v in valLogs:
#                     print("Elaborating on valueLogic: ", v)
                    pp = v.getAncestors(f)
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
            if sparql_tree == None or sparqle_var == None:
                raise RuntimeError("Both parsed sparql tree and sparql var required.")
            elFilters= sparql_tree.searchElements(element_type=Filter)
            if elFilters == []:
                raise NotImplementedError('Constraint other than type <Filter> not yet implemented')
            
            # Find the var as part of a [ValueLogical] in this part of the tree
            tpe = Var
            for f in elFilters:
                print("Searching for <{}> as type <{}> in {}: ".format(sparqle_var, tpe, f))
                valLogs = f.searchElements(element_type=tpe, value=sparqle_var)
                if valLogs == []:
                    warnings.warn('Cannot find <{}> as part of a [{}] expression in <{}>'.format(sparqle_var, tpe, f))
                else:
                    self.boundVar = sparqle_var
                    for v in valLogs:
    #                     print("Elaborating on valueLogic: ", v)
                        pp = v.getAncestors(f)
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
                                    self.valueLogic.append({'varFirst': varFirst, 'operation': operation, 'operand': operand})
                                    break
    #                             elif pType == 'ConditionalAndExpression':
    #                                 for c in cc:
    #                                     print(">>\t<{}> is a [{}]".format(c, type(c).__name__))
    #                             else: 
    #                                 for c in cc:
    #                                     print(">>\t<{}> is a [{}]".format(c, type(c).__name__))
                            prevP = p
    #                         if pType == 'RelationalExpression':
    #                             pass
    #                         elif pType == 'ValueLogical':
    #                             print("<{}> is a [{}] with length <{}>".format(p, pType, len(p)))
    #                             pass
                if len(self.valueLogic) > 0:
                    self.render()
                else: print('No applicable Query Modifiers found for <{}>'.format(sparqle_var))

        def __str__(self):
            result = 'Constraints: \n' 
            for vl in self.valueLogic:
                if vl['varFirst']: result+= '\t' + self.boundVar + ' ' + str(vl['operation']) + ' ' + str(vl['operand'])
                else: result+= '\t' + str(vl['operand'] + ' ' + str(vl['operation']) + ' ' + self.boundVar)
            return(result)

        def render(self):
            print(self.__str__())


    def __init__(self, edoalEntity=None, sparqlData=None, *, entity_type=iri):
        '''
        Generate the sparql context that is associated with the edoalEntity. If no entity_type is given, assume an IRI type.
        Returns the context, with attributes:
        * entity       : the subject edoalEntity
        * parsedQuery  : the parsed sparql-query-tree
        * qpNodes      : the nodes from the sparql Query Pattern that are referred to in the edoalEntity
        * qmNodes      : the nodes from the sparql Query Modifiers that are related to the qpNodes 
        
        '''

        if (edoalEntity==None or sparqlData==None):
            raise ValueError("Edoal entity and sparqlData required")
        
        #TODO: process other sparqlData than sparql query, i.e., rdf triples or graph, and sparql result sets
        rq = parseQuery(sparqlData)
        if rq == []:
            raise RuntimeError("Cannot parse the query sparqlData")
        self.parsedQuery = rq
        
        qryPatterns = rq.searchElements(element_type=WhereClause)
        if qryPatterns == []:
            raise RuntimeError("Cannot find WHERE-clause")
        elif len(qryPatterns) > 1:
            raise NotImplementedError("Cannot yet process more than one WHERE-clause")
           
        for p in qryPatterns: 
            print(p.dump())
        #TODO: get the namespace from the sparqle query, don't assume 'ns:'
        val = 'ns:'+edoalEntity.split("#")[-1]
        
        # 1: Find the nodes for which the context is to be build, matching the Entity1 Name and its Type
        srcNodes = rq.searchElements(element_type=entity_type, value=val, labeledOnly = False)
        print("Building context for <{}>".format(srcNodes))
        if srcNodes == []: 
            raise RuntimeError("Cannot find element <{}> of type <{}> in sparqlData".format(val, entity_type))
        
        # 2: For each node, build the context
        self.qpNodes = []           # the main Node(s) that respond to this edoal entity; type sparqlparser.grammar.ParseInfo
        self.entity = edoalEntity   # 
        self.qmNodes = {}           # a dictionary, indexed by the qp.about, i.e., the name of the edoalEntity, of lists of constraints 
                                    # that appear in the Query Modifiers clause, each list indexed by the variable name that is bound
        
        for qrySrcNode in srcNodes:
            # Find and store the QueryPatternTriple of the main Node
            #TODO: Probably rq is too high in the tree - consider a lower node such as [WhereClause] (qryPatterns) or[GroupGraphPattern] 
            qp = self.QueryPatternTriple(sparql_tree=rq, query_node=qrySrcNode)
            self.qpNodes.append(qp)
            print("query pattern determined: \n", str(qp))
            # Find and store its constraints, hence:
            # (1 - Select the right node in the sparql tree) For now use rq
            
            #TODO: Assumed one [WhereClause] (hence, qryPatterns[0])  
            localTop = list(qryPatterns[0].searchElements(element_type=GraphPatternNotTriples))[0]
#             print('Top for QM part of tree:')
#             print(localTop.dump())
            #TODO: Assumed one [GraphPatternNotTriples] (hence, list(...)[0])  
            # 2 - for each bound variable in the qp,
            self.qmNodes[str(qp.about)] = []
            for var in qp.binds:
                print("Elaborating on var <{}>".format(str(var)))
                # 3 - determine and store its query modifiers
                print('key: ', str(qp.about).replace(':',''))
                qms = self.QueryModifiers(sparql_tree=localTop, sparqle_var=str(var))
                self.qmNodes[str(qp.about)].append(qms)    

    def __str__(self):
        result = "<entity1>: " + self.entity 
        for qp in self.qpNodes:
            result += "\n-> " + str(qp) + "\n-> " 
            for qm in self.qmNodes[str(qp.about)]:
                result += str(qp.about) + ' has ' + str(qm) 
        return(result)
        
    def render(self):
        print(self.__str__())
            
    def getSparqlElements(self):
        result = []
        print("Searching for sparql elements that are associated with <{}>".format(self.entity))
        return(result)
  
