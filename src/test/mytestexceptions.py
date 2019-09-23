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

import warnings

class WarningTestMixin(object):
    'A test which checks if the specified warning was raised'

    def assertWarns(self, warning, callable, *args, **kwds):
        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter('always')

            result = callable(*args, **kwds)

            self.assertTrue(any(item.category == warning for item in warning_list))
            
AS_EXCEPTION_TYPE = {
    "UserWarning": UserWarning
}