# -*- coding: utf-8 -*-
from suds.sax.text import Text
import datetime
import six


def node_to_dict(node):

    # if type(node) is str or type(node) is unicode:
    if isinstance(node, six.string_types) or isinstance(node, six.text_type):
        return node
    elif type(node) is Text:
        return str(node)
    elif isinstance(node, six.integer_types):
        return node
    elif type(node) is bool:
        return node
    elif type(node) is datetime.datetime:
        return node
    elif type(node) is float:
        return node
    # elif type(node) is NoneType:
    elif node is None:
        return node
    elif type(node) is list:
        result = []
        for x in node:
            result.append(node_to_dict(x))
        return result
    elif isinstance(node, dict):
        result = {}
        for key, value in six.iteritems(node):
            result[key] = node_to_dict(value)

        return result
    elif hasattr(node, '__keylist__'):
        # return node_to_dict(node.__dict__)
        result = {}
        for key in node.__keylist__:
            result[key] = node_to_dict(getattr(node, key))

        return result
    else:
        # print node
        raise Exception('node_to_dict Unknown type: %s' % type(node))
