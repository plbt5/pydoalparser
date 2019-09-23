'''
Created on 23 feb. 2016

@author: brandtp

This example shows how to use a mediator that can make translations between concepts and data from one ontology into another ontology.
Prerequisites:
1. both ontologies (at this moment only an identifying IRI for each of them is required)
2. data to translate, i.e., a sparql SELECT query
3. a specification of the namespaces that are in use

'''


from mediator.mediator import Mediator
from utilities import namespaces
import json

# Create a namespace specification 
nsDict = {
    'ts'   : 'http://ts.tno.nl/mediator/test#'
}
# Use this namespace specification to create a namespace manager; the second argument represents the default namespace
#TODO: Dit is gerommel in de marge met namespaces; het is niet duidelijk waarom ik hier een dergelijke setup vereis, temeer omdat de in de mediator
# gebruikte namespaces hier niet worden gespecificeerd, maar impliciet uit de alignment volgen. Vanuit dit nivo wordt alleen een iri geformuleerd ter identificatie van de mediator, en dat kan ook
# in de mediator initiatie worden gedaan.
nsMgr = namespaces.NSManager(nsDict, "http://ts.tno.nl/mediator/test#")

# Create a mediator
m = Mediator(about='ts:myMediator', nsDict=nsDict)

# Select an EDOAL alignment
edoal_file = "./exampleAlignment.xml"
print("Alignment from: {}".format(edoal_file))

# Add the alignment to the mediator that specifies how to translate concepts and data between both ontologies
m.addAlignment(edoal_file)
print("mediator '{}' with alignments: {}".format(m.getName(), m.alignments))

# Read the data, i.e., a sparql SELECT query
with open("./exampleSparqlSelect.rq", 'r') as f:
    sparl_string = f.read() 
print("\nOriginal query: \n{}".format(sparl_string))

# Translate the query accoring to the alignment
# This call requires the data to translate, and also the source ontology that the data originates from in order to indicate the translation direction
queryTranslated = m.translate(raw_data = sparl_string, source_onto_ref = "http://ts.tno.nl/mediator/1.0/examples/ontoTemp1A#")
print("\nTranslated query: \n{}".format(queryTranslated))

# Since the aligment specifies a bidirectional translation, the translated query (that is in terms of ontoTemp1B#) can be  translated back into 
# a query on (the original) ontology ontoTemp1A#
# To that end, we take the translated query and reverse the direction of translation

double_translated_query = m.translate(raw_data = queryTranslated, source_onto_ref = "http://ts.tno.nl/mediator/1.0/examples/ontoTemp1B#")
print("\nReverse translated query: \n{}".format(double_translated_query))

# Now, for the query has been translated, it is ready to be forwarded to the target triplestore endpoint.

#TODO: The translated query can now be sent to the sparql endpoint of the collaborating application
# For that, make use of a sparql endpoint wrapper: https://rdflib.github.io/sparqlwrapper/
# For the moment, use a dummy file representing the response to the query. 
with open("./exampleSelectQueryResultSet.srj", 'r') as f:
    responseData = json.load(f)
print("\nResponse data: \n{}".format(responseData))

# The sparql result has been received. Before those results can be returned to the source application, those results require to be translated as well.
# For this, the identical method can be called, however, since the data originates from the second ontology, this second ontology now represents 
# the source ontology for this translation.

responseDataTranslated = m.translate(raw_data = responseData, source_onto_ref = "http://ts.tno.nl/mediator/1.0/examples/ontoTemp1B#")
print("\nTranslated response data: \n{}".format(responseDataTranslated))

print(help('mediator'))