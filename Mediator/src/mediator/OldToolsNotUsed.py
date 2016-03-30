'''
Created on 30 mrt. 2016

@author: brandtp
'''

from sparqlparser.grammar import *
from rdflib import Graph, BNode, Variable, URIRef, Namespace
from distutils.dist import warnings
from rdflib.namespace import RDF,RDFS

class AssociationGraph(Graph):
    '''
    Represents a structure that associates all nodes in a sparql query in a way that is related to mediation.
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
    
        
    class AGBNode():   
        def __init__(self, g):
            self.graph = g
            self.node = BNode()
        
        def bind(self, sparqlNode):
            sub = sparqlNode.getChildren()
            if sub == []:
                raise RuntimeError("Sparql node <{}> unexpectedly appears child-less; impossible to proceed".format(sparqlNode))
            for s in sub:
                sType = type(s).__name__
                if sType == 'VarOrTerm':
                    atom = s.descend()
                    if atom.isAtom():
                        # Add the Binds statement:
                        self.graph.add((self.node, URIRef(AssociationGraph.mns[self.graph.uris['binds']]), Literal(atom)))
                else: warnings.warn("Cannot yet create a bind statement for <{}> resources".format(sType)) # It may even be an ERROR

        
    def __makeAboutStatement(self, sparqlNode):
        atom = sparqlNode.descend()
        # Create the sparql tree node as term in the overlay association graph
        if atom.isAtom():
            # Add statement (2)
# #             self.mns.spo = Literal(self.mns[str(self.uris[term])])
#             self.mns.spo = URIRef(self.mns[self.uris[term]])
#             self.add((self.mns.entity, URIRef(self.mns[self.uris['appearsAs']]), self.mns.spo))
            # Add statement (1)
            sparqlTreeNode = Literal(atom)
            self.add((self.mns.spo, RDF.about, sparqlTreeNode))
        else: warnings.warn("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))
        return(atom)
       
        
    def __init__(self, edoalEntity=None, sparqlData=None, *, entity_type=iri):
        '''
        Constructor
        '''
        super().__init__()
        self.bind('mns', URIRef(self.mns))

        if (edoalEntity==None or sparqlData==None):
            raise ValueError("Edoal entity and sparqlData required")
        
        #TODO: process other sparqlData than sparql query, i.e., rdf triples or graph, and sparql result sets
        r = parseQuery(sparqlData)
        if r == []:
            raise RuntimeError("Cannot parse the query sparqlData")
            
        qryPatterns = r.searchElements(element_type=WhereClause)
        if qryPatterns == []:
            raise RuntimeError("Cannot find WHERE-clause")
        
        print(r.dump())
        #TODO: get the namespace from somewhere, don't assume 'ns:'
        val = 'ns:'+edoalEntity.split("#")[-1]
        print(val, entity_type)
        srcNodes = r.searchElements(element_type=entity_type, value=val, labeledOnly = False)
        print("Building context for <{}>".format(srcNodes))

        if srcNodes == []: 
            raise RuntimeError("Cannot find element <{}> of type <{}> in sparqlData".format(val, entity_type))            
        
        # Prepare the association graph; add statement "mynamespace:<this_EDOAL_entity> isA Class".
        # I'm not sure how relevant this statement will show...
        self.add((self.mns.entity, RDF.type, RDFS.Class))
        
        for qryElmtNode in srcNodes:
            # Build the two statements that form the anchor into the sparql graph:
            # 1: "mynamespace:<this_EDOAL_entity> mynamespace:appearsAs <S|P|O>"
            # 2: "<S|P|O> rdf:about <qryElmtNode>"
            # theoretically, the first statement (1) can occur multiple times. For each (1) there is only one (2)
            
            # Create statement (1); since the BGP-position is not yet known, use a temporary Blank Node
            SPONode = self.AGBNode(self)
            appearsAs = URIRef(self.mns[self.uris['appearsAs']])
            entityNode = Literal(edoalEntity)
            self.add((entityNode, appearsAs, SPONode.node))
            
            term = None
            
            # Second: identify the type of object qryElmtNode that must be created for each statement (1)
            pp = qryElmtNode.getAncestors(r)
            for p in pp:
                nType = type(p).__name__
                if nType == 'TriplesSameSubjectPath':
                    if term == None:
                        # Process first parent, i.e., srcNode represents a subject
                        term = 'subject'
                        print("Found <{}>, type <{}>".format(p, nType))
                        # Now add statement (1), which is a modification of an already existing statement
                        SPONode.node = URIRef(self.mns[self.uris[term]])
                        self.set((entityNode, appearsAs, SPONode.node))
                        # Now add the statements (2)
                        atom = p.descend()
                        if atom.isAtom():
                            aNode = Literal(atom)
                            self.add((SPONode.node, RDF.about, aNode))
                        else: warnings.warn("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))
                    elif term == 'object':
                        # This is the grandparent of the srcNode (object), hence bind srcNode to this subject
                        SPONode.bind(p) 
                    elif term == 'property': 
                        # This is the grandparent of the srcNode (a property). Irrelevant?
                        warnings.warn("Found <{}> as grandparent of property; considered irrelevant to include in the overlay Graph(?)".format(p))
                    break
                elif nType == 'ObjectListPath':
                    term = 'object'
                    print("Found <{}>, type <{}>".format(p, nType))
                    # Now add statement (1), which is a modification of an already existing statement
                    SPONode.node = URIRef(self.mns[self.uris[term]])
                    self.set((entityNode, appearsAs, SPONode.node))
                    # Now add statement (2)
                    atom = p.descend()
                    if atom.isAtom():
                        aNode = Literal(atom)
                        self.add((SPONode.node, RDF.about, aNode))
                    else: warnings.warn("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))
                    # Continue, and find binding with its subject
                elif nType == 'VerbPath':
                    term = 'property'
                    print("Found <{}>, type <{}>".format(p, nType))
                    # Now add statement (1), which is a modification of an already existing statement
                    SPONode.node = URIRef(self.mns[self.uris[term]])
                    self.set((entityNode, appearsAs, SPONode.node))
                    # Now add statement (2)
                    atom = p.descend()
                    if atom.isAtom():
                        aNode = Literal(atom)
                        self.add((SPONode.node, RDF.about, aNode))
                    else: warnings.warn("Sparql node unexpectedly appears parent of more than one atomic path. Found <{}> with siblings. Hell will break loose".format(atom))
                    break
                elif nType == 'PropertyListPathNotEmpty':
                    if term == 'property':
                        # Child of this qryElmtNode was a property, hence process the object
                        #TODO: Implement the processing of the object of the triple in the overlay graph
                        warnings.warn("Found <{}>: processing object not yet implemented. All hell will break loose?!".format(p))
                    elif term == 'object':
                        # Child of this qryElmtNode was an object, hence process the property
                        warnings.warn("Found <{}> as property and considered irrelevant to include in the overlay Graph".format(p))
                        pass # Properties are Not Applicable Yet
                    print("Found <{}>, type <{}>".format(p, nType))
                    # Now add the statements (1) and (2)
                 

                # Determine the sparql atomic element type and add that as statement to the graph
#                 nType = type(atom).__name__
#                 if nType == 'TYPE_kw':
#                     print("Found {} as type for {}".format(nType, atom))
#                     mns.rdfTerm = RDF.type
#                 elif nType == 'PNAME_LN':
#                     print("Found {} as type for {}".format(nType, atom))
#                     mns.rdfTerm = URIRef(str(atom))
#                 elif nType == 'VAR1' or nType == 'VAR2':
#                     print("Found {} as type for {}".format(nType, atom))
#                     mns.rdfTerm = Literal(str(atom))
#                 else: raise NotImplementedError("Cannot yet create an RDF qryElmtNode of type {}".nType)
#                 
#                 # Add this information to the new graph
#                 self.add((mns.edoalEntity, RDF.datatype, mns.rdfTerm))
            

            print("Got qryElmtNode of type <{}>: {}".format(term, self.mns.rdfNode))
                    
    
    def getSparqlElements(self, edoalEntity):
        result = []
        prop = URIRef(self.mns[self.uris['appearsAs']])
        print("Searching for <{}> with property <{}>".format(edoalEntity,prop))
        tuples = self.predicate_objects()
        for p,o in tuples:
            print ("Found tuple: ({},{})".format(p,o))
        for s in self.subjects():
            print ("Found subject: {}".format(s))
        for o in self.objects(subject=edoalEntity):
            print ("Found object: {}".format(o))
            for sparqlEl in self.objects(o, RDF.about):
                print ("{} associates {}".format(o,sparqlEl))
                result.append(sparqlEl)
        return(result)
    
    
    


 
class BGP(object):
    '''
    A tool to support a Basic Graph Pattern (s, p, o)
    '''

    def __init__(self, s, p, o):
        '''
        Constructor
        '''
        self.add(s, p, o)
        
    def __str__(self):
        return (str(self.s) + " " + str(self.p) + " " + str(self.o))
    
    def render(self):
        return str(self)
    
    def addS(self, s):
        self.s = s
    
    def addP(self, p):
        self.p = p
        
    def addO(self, o):
        self.o = o
        
    def add(self, s, p, o):
        self.addS(s)
        self.addP(p)
        self.addO(o)

def searchForType(e, typeList):
    for t in typeList:
        ok = e.searchElements(element_type=t, labeledOnly=False)
        if ok: return(ok)
    return(None)

def makeRDFNode(p):
    t = type(p[0]).__name__
    if t in ["VAR1", "VAR2"]:
        return Variable(str(p[0]))
    elif t in ["PNAME_LN"]:
        return URIRef(str(p[0]))
    elif t in ["TYPE_kw"]:
        return BNode(RDF.type)
    else: raise NotImplementedError("Found unknown type: {}".format(t))
    
    
def getBGPs(e):
    '''
    input: e: (part of) a parsed sparql query that encompasses its Query Pattern.
    returns: a list of all BGPs that are present in that Query Pattern.
    '''
    DEBUG=False
    
    # Validate the input; must be pointing at the Query Pattern
    triplesBlocks = None
    if (type(e) in [WhereClause, SelectQuery, ConstructQuery, AskQuery, Query, QueryUnit]):
        triplesBlocks = e.searchElements(element_type=TriplesBlock, labeledOnly=False)
    elif type(e) is TriplesBlock:
        triplesBlocks = e
    
    if not triplesBlocks:
        raise NotImplementedError('TriplesBlock expected but not found!')
    
    # Initialise the result
    result = Graph()
#     result = []
    
    # For each triplesBlock
    for tb in triplesBlocks:
        # Search for TriplesSameSubjectPaths, which contain the BGPs
        tripleSSubPaths = tb.searchElements(element_type=TriplesSameSubjectPath, labeledOnly=False)
        if not tripleSSubPaths: raise NotImplementedError('TriplesSameSubjectPath expected but not found!')

        # For each TripleSameSubjectPath: 
        # 1 - find the subject (sub)
        # 2 - find one or more properties (prop) that belong to this subject, and 
        # 3 - find at least one object (objects) for each property
        for tssp in tripleSSubPaths:  
            # 1 - find the subject (sub)       
            vots = tssp.searchElements(element_type=VarOrTerm, labeledOnly=False)
            if not vots:
                raise NotImplementedError("VarOrTerm expected but not found!")
            
            # The triple subject is the first VarOrTerm encountered in the TripleSameSubjectPath
            vot = vots[0]
            sub = searchForType(vot, [VAR1, VAR2, PNAME_LN])  # The terminator in this branch is the subject
            if not sub: raise NotImplementedError("subject expected but not found!")
            
            # 2 - find one or more properties (prop) that belong to this subject
            # Get the PropertyListPath in this TripleSameSubjectPath. This contains the properties.
            propListPathNE = tssp.searchElements(element_type=PropertyListPathNotEmpty, labeledOnly=False)
            if not propListPathNE: raise NotImplementedError("PropertyListPathNotEmpty expected but not found!")

            # Each "part" in the PropertyListPathNotEmpty contains a single property and its objects
            for propListPart in propListPathNE:
                # Each VerbPath in the "part" contains a property
                verbPaths = propListPart.searchElements(element_type=VerbPath, labeledOnly=False)
                if not verbPaths: raise NotImplementedError("VerbPath(s) expected but none found!")
                
                # The "part's" ObjectListPath contains the first object, belonging to the first VerbPath
                objectListPath = propListPart.searchElements(element_type=ObjectListPath, labeledOnly=False)
                if not objectListPath: raise NotImplementedError("ObjectListPath expected but not found!")
                
                # The "part's" ObjectList, if any, contains the other object, belonging to the other VerbPath(s)
                objectList = propListPart.searchElements(element_type=ObjectList, labeledOnly=False)                            
                objectsPaths = objectListPath + objectList
                zippedPair = zip(verbPaths, objectsPaths)
                
                if DEBUG: warnings.warn("zipped verb,object: {}".format(str(zippedPair)))

                # Each verb can have more than one object, zipping couples each verb with its objects
                for (verb, objects) in zippedPair:
                    # Get the terminator in the VerbPath branch as the property
                    prop = searchForType(verb, [TYPE_kw, PNAME_LN])
                    if not prop: raise NotImplementedError("property expected but not found!")
                    
                    # 3 - find at least one object (obj) for this property
                    # The mandatory obj is part of the objectListPath, 
                    # the optional obj's can be part of the objectListPath or objectList
                    if isinstance(objects, ObjectListPath):
                        # An ObjectListPath contains at least one object for this property
                        objs = objects.searchElements(element_type=ObjectPath, labeledOnly=False)
                        if not objs: raise NotImplementedError("ObjectPath expected but not found!")
                        if DEBUG: warnings.warn("objects(OLP): {}".format(objs))
                        for objct in objs: 
                            # Get the terminator in the Object branch as the object
                            if DEBUG: warnings.warn("objct(OLP): {}".format(objct))
                            obj = searchForType(objct, [VAR1, VAR2, PNAME_LN])
                            if DEBUG: warnings.warn("obj(OLP): {}".format(obj))
                            if not obj: raise NotImplementedError("object expected but not found!")
                            # Now we have a complete BGP, hence create it and push it to the results
                            s = makeRDFNode(sub)
                            p = makeRDFNode(prop)
                            o = makeRDFNode(obj)
#                             bgp = BGP(sub, prop, obj)
#                             result.append(bgp)
                            result.add((s, p, o))
#                             if DEBUG: warnings.warn("BGP: {}".format(bgp))
                    elif isinstance(objects, ObjectList):
                        # An ObjectList may contain zero or more objects for this property
                        objs = objects.searchElements(element_type=Object, labeledOnly=False)
                        if not objs: raise NotImplementedError("Object expected but not found!")
                        if DEBUG: warnings.warn("objs(OL): {}".format(objs))
                        for objct in objs: 
                            # Get the terminator in the Object branch as the object
                            obj = searchForType(objct, [VAR1, VAR2])
                            if not obj: raise NotImplementedError("object expected but not found!")
                            # Now we have a complete BGP, hence create it and push it to the results
#                             bgp = BGP(sub, prop, obj)
#                             result.append(bgp)
                            s = makeRDFNode(sub)
                            p = makeRDFNode(prop)
                            o = makeRDFNode(obj)
                            result.add((s, p, o))
#                             if DEBUG: warnings.warn("BGP: {}".format(bgp))
                    else: raise TypeError("Type <ObjectList> or <ObjectListPath> expected but found {}".format(type(objects)))
                    
    return result
    
  
def searchInQuery(e, pattern):
    '''
    input: 
    * e: (part of) a parsed sparql query that contains its Query Pattern
    * pattern: the search pattern may be either a BGP (s, p, o) or a stand-alone element that represents any part of a BGP.
               A stand-alone element can be a string or a list. 
               Each of the BGP elements or the generic element may be None, representing a wildcard for the search.
    returns: a list of BGPs that match the search pattern 
    '''
    
    # Validate the input; must be pointing at the Query Pattern
    triplesBlocks = None
    if (type(e) in [WhereClause, SelectQuery, ConstructQuery, AskQuery, Query, QueryUnit]):
        triplesBlocks = e.searchElements(element_type=TriplesBlock, labeledOnly=False)
    elif type(e) is TriplesBlock:
        triplesBlocks = e
    
    if not triplesBlocks:
        raise NotImplementedError('TriplesBlock expected but not found!')
    
    # Initialise the result
    result = []
    
    # Determine whether the search is for a BGP or a stand-alone element
    if (type(pattern) is BGP):
        # Search for a BGP pattern
        pass
    elif (type(pattern) is str):
        # Search for stand-alone element
        for tp in triplesBlocks:
            els = tp.searchElements(value=pattern, labeledOnly=False)
            for el in els:
            
                result.append(el)
    elif (type(pattern) is list):
        # Search for stand-alone element
        pass
    else: raise TypeError('Can only search for patterns of type {}, {} or {}, but found {}'.format(BGP, str, int, type(pattern)))
    return result
