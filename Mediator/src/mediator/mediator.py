'''
Created on 26 feb. 2016

@author: brandtp
'''


from parsertools.parsers.sparqlparser import parseQuery
from utilities import namespaces
from mediator import EDOALparser
import os.path
from builtins import str

class Mediator(object):
    '''
    The Mediator class mediates the semantic communication between a pair of interacting applications. To that end, it performs translations of sparql queries or sparql variable bindings. 
    This translation is based upon mappings from an alignment. Either a translation succeeds, resulting in a translated sparql query or variable binding, or
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

    class nsDict(dict):
        def __init__(self):
            super().__init__()
        def update(self, *args, **kwargs):
            return dict.update(self, *args, **kwargs)
   
    def __init__(self, nsDict={}, *, about=None):
        '''
        The mediator represents at least one complete EDOAL Alignment, as follows:
            self.nsMgr       : utilities.NSManager : a NamespaceManager that can keep track of the namespaces in use
                                and can convert between prefix and qnames and what have you
            self.about       : string              : the name of this mediator
            self.alignments  : Dict of Alignment   : Dictionary of Alignments, indexed by name of the alignment_element
        '''
        
        assert isinstance(about, str) and about != '', "Mediator requires an ID"
        mediatorNSs = { 'med'   : 'http://ts.tno.nl/mediator/1.0/',
                'medtfn': 'http://ts.tno.nl/mediator/1.0/transformations#',
                'dc'    : 'http://purl.org/dc/elements/1.1/',
                'foaf'  : "http://xmlns.com/foaf/0.1/",
                'edoal' : EDOALparser.Alignment.EDOAL_NAMESPACE,
                'align' : 'http://knowledgeweb.semanticweb.org/heterogeneity/alignment#',
                'alext' : 'http://exmo.inrialpes.fr/align/ext/1.0/'
                 }
        # Combine the default namespaces with the presented namespace, but reject double prefixes/keys
        for key in nsDict.keys():
            assert not key in mediatorNSs.keys()
        mediatorNSs.update(nsDict)
        print("mediator ns:", mediatorNSs)
        self.nsMgr = namespaces.NSManager(nsDict=mediatorNSs, base='http://knowledgeweb.semanticweb.org/heterogeneity/alignment#')
        if self.nsMgr == None: raise RuntimeError("Fatal: Couldn't create a namespace manager")
        self.about = self.nsMgr.asIRI(about)
        self.alignments = {}
        
    def addAlignment(self, alignment_filename=''):
        assert alignment_filename != '', "Name of file containing alignment expected"
        assert os.path.isfile(alignment_filename), "Cannot find file {}".format(alignment_filename)
        alignment = EDOALparser.Alignment(fn = alignment_filename, nsMgr=self.nsMgr)
        self.alignments[alignment.getAbout()] = alignment
        
    def getNSs(self):
        return(self.nsMgr)
            
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
#         self.nsMgr.bindPrefixesFrom(rq)
        print(rq.dump())
        rq.expandIris()
        print (rq.dump())
        rq.render()
        for name, align in self.alignments.items():
            print("Translating according to Alignment '{}'".format(name))
            for corr in align.getCorrespondences():
                print(corr)
                print(corr.translate(rq))
            
    def __len__(self):
        '''
        Calculates the length of the Mediator as the amount of Alignments it contains.
        '''
        return len(self.alignments)     
    
    def getName(self):
        '''
        Retrieves the name of this Mediator, which reifies the Alignment's "about" attribute.
        '''
        return self.about
     
    def render(self):
        '''
        Produce a rendering of the Mediator 
        '''
        return repr(self)
    
    def __str__(self):
        return repr(self)
        
    def __repr__(self):
        s = self.getName() + ' has ({}) alignments'.format(len(self)) + ' ( '
        for name,_ in self.alignments:
            s += name + ' '
        return s + ')\n' + self.getNSs()
    
if __name__ == '__main__':
    print('running main')


