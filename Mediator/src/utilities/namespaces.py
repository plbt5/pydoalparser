'''
Created on 1 apr. 2016

@author: brandtp
'''

# import elementtree.ElementTree as ET
import xml.etree.ElementTree as ET

def parse_and_get_ns(file):
    events = "start", "start-ns"
    root = None
    ns = {}
    for event, elem in ET.iterparse(file, events):
        if event == "start-ns":
            if elem[0] in ns and ns[elem[0]] != elem[1]:
                # NOTE: It is perfectly valid to have the same prefix refer
                #     to different URI namespaces in different parts of the
                #     document. This exception serves as a reminder that this
                #     solution is not robust.    Use at your own peril.
                raise KeyError("Duplicate prefix with different URI found.")
            ns[elem[0]] = "{%s}" % elem[1]
        elif event == "start":
            if root is None:
                root = elem
    return ET.ElementTree(root), ns

NS_MAP = "xmlns:map"
def parse_with_nsmap(file):

    events = "start", "start-ns", "end-ns"

    root = None
    ns_map = []

    for event, elem in ET.iterparse(file, events):
        if event == "start-ns":
            ns_map.append(elem)
        elif event == "end-ns":
            ns_map.pop()
        elif event == "start":
            if root is None:
                root = elem
            elem.set(NS_MAP, dict(ns_map))

    return ET.ElementTree(root)

def getNSMap():
    return(NS_MAP)

from rdflib import Namespace as RDFNamespace
class Namespace(RDFNamespace):
    '''
    Utility class for simple manipulation and comparison of namespaced entities in the Mediator. Is based on rdflib.Namespace
    Input: your basic part of the 
    '''

    def __init__(self, ns):
        '''
        Constructor
        '''
        self.__super__(ns)
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
