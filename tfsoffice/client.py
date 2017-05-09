# -*- coding: utf-8 -*-
from types import ModuleType
from suds.client import Client as SudsClient
from suds.sax.text import Text
from .utils import node_to_dict

import string
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('suds.client')

from . import error, resources  # noqa
# from . import error, resources, __version__  # noqa

# Create a dict of resource classes
RESOURCE_CLASSES = {}
for name, module in resources.__dict__.items():
    classified_name = string.capwords(name, '_').replace('_', '')
    if isinstance(module, ModuleType) and classified_name in module.__dict__:
        RESOURCE_CLASSES[name] = module.__dict__[classified_name]

# Create a mapping of status codes to classes
STATUS_MAP = {}
for name, Klass in error.__dict__.items():
    if isinstance(Klass, type) and issubclass(Klass, error.AsanaError):
        STATUS_MAP[Klass().status] = Klass


class Client:
    """
    24sevenoffice Client

    Offers access to Company, Project,

    Syntax:
    from tfsoffice import Client
    client = client = Client(raw_input('E-mail:'), getpass.getpass('Password:'), settings.TWENTYFOUR_APP_ID)
    print 'All my projects'
    for project in client.projects.find_mine():
        print project['Id'], project['Name']
    """

    DEFAULTS = {
        'base_url': 'https://api.24sevenoffice.com/',
        'item_limit': None,
        'page_size': 50,
        'poll_interval': 5,
        'max_retries': 5,
        'full_payload': False,
        'iterator_type': 'items'
    }

    RETRY_DELAY = 1.0
    RETRY_BACKOFF = 2.0

    CLIENT_OPTIONS = set(DEFAULTS.keys())
    QUERY_OPTIONS = set(['limit', 'offset', 'sync'])
    REQUEST_OPTIONS = set(['headers', 'params', 'data', 'files', 'verify'])
    API_OPTIONS = set(['pretty', 'fields', 'expand'])

    ALL_OPTIONS = CLIENT_OPTIONS | QUERY_OPTIONS | REQUEST_OPTIONS | API_OPTIONS

    _services = {
        'Authenticate':
            'https://api.24sevenoffice.com/authenticate/' +
            'v001/authenticate.asmx?WSDL',
        'Account':
            'https://webservices.24sevenoffice.com/Economy/Account/' +
            'AccountService.asmx?WSDL',
        'Attachment':
            'https://webservices.24sevenoffice.com/Economy/Accounting/Accounting_V001/' +
            'AttachmentService.asmx?WSDL',
        'Client':
            'https://api.24sevenoffice.com/Client/V001/' +
            'ClientService.asmx?WSDL',
        'Company':
            'https://api.24sevenoffice.com/CRM/Company/V001/' +
            'CompanyService.asmx?WSDL',
        'File':
            'https://webservices.24sevenoffice.com/file/V001/' +
            'FileService.asmx?wsdl',
        'FileInfo':
            'https://webservices.24sevenoffice.com/file/V001/' +
            'FileInfoService.asmx?wsdl',
        'Invitation':
            'https://webservices.24sevenoffice.com/Invitation/' +
            'Invitation_V001/InvitationService.asmx?WSDL',
        'Invoice':
            'https://api.24sevenoffice.com/Economy/InvoiceOrder/V001/' +
            'InvoiceService.asmx?WSDL',
        'Payment':
            'https://api.24sevenoffice.com/Economy/InvoiceOrder/V001/' +
            'PaymentService.asmx?WSDL',
        'Product':
            'https://api.24sevenoffice.com/Logistics/Product/V001/' +
            'ProductService.asmx?WSDL',
        'Project':
            'https://webservices.24sevenoffice.com/Project/V001/' +
            'ProjectService.asmx?WSDL',
        'SalesOpp':
            'https://webservices.24sevenoffice.com/SalesOpp/V001/' +
            'SalesOppService.asmx?WSDL',
        'Template':
            'https://api.24sevenoffice.com/CRM/Template/V001/' +
            'TemplateService.asmx?WSDL',
        'Time':
            'https://webservices.24sevenoffice.com/timesheet/v001/' +
            'timeservice.asmx?WSDL',
        'Transaction':
            'https://api.24sevenoffice.com/Economy/Accounting/V001/' +
            'TransactionService.asmx?WSDL',
    }
    _clients = {}
    _session_id = None
    _headers = None
    _faults = False

    def __init__(self, username, password, applicationid, session=None, auth=None, faults=False, **options):  # noqa
        """
        Initialize a Client object with session, optional auth handler, and options
        """
        # self.session = session or requests.Session()
        self._faults = faults

        # authenticate
        status, session_id = self._authenticate(
            username, password, applicationid)
        if status != 200:
            logger.warning('Cannot authenticate with 24so, Status is not OK: %s - %s' % (status, session_id))
        assert status == 200, 'Cannot authenticate with 24so, Status is not OK: %s' % status
        logging.debug('Authenticated OK as %s' % username)
        # store session id
        self._session_id = session_id
        self._headers = {'Cookie': 'ASP.NET_SessionId=%s' % self._session_id}

        self.auth = auth
        # merge the provided options (if any) with the global DEFAULTS
        self.options = _merge(self.DEFAULTS, options)

        # intializes each resource, injecting this client object into the constructor
        for name, Klass in RESOURCE_CLASSES.items():
            setattr(self, name, Klass(self))

    def _authenticate(
            self,
            username,
            password,
            applicationid,
            identityid="00000000-0000-0000-0000-000000000000"
    ):
        client = SudsClient(self._services['Authenticate'], faults=self._faults)
        cred = client.factory.create('Credential')
        cred.ApplicationId = applicationid
        # cred.identityid = identityid
        cred.Username = username
        cred.Password = password
        return client.service.Login(cred)

    def get_client(self, name):
        """
        Return a client

        TODO change name to: get_handler ?
        get_api ?
        """
        if name in self._clients:
            return self._clients[name]

        # Create a new client
        self._clients[name] = SudsClient(
            self._services[name],
            faults=self._faults,
            headers=self._headers)
        logging.debug('Created new service: %s' % name)
        return self._clients[name]

    # .client.get(method, params, return_values=return_values, **options)
    def get(self, method, params, **options):
        """Parse GET request options and dispatches a request."""
        # api_options = self._parse_api_options(options, query_string=True)
        # query_options = self._parse_query_options(options)
        # parameter_options = self._parse_parameter_options(options)
        # query = _merge(query_options, api_options, parameter_options, query)  # options in the query takes precendence
        # return self.request('get', path, params=query, **options)
        return_values = options.pop('return_values', None)
        if return_values:
            status, result = method(params, return_values)
        else:
            status, result = method(params)
        assert status == 200, 'Status is %s' % status
        if type(result[0]) is list:
            result = result[0][0]
        data = node_to_dict(result)
        return data

    def get_collection(self, method, params, **options):
        """Parse GET request options for a collection endpoint and dispatches a request."""
        # options = self._merge_options(options)

        # create output
        output = dict(
            count=0,
            results=[]
        )

        # execute -> backend
        return_values = options.pop('return_values', None)
        if return_values:
            status, results = method(params, return_values)
        else:
            status, results = method(params)

        output['status_code'] = status

        # check response
        # assert status == 200, 'Status is %s' % status
        if type(results) is Text:
            return output

        # raise Exception if result is anything but a List
        assert type(results[0]) is list, 'Expected list from API, got %s' % type(results[0])

        # Convert to JSON
        for result in results[0]:
            data = node_to_dict(result)
            output['results'].append(data)
        output['count'] = len(output['results'])
        return output

        # if options['iterator_type'] == 'items':
        #     return CollectionPageIterator(self, path, query, options).items()
        # if options['iterator_type'] is None:
        #     return self.get(path, query, **options)
        # raise Exception('Unknown value for "iterator_type" option: ' + str(options['iterator_type']))


def _merge(*objects):
    """Merge one or more objects into a new object"""
    result = {}
    [result.update(obj) for obj in objects]
    return result
