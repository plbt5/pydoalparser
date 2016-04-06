'''
Created on 30 mrt. 2016

@author: brandtp
'''

from sparqlparser.grammar import *
from rdflib import Graph, BNode, Variable, URIRef, Namespace
from distutils.dist import warnings
from rdflib.namespace import RDF,RDFS


    
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
             
    class Correspondence():
   
        def __init__(self, el):
            '''
            Create a new Correspondence by copying the children from an EDOAL cell into the object's fields. 
            -> el (ET.element): should contain the 'xmlns:Cell' element of an EDOAL mapping
            Prerequisite: this EDOAL cell should contain the elements: <xmlns:entity1>, <xmlns:entity2>, and <xmlns:relation>
            
            Returns an object with fields:
            - .nme: (string) : the name of the correspondence (reification of rdf:about in <Cell>)
            - .src: (elementtree Element) : the source EntityExpression expression
            - .tgt: (elementtree Element) : the target EntityExpression expression
            - .rel: (string) : the EDOAL EntityExpression expression relation
            - .tfn: []       : List of translations for individuals of this source
                * {'direction'} : direction if this transformation
                * {'entity1'}   : (elementtree Element) : transformation details
                * {'entity2'}   : (elementtree Element) : transformation details
            ''' 
            self.nme = el.get(RDFABOUT)
            if self.nme == None: raise ValueError('XML attribute {} expected in element {}'.format(RDFABOUT, el.tag))
            
            self.src = el.find('xmlns:entity1', ns)
            if self.src == None: raise RuntimeError('Edoal element <xmlns:entity1> required')
            elif not (self.src[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST]):
                raise NotImplementedError('Only edoal EntityExpression type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.src["EntityExpression"]))

            self.tgt = el.find('xmlns:entity2', ns)
            if self.tgt == None: raise RuntimeError('Edoal element <xmlns:entity2> required')
            elif not ((self.tgt[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST])):
                raise NotImplementedError('Only edoal EntityExpression type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.tgt[0].tag.lower()))

            rel = el.find('xmlns:relation', ns)
            if rel == None: raise RuntimeError('Edoal element <xmlns:relation> required')
            else: self.rel = Mediator.canonical(rel.text)
            
            self.tfn = []
            tfns = el.findall('xmlns:transformation', ns)
            if tfns != None: # This part of the alignment is optional.
                for tfn in tfns:
                    Tfn = tfn.find('xmlns:Transformation', ns)
                    if Tfn == None: raise RuntimeError('Edoal element <xmlns:Transformation> expected')
                    self.tfn.append({'direction': Tfn.get(EDOALDIRECTION), 'entity1': Tfn.find('xmlns:entity1', ns) , 'entity2': Tfn.find('xmlns:entity2', ns)})
            
        def render(self):
            '''
                Produce a rendering of the Correspondence as EDOAL Map
            '''
            #TODO: Produce a rendering of the Correspondence in EDOAL XML
            e1 = ''
            e2 = ''
            t = ''
            for el in self.src.iter():
                e1 += '\t' + el.tag + str(el.attrib) + '\n'
            for el in self.tgt.iter():
                e2 += '\t' + el.tag + str(el.attrib) + '\n'
            for el in self.tfn:
                t += '\t' + str(el['direction']) + '\n\tentity1: ' + str(el['entity1']) + '\n\tentity2: ' + str(el['entity2']) + '\n'
            return self.getName() + '\n>>src:' + e1 + '>>tgt:' + e2 + '>>rel:' + self.rel + '\n>>tfn:' + t
        
        def getName(self):
            return self.nme
        
        def __str__(self):
            return self.getName()
         
        def translate(self, data):
            '''
            Translate the data according to the EDOAL alignment from the Correspondence Class
            - data (string): the data to be translated; this data can represent one out of the following
                1: a sparql query (one of: SELECT, ASK, UPDATE, DESCRIBE)
                2: a sparql result set
                3: an RDF triple or RDF graph
            returns: the translated data, in the same rendering as received
            
            As of this moment, only data of type 1 is supported, and even then only SELECT
            '''
            
            print(self.render())
            if self.rel != 'EQ':
                #TODO: Translate entity expressions LT, GT and ClassConstraints
                raise NotImplementedError('Only entity expression relations of type "EQ" supported')
            elif (len(list(self.src.iter())) > 2):
                # Classrestriction: <AttributeValueRestriction> onatt comp val </AttributeValueRestriction>
                
                if (self.src[0].tag.lower() == EDOALCLASS):
                    if (self.src[0].get(RDFABOUT) == None):
                        # Complex Boolean Class Construct found
                        raise NotImplementedError('Complex Boolean Edoal Class constructs not supported')
                    else:
                        # Simple Class Entity found; hand over to the simple entity EQ translation
                        print("Implementation required to translate {}".format(self.src[0].tag))
                        
                elif (self.src[0].tag.lower() in [EDOALCAOR, EDOALCADR, EDOALCATR, EDOALCAVR]):
                    # Complex Class Restriction found
                    
                    raise NotImplementedError('Complex Class Restriction found, under construction')
                else: raise NotImplementedError('For complex entity expressions, only class restrictions supported')
            
            elif (len(list(self.tgt.iter())) > 2):
                raise NotImplementedError('Only simple entity2 expressions supported')
            elif not ((self.src[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST]) and \
                    (self.tgt[0].tag.lower() in [EDOALCLASS, EDOALPROP, EDOALRELN, EDOALINST])):
                raise KeyError('Only edoal entity type "Class", "Property", "Relation", and "Instance" supported; got {}'.format(self.src[0].tag.lower()))
            
            # EQ relation for simple entities found. 
            # Since this is a simple entity expression, get name of src (entity1) and tgt (entity2)
            src = list(self.src.iter())[1].get(RDFABOUT)
            tgt = list(self.tgt.iter())[1].get(RDFABOUT)
#             at = AssociationGraph(edoalEntity=src, sparqlData=data)
#             print("Association graph has {} statements:".format(len(at)))
#             print ((at.serialize(format='turtle')).decode("utf-8"))
            
            # Determine the sparql context for the src, i.e., in the parsed sparql tree, determine:
            # the Node(s), their binding(s) and their constraining expression(s)
            rq = parseQuery(data)
            context = Context(edoalEntity=src, sparqlData=data)
            
            context.render()
            print("translating {} ---> {}".format(src, tgt))

            # Change the src into the tgt. 
            # 1 - First the concepts in the Query Pattern part of the query.
            #     The src can occur in multiple BGP's, and each qpNode represents a distinct BGP
            for qpt in context.qpTriples:
                print("tgt:", tgt)
                #TODO: Namespace problem, resolve
                tgt = 'ToDoNS:'+tgt.split("#")[-1]
                print("src:", str(qpt.represents))
                print("tgt:", tgt)
                for qpn in qpt.qpNodes:
                    qpn.about.updateWith(tgt)
            # 2 - Then transform the constraints from the Query Modification part of the query.
            # 2.1 - Determine the edoal spec of the transformation; ASSUME simple transformation
            for transformation in self.tfn:
                for element in list(transformation['entity1']):    # TODO: better parser for EDOAL transformations/values et.al.
                    if element.tag == EDOALAPPLY:
                        operator = element.get(EDOALOPRTR)
                        value = operator.find('edoal:arguments/edoal:Property', ns).get(RDFABOUT)
                    else: warnings.warn("Do not yet support other transformation specifications than <{}>".format(EDOALAPPLY))
            #     The src can be bound to more than one variable that can have more constraints.
            #     The qmNodes in the context is a dictionary for which the src indexes a list of variables. 
            #     Each variable is represented by a qmNode; each constraint by a valueLogic.
            
            for key in context.qmNodes:
                for qm in context.qmNodes[key]:
                    for vl in qm.valueLogic:
                        vl['operand'].updateWith('100.0')
            
            context.parsedQuery.render()
            return True
    
    def __init__(self, edoal):
        '''
        The Mediator can be initialized with an EDOAL alignment.  
        - edoal : edoal expression, represented as ET.Element
                
        The mediator represents one complete EDOAL Alignment, as follows:
            self.ns      ::== dict with uri's as key and prefix as value
            self.about   ::== string
            self.creator ::== xml.etree.Element
            self.date    ::== xml.etree.Element
            self.method  ::== xml.etree.Element
            self.purpose ::== xml.etree.Element
            self.level   ::== string
            self.type    ::== string
            self.onto1   ::== xml.etree.Element
            self.onto2   ::== xml.etree.Element
            self.corrs ::== List of Correspondence
        '''
        #TODO: Consider other EDOAL levels than 2EDOAL only
        #TODO: Consider other alignments than EDOAL only, e.g., SPIN
        if edoal == None:
            raise TypeError('EDOAL expression expected')
        elif type(edoal) != ET.Element:
            raise TypeError('EDOAL expression of type {} expected'.format(type(ET.Element)))
        else:
            # Get the namespaces first, and plug them reversed into self
            self.ns = ns
            # Get the Alignment
            align = edoal.find('xmlns:Alignment', self.ns)
        
        if align == None: 
            raise RuntimeError('Cannot find required "xmlns:Alignment" element in XML-tree')
        else: t = align.get(RDFABOUT, default='')
        
        if (t == '') or (t == None): 
            raise ValueError('Alignment id as {} attribute expected'.format(RDFABOUT))
        else: self.about = t
        
        t = align.find('xmlns:level', self.ns)
        if t == None: raise RuntimeError('No alignment <level> element found in Alignment {}'.format(self.about))
        else: self.level = t.text
        if self.level != '2EDOAL': 
            raise NotImplementedError('Alignment level other than "2EDOAL" not supported; found {}'.format(self.level))
                
        self.creator = align.find('dc:creator', self.ns)
        self.date = align.find('dc:date', self.ns)
        self.method = align.find('xmlns:method', self.ns)
        self.purpose = align.find('xmlns:purpose', self.ns)
        t = align.find('xmlns:type', self.ns)
        
        if t == None: raise RuntimeError('Edoal element <xmlns:type> required; found {}'.format(t))
        else: self.type = t.text
        if not self.type in ['**', '?*', '*?', '??']:
            raise ValueError('Incorrect value of element <xmlns:type> required, Expected {}, found {}'.format('**, ?*, *?, ??', self.type))
        self.onto1 = align.find('xmlns:onto1', self.ns)
        self.onto2 = align.find('xmlns:onto2', self.ns)
        self.corrs = {}
        
        cells = align.findall('xmlns:map/xmlns:Cell', self.ns)

#         print('#cells', len(cells))
        if len(cells) == 0:
            raise RuntimeError('An Edoal alignment requires at least one <xmlns:map><xmlns:Cell>...</xmlns:Cell></xmlns:map> element, but zero found')
        for el in cells:
            c = self.Correspondence(el)
            self.corrs[c.getName()] = c
       

    def __len__(self):
        '''
        Calulates the length of the Mediator as the amount of Correspondences it contains.
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
        return self.getName() + ' (onto1: ' + self.onto1.find('xmlns:Ontology', self.ns).get(RDFABOUT) + \
            ' onto2: ' + self.onto2.find('xmlns:Ontology', self.ns).get(RDFABOUT) + ')'
    


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
       
        
    def __init__(self, EntityExpression=None, sparqlData=None, *, entity_type=iri):
        '''
        Constructor
        '''
        super().__init__()
        self.bind('mns', URIRef(self.mns))

        if (EntityExpression==None or sparqlData==None):
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
        val = 'ns:'+EntityExpression.split("#")[-1]
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
            entityNode = Literal(EntityExpression)
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
#                 self.add((mns.EntityExpression, RDF.datatype, mns.rdfTerm))
            

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
