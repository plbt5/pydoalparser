'''
Created on 23 mrt. 2016

@author: brandtp
'''
import unittest

import json

class TestNSManager(unittest.TestCase):


    def setUp(self):
        self.testdir = './resources/sparqlQueries/'
        self.testCases = {}
        self.testCases['mf:Manifest'] = []
        with open(self.testdir + 'manifest.json') as f:    
            self.testCases = json.load(f)


    def tearDown(self):
        pass


    def testsparql(self):
        for case in self.testCases["mf:entries"]:
            fileName = self.testCases[case]["mf:action"]["qt:query"]
            with open(self.testdir + fileName, 'r') as f:
                querystring = f.read() 
#             print(querystring)
            root = parseQuery(querystring)
            results = getBGPs(root)
            
            cases = []
            for d in self.testCases[case]["mf:result"]:
                pair = (d['rdf:type'],d['value'])
                cases.append(pair)
            for case in cases:
                print(case)

            for (passfail, fileName) in cases:
                with open(self.testdir + fileName, 'r') as f:
                    criteria = json.load(f) 

                if passfail == "PASS":
                    cList = []
                    for triple in criteria["results"]["bindings"]:
                        print(triple["s"], triple["p"], triple["o"])
                    for result in results:
                        for (s,p,o) in result:
                            print(s)
                elif passfail == "FAIL":
                    pass
                else: raise KeyError("manifest {}: PASS or FAIL expected, got {}".format(self.testCases["manifest"]["file"], passfail))
            


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'TestNSManager.testsparql']
    unittest.main()