'''
Created on 26 feb. 2016

@author: brandtp
'''

from EdoalParser.alignment import Alignment
from sparqlparser.grammar import SPARQLElement

'''
conflictType represents the different types of semantic conflict that can be distinguished:
- None:    No conflict
- Dinges:    Another conflict, no idea yet
'''
conflictType = ['None', 'Dinges']
#TODO: Specifying the various conflictTypes

class SemanticConflict(object):
    '''
    An SemanticConflict object will be created during data translation whenever the translation cannot
    guarantee the semantic correctness of the translation.  
    '''
    
    def __init__(self):
        self.type = {}

class VarBounding(object):
    '''
    '''
    def __init__(self):
        pass

class Query(SPARQLElement):
    '''
    '''
    def __init__(self):
        pass
    
class Mediator(object):
    '''
    The Mediator class performs translations of sparql queries or sparql variable bindings. This translation is based
    upon mappings from an alignment. Either a translation succeeds, resulting in a translated sparql query or variable binding, or
    fails. In the latter case the mediator provides information on the reason for failing, for other classes to proceed upon in
    a protocolised way of operation.
    '''

    def __init__(self, align, ontoA, ontoB):
        '''
        The Mediator can be initialized with, at a minimum, an Alignment object. In addition, the two
        ontologies to mediate between can be provided as Ontology object. Prerequisite: These Ontologies must be
        the same as defined in the Alignment object, otherwise an error will be raised.
        '''
        
        if align == None or type(align) != Alignment:
            raise AttributeError
        else:
            self.align = align
            self.ontoA = self.ontoB = None
            #TODO: provide for addition of ontoA and ontoB in the Mediator
            

    def getName(self):
        '''
        Retrieves the name of this Mediator, which reifies the Alignment's "about" attribute.
        '''
        return self.align.about
     
    def translate(self, data, inPlace = True):
        '''
        Translate the data according to the Alignment this mediator addresses. The data might 
        either represent a Sparql variable bounding (represented by a VarBounding object) or a Sparql 
        Query (represented by a Query object).
        The inPlace parameter is optional, defaulting to True, making for an in-place translation. On
        specifying inPlace = False, a new object will be created of type(data), leaving the original source
        data unchanged. The newly, translated, data will be stored in the original data parameter, hence reference
        to the original data will be lost.
        Whenever issues occur during translations, the method returns an Issue object, or True otherwise.
        Prerequisite: the data is expected to adhere to the Alignment; if not, e.g., an entity expression is 
        specified that is missing in the Alignment, an error will be raised.
        '''
        if data == None or (type(data) != VarBounding and type(data) != Query):
            raise AttributeError
        else:
            return False
     