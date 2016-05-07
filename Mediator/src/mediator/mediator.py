'''
Created on 26 feb. 2016

@author: brandtp
'''


from parsertools.parsers.sparqlparser import parseQuery


class Mediator(object):
    '''
    The Mediator class performs translations of sparql queries or sparql variable bindings. This translation is based
    upon mappings from an alignment. Either a translation succeeds, resulting in a translated sparql query or variable binding, or
    fails. In the latter case the mediator provides information on the reason for failing, for other classes to proceed upon in
    a protocolised way of operation.
    '''
      
                                
    mediatorLabels = {
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


   
    def __init__(self, alignment):
        '''
        The mediator represents one complete EDOAL Alignment, as follows:
            self.nsMgr   : utilities.NSManager : a NamespaceManager that can keep track of the namespaces in use
                                and can convert between prefix and qnames and what have you
            self.about   : string              : the name of this mediator (sourced from the alignment)
            self.corrs   : Dictionary          : Dictionary of Correspondences, indexed by name of the correspondence
        '''
        self.nsMgr = alignment.nsMgr
        self.about = alignment.getAbout()
        self.corrs = alignment.getCorrespondences()
        
    def getNSs(self):
        return(str(self.nsMgr))
            
    def translate(self,data):
        '''
        Translate the data according to the EDOAL alignment cells that are stored in correspondence objects
        - data (sparql query as string): the data to be translated; this data can represent one out of the following
            1: a sparql query (one of: SELECT, ASK, UPDATE, DESCRIBE)
            2: a sparql result set
            3: an RDF triple or RDF graph
        returns: the translated data, in the same rendering as received
        
        As of this moment, only a SPARQL SELECT is supported
        '''
        # Process:
        # 1 - parse sparlq data
        # 2 - add namespaces that are used in the sparql query to the namespaceManager
        # 3 - translate the query, by changing (in place) the iri's and data values as 
        #     specified in the correspondences
        assert data != None and isinstance(data, str) and data != '' 
        rq = parseQuery(data)
        if rq == []:
            raise RuntimeError("Couldn't parse the following query:\n{}".format(data))
        self.nsMgr.bindPrefixesFrom(rq)
        rq.render()
        for corr in self.corrs:
#             print(corr)
            print(corr.translate(rq))
            
    def __len__(self):
        '''
        Calculates the length of the Mediator as the amount of Correspondences it contains.
        '''
        return len(self.corrs)     
    
    def getName(self):
        '''
        Retrieves the name of this Mediator, which reifies the Alignment's "about" attribute.
        '''
        return self.about
     
    def render(self):
        '''
        Produce a rendering of the Mediator 
        '''
        #TODO: Produce a rendering of the Mediator in EDOAL XML
        s = self.__str__()
        for k, v in sorted(self.corrs.items()):
            s += v.render()
        return s
    
    def __str__(self):
        return self.getName() + ' (onto1: ' + self.onto1.find(str(self.nsMgr.asClarks(':Ontology'))).get(str(self.nsMgr.asClarks('rdf:about'))) + \
            ' onto2: ' + self.onto2.find(str(self.nsMgr.asClarks(':Ontology'))).get(str(self.nsMgr.asClarks('rdf:about'))) + ')'
    
if __name__ == '__main__':
    print('running main')


