'''
Created on 24 apr. 2016

@author: brandtp
'''

class TestException(Exception):
    '''
    A new exception class to differentiate between the operational exceptions that are thrown during testing, and the
    exceptions that the testing process need to throw to flag missing test outcomes.
    '''

    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(TestException, self).__init__(message)
