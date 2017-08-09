# -*- coding: utf-8 -*-
from types import ModuleType

from suds.client import Client as SudsClient
from suds.sax.text import Text
from .utils import node_to_dict
from . import resources
# from . import error, resources, __version__  # noqa

import string
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('suds.client')

# Create a dict of resource classes
RESOURCE_CLASSES = {}
for name, module in resources.__dict__.items():
    classified_name = string.capwords(name, '_').replace('_', '')
    if isinstance(module, ModuleType) and classified_name in module.__dict__:
        RESOURCE_CLASSES[name] = module.__dict__[classified_name]

# Create a mapping of status codes to classes
# STATUS_MAP = {}
# for name, Klass in error.__dict__.items():
#     if isinstance(Klass, type) and issubclass(Klass, error.AsanaError):
#         STATUS_MAP[Klass().status] = Klass


class Client:
    """
    API client for 24SevenOffice

    There are three services ready: PersonService, CompanyService and ProjectService
    For more information: http://developer.24sevenoffice.com/

    --------

    api = Client(username, password, apikey)

    # search for person by name
    people = api.persons.find_by_name('rune')

    if len(people):
        # get detailed info about a person
        person = api.persons.find_by_id(people[0]['Id'])

    # list all projects assigned to you
    projects = api.projects.find_mine()

    # search for a company
    customers = api.companies.find_by_name('dataselskapet')

    # get detailed information about a company
    dataselskapet = api.companies.find_by_id(102)

    # list all projects assigned to a company
    projects = api.projects.find_by_customerid(102)
    """

    _DEFAULTS = {
        'base_url': 'https://api.24sevenoffice.com/',
        'item_limit': None,
        'page_size': 50,
        'poll_interval': 5,
        'max_retries': 5,
        'full_payload': False,
        'iterator_type': 'items'
    }

    _services = {
        'Authenticate':
            'https://api.24sevenoffice.com/authenticate/' +
            'v001/authenticate.asmx?WSDL',
        'Project':
            'http://webservices.24sevenoffice.com/Project/V001/' +
            'ProjectService.asmx?WSDL',
        'Person':
            'https://webservices.24sevenoffice.com/CRM/Contact/PersonService.asmx?WSDL',
        'Template':
            'https://api.24sevenoffice.com/CRM/Template/V001/' +
            'TemplateService.asmx?WSDL',
        'Company':
            'https://api.24sevenoffice.com/CRM/Company/V001/' +
            'CompanyService.asmx?WSDL',
        'Product':
            'https://api.24sevenoffice.com/Logistics/Product/V001/' +
            'ProductService.asmx?WSDL',
        'Invoice':
            'https://api.24sevenoffice.com/Economy/InvoiceOrder/V001/' +
            'InvoiceService.asmx?WSDL',
        'Client':
            'https://api.24sevenoffice.com/Client/V001/' +
            'ClientService.asmx?WSDL',
        'Transaction':
            'https://api.24sevenoffice.com/Economy/Accounting/V001/' +
            'TransactionService.asmx?WSDL',
        'File':
            'https://webservices.24sevenoffice.com/file/V001/' +
            'FileService.asmx?wsdl',
        'FileInfo':
            'https://webservices.24sevenoffice.com/file/V001/' +
            'FileInfoService.asmx?wsdl',
        'Attachment':
            'https://webservices.24sevenoffice.com/Economy/Accounting/Accounting_V001/' +
            'AttachmentService.asmx?WSDL',
        'SalesOpp':
            'https://webservices.24sevenoffice.com/SalesOpp/V001/' +
            'SalesOppService.asmx?WSDL',
        'Invitation':
            'https://webservices.24sevenoffice.com/Invitation/' +
            'Invitation_V001/InvitationService.asmx?WSDL',
        'Time':
            'http://webservices.24sevenoffice.com/timesheet/v001/' +
            'timeservice.asmx?WSDL',
        'Account':
            'http://webservices.24sevenoffice.com/Economy/Account/' +
            'AccountService.asmx?WSDL',
    }
    _clients = {}
    _session_id = None
    _headers = None
    _faults = False

    def __init__(self, username, password, applicationid, session=None, auth=None, faults=False, **options):  # noqa
        """Initialize a Client object with session, optional auth handler, and options"""
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

        # merge the provided options (if any) with the global DEFAULTS
        self._options = _merge(self._DEFAULTS, options)
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

    def _get_client(self, name):
        if name in self._clients:
            return self._clients[name]

        # Create a new client
        self._clients[name] = SudsClient(
            self._services[name],
            faults=self._faults,
            headers=self._headers)
        logging.debug('Created new service: %s' % name)
        return self._clients[name]

    def _get(self, method, params, **options):
        """Parse GET request options and dispatches a request."""
        return_values = options.pop('return_values', None)
        if return_values:
            status, result = method(params, return_values)
        else:
            status, result = method(params)

        assert status == 200, 'Status is %s' % status

        if type(result) is Text:
            logger.info('Found 0 results')
            return None
        elif type(result[0]) is list:
            result = result[0][0]
        data = node_to_dict(result)
        return data

    def _get_collection(self, method, params, **options):
        """Parse GET request options for a collection endpoint and dispatches a request."""
        return_values = options.pop('return_values', None)
        if return_values:
            status, results = method(params, return_values)
        else:
            status, results = method(params)

        assert status == 200, 'Status is %s' % status

        if type(results) is Text:
            logger.info('Found 0 results')
            return []
        assert type(results[0]) is list, 'Expected list from API, got %s' % type(results[0])

        output = []
        for result in results[0]:
            data = node_to_dict(result)
            output.append(data)
        return output


def _merge(*objects):
    """Merge one or more objects into a new object"""
    result = {}
    [result.update(obj) for obj in objects]
    return result
