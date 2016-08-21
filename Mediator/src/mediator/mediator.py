'''
Created on 26 feb. 2016

@author: brandtp
'''


from parsertools.parsers.sparqlparser import parseQuery
from utilities import namespaces
from mediator import EDOALparser
from mediator.sparqlTools import SparqlQueryResultSet, isSparqlQuery, isSparqlResult,\
    Context
from builtins import str
import warnings
import os.path
from uuid import uuid1
from pywin.scintilla import bindings

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

    class TranslationResult():
        '''
        Translations that are performed by the mediator are not always straightforward. For instance, only part of the data might be 
        translatable, or, just like a sparql query result set relates to the sparql query, their translations are related as well.
        This class serves as intermediate for storing translation results that are relevant to consider when having a semantic
        interaction, i.e., to direct the semantic protocol, or when translating query results back. 
        The class will contain:
        * a unique identifier
        * the context for a sparql query
        * more stuff when deemed relevant
        '''
        def __init__(self, c=None):
            self.id = uuid1()
            if c: self.context = self.addContext(c)
            else: self.context = None
        
        def addContext(self, c=None):
            '''
            add the sparqlTools.Context to this translation result. Only one context can be added.
            '''
            assert isinstance(c, Context)
            if not self.context:
                self.context = c
   
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
#         print("Mediator init(): adding namespace:", mediatorNSs)
        self.nsMgr = namespaces.NSManager(nsDict=mediatorNSs, base='http://knowledgeweb.semanticweb.org/heterogeneity/alignment#')
        if self.nsMgr == None: raise RuntimeError("Mediator.init(): Fatal: Couldn't create a namespace manager")
        self.about = self.nsMgr.asIRI(about)
        self.alignments = {}
        self.parsedAlignFiles = []
        
    def addAlignment(self, alignment_filename=''):
        assert alignment_filename != '', "Mediator.addAlignment(): Name of file containing alignment expected"
        assert os.path.isfile(alignment_filename), "Mediator.addAlignment(): Cannot find file {}".format(alignment_filename)
        if not alignment_filename in self.parsedAlignFiles :
            # First, create the alignment that will be added to this mediator
            alignment = EDOALparser.Alignment(fn = alignment_filename, nsMgr=self.nsMgr)
            assert not alignment.getAbout() in self.alignments, "Mediator.addAlignment(): already added alignment '{}' to mediator '{}'".format(alignment.getAbout(), self.about)
            # Second, parse and create the correspondences that are part of this alignment, and add them to the alignment
            assert len(alignment.getCorrespondences()) > 0, "Mediator.addAlignment(): cannot find correspondences in alignment '{}' of mediator '{}'".format(alignment.getAbout(), self.about)
            # Third and finally, add the alignment (including the correspondences) to the mediator, and flag that the file has been parsed
            self.alignments[alignment.getAbout()] = alignment
            self.parsedAlignFiles.append(alignment_filename)
        else: warnings.warn("Mediator.addAlignment(): alignment file '{}' already processed by mediator '{}', skipping ...".format(alignment_filename, self.about), category = UserWarning)
        
    def getNSs(self):
        return(self.nsMgr)
            
    def translate(self, *, raw_data=None, source_onto_ref=None):
        '''
        Translate the data according to the EDOAL alignment cells that are stored in correspondence objects
        - data (sparql query as string): the data to be translated; this data can represent one out of the following
            1: a sparql query (one of: SELECT, ASK, UPDATE, DESCRIBE)
            2: a sparql result set
            3: an RDF triple or RDF graph
        - source: reference to the ontology that the data originates from, in order to indicate the direction of the translation
        returns: the result of the translation, currently of type (parsertools.base.ParseStruct)
        
        As of this moment, only SPARQL SELECT and ASK queries are supported
        '''
        # Process:
        # 1 - Prepare the input data:
        #    (i) in case of query data, parse the query string
        #    (ii) in case of query result data, create a class from it
        # 2 - Loop over all alignments (currently only one) and check its src and tgt ontology iri's to match with the source ontology the data originates from
        #     (this also establishes the translation direction)
        # 3 - On a match: loop over all correspondences in an alignment in order to ...
        # 4 - ... let the correspondence determine if and how to translate the data

        assert raw_data, "Mediator.translate(): Fatal - data required"
        assert source_onto_ref, "Mediator.translate(): Fatal - Indication of translation direction is required by means of specifying the ontology iri from which the data originates"
        
        # 1 - prepare the input data
        # Determine the type of data: sparql query or sparql query result set.
        
#         print("Mediator.translate(): translating data ...")
        if isSparqlResult(raw_data):
            print("Mediator.translate(): translating a Sparql Result Set ...")
            # (i) Data are sparql query result set (SQRset), hence create sparql result object
            data = SparqlQueryResultSet(raw_data)
            
            if data.isResponseToASK():
                # A Boolean True or False doesn't need translation
                return data
            elif not data.isResponseToSELECT():
                raise RuntimeError("Mediator.translate(): Fatal - Can only translate query result responses to ASK or SELECT queries, got '{}'".format(data.getQueryType()))
        elif isSparqlQuery(raw_data):
            # (ii) Data are a sparql query
            # (ii) a - Parse the sparql data into graph (tree)
            data = parseQuery(raw_data)
            if data == []:
                raise RuntimeError("Mediator.translate(): Couldn't parse query:\n{}".format(raw_data))
    
            # (ii) b - Base the comparison between querygraph and aligment on full iri's: Thus expand the iri's in the querygraph. 
            data.expandIris()
            # (ii) c - Create the context for this query
            
            # (ii) d - Create the Translation result and add the context
        else: 
            raise RuntimeError("Mediator.translate(): Fatal - Expected sparql query, or query result set, got:\n{}".format(raw_data))

        # 1b - All iri's are represented with embraced '< >' pair. Make sure that this is the case
        if source_onto_ref[0] != '<' and source_onto_ref[-1] != '>':
            source_onto_ref = '<' + source_onto_ref + '>'

        # 2 - Loop over all alignments
        for name, align in self.alignments.items():
            # 2a - Determine what is the source and what the target entity expression for this data, i.e., determine direction for translation
#             print("Direction specified by source '{}'\nAlignment specifies '{}'".format(source_onto_ref, str(align.getSrcOnto()))) 
            if source_onto_ref == str(align.getSrcOnto()):
                # 3 - This alignment addresses this data for a forward translation, hence loop over all correspondences
                for corr in align.getCorrespondences():
                    srcEE = corr.getEE1()
                    tgtEE = corr.getEE2()
#                     print("Mediator.translate(): Translating '{}' to '{}' according to Alignment '{}'".format(srcEE,tgtEE,name))
                    # 4 - Let the correspondence establish whether it does or does not match something in the data, and can translate accordingly
                    _ = corr.translate(parsed_data=data, srcEE=srcEE, tgtEE=tgtEE)
                    #TODO: use result of the translation in the semantic protocol
            elif source_onto_ref == str(align.getTgtOnto()):
                # 3 - This alignment addresses this data for a backwards translation, hence loop over all correspondences
                for corr in align.getCorrespondences():
                    srcEE = corr.getEE2()
                    tgtEE = corr.getEE1()
#                     print("Mediator.translate(): Translating '{}' to '{}' according to Alignment '{}'".format(srcEE,tgtEE,name))
                    # 4 - Let the correspondence establish whether it does or does not match something in the data, and can translate accordingly
                    _ = corr.translate(parsed_data=data, srcEE=srcEE, tgtEE=tgtEE)
                    #TODO: use result of the translation in the semantic protocol
            else:
                warnings.warn("Mediator.translate(): Alignment '{}' cannot translate data that originate from ontology {}".format(name, source_onto_ref), category=UserWarning)
            
        # Return the resulting query, rendered into valid format
        return (str(data))
            
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


