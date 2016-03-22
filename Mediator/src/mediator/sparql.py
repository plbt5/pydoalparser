'''
Created on 22 mrt. 2016

@author: brandtp
'''

from sparqlparser.grammar import *
from builtins import str

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
    
    
def getBGPs(e):
    '''
    input: e: (part of) a parsed sparql query that encompasses its Query Pattern.
    returns: a list of all BGPs that are present in that Query Pattern.
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

                # Each verb can have more than one object, zipping couples each verb with its objects
                for (verb, objects) in zip(verbPaths, objectsPaths):
                    # Get the terminator in the VerbPath branch as the property
                    prop = searchForType(verb, [TYPE_kw, PNAME_LN])
                    if not prop: raise NotImplementedError("property expected but not found!")
                    
                    # 3 - find at least one object (obj) for this property
                    # The mandatory obj is part of the objectListPath, 
                    # the optional obj's can be part of the objectListPath or objectList
                    if isinstance(objects, ObjectListPath):
                        # An ObjectListPath contains at least one object for this property
                        objs = searchForType(objects, [VAR1, VAR2, PNAME_LN])
                        if not objs: raise NotImplementedError("object expected but not found!")
                        for objct in objs: 
                            # Get the terminator in the Object branch as the object
                            obj = searchForType(objct, [VAR1, VAR2, PNAME_LN])
                            if not obj: raise NotImplementedError("object expected but not found!")
                            # Now we have a complete BGP, hence create it and push it to the results
                            bgp = BGP(sub, prop, obj)
                            result.append(bgp)
#                             print(bgp)
                    elif isinstance(objects, ObjectList):
                        # An ObjectList may contain zero or more objects for this property
                        objs = objects.searchElements(element_type=Object, labeledOnly=False)
                        for objct in objs: 
                            # Get the terminator in the Object branch as the object
                            obj = searchForType(objct, [VAR1, VAR2])
                            if not obj: raise NotImplementedError("object expected but not found!")
                            # Now we have a complete BGP, hence create it and push it to the results
                            bgp = BGP(sub, prop, obj)
                            result.append(bgp)
#                             print(bgp)
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
    elif (type(pattern) is str) or (type(pattern) is list):
        # Search for stand-alone element
        pass
    else: raise TypeError('Can only search for patterns of type {}, {} or {}, but found {}'.format(BGP, str, int, type(pattern)))
    return result
