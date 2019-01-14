import json, copy
from numbers import Number
from flask_restful import fields

class SafeDocument(fields.Raw):
    '''JSON-safe Mongo document or documents.'''
    def format(self, value):
        # See if the object is easily coerced to JSON.
        try:
            j = json.dumps(value)
        except TypeError:
            # We probably shouldn't alter the original value, which is likely
            # mutable.
            value = copy.deepcopy(value)
            # Define a recursive function for making dicts and lists safe.
            def make_safe(x):
                '''Make a list or dictionary JSON-safe.'''
                # If it isn't an iterable, make sure it's a string or a number.
                if not isinstance(x, list) and not isinstance(x, dict):
                    if isinstance(x, Number):
                        return x
                    else:
                        return str(x)
                # If it's a dictionary, make each value safe.
                if isinstance(x, dict):
                    for key in x.keys():
                       x[key] = make_safe(x[key]) 
                    return x
                # If it's a list, make each element safe.
                if isinstance(x, list):
                    return [make_safe(e) for e in x]
            value = make_safe(value)
        return value
