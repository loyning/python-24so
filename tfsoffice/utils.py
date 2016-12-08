# from suds.sax.text import Text
from suds.sudsobject import asdict
# from types import NoneType, InstanceType
# import datetime


def node_to_dict(d):
    """Convert Suds object into serializable format."""
    out = {}
    for k, v in asdict(d).iteritems():
        if hasattr(v, '__keylist__'):
            out[k] = node_to_dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    out[k].append(node_to_dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out

# def node_to_dict(node):

#     if type(node) is str or type(node) is unicode:
#         return node
#     elif type(node) is Text:
#         return node.decode('utf-8')
#     elif type(node) is int:
#         return node
#     elif type(node) is bool:
#         return node
#     elif type(node) is datetime.datetime:
#         return node
#     elif type(node) is float:
#         return node
#     elif type(node) is NoneType:
#         return node
#     elif type(node) is list:
#         result = []
#         for x in node:
#             result.append(node_to_dict(x))
#         return result
#     elif type(node) is InstanceType:
#         result = {}
#         for key, value in node:
#             result[key] = node_to_dict(value)
#         return result
#     else:
#         print node
#         raise Exception('node_to_dict Unknown type: %s' % type(node))
