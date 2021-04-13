# -*- coding: utf-8 -*-
from types import ModuleType

from suds.client import Client as SudsClient
from suds.sax.text import Text
from suds import WebFault
from tfsoffice.utils import node_to_dict
from tfsoffice import exceptions
from tfsoffice import resources
# from . import error, resources, __version__  # noqa

import string
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('suds.client')

# Create a dict of resource classes
RESOURCE_CLASSES = {}
for name, module in list(resources.__dict__.items()):
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

    api = Client(username, password, applicationid)
    # this will log you in as your default commonity identity
    # http://developer.24sevenoffice.com/#webserviceaccountservice

    # or with additional identityid

    api = Client(username, password, applicationid, identityid)

    # or with sesson_id

    api = Client(username=None, password=None, applicationid, session_id=sessionid)

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
        'Account':
            'https://webservices.24sevenoffice.com/economy/accountV002/' +
            'AccountService.asmx?WSDL',
        'AccountVersionThree':
            'https://webservices.24sevenoffice.com/Economy/Account/V003/' +
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
        'Person':
            'https://webservices.24sevenoffice.com/CRM/Contact/PersonService.asmx?WSDL',
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

    _client_information = {}
    _country_code = ''

    def __init__(self, username, password, applicationid, identityid=None, token_id=None, faults=True, **options):  # noqa
        """
        Initialize a Client object with session, optional auth handler, and options
        """
        # self.session = session or requests.Session()
        self._faults = faults
        self._clients = {}
        self._headers = None
        self._username = username

        if 'session_id' in options:
            session_id = options['session_id']

        elif token_id:
            session_id = self._authenticate_by_token(token_id, applicationid)

        else:
            # authenticate
            try:
                session_id = self._authenticate(username, password, applicationid, identityid)
            except WebFault as ex:
                if 'The provided IdentityId is blocked' in ex.fault.faultstring:
                    raise exceptions.IdentityBlockedException(
                        ex.fault.faultstring,
                        detail=ex.fault.detail,
                        faultcode=ex.fault.faultcode,
                        params=dict(
                            username=username,
                            identityid=identityid
                        )
                    )
                raise exceptions.WebFault(
                    message=ex.fault.faultstring,
                    detail=ex.fault.detail,
                    faultcode=ex.fault.faultcode
                )

            assert session_id, 'Authentication failure'

            logging.debug('Authenticated OK as %s' % username)

        # store session id
        self._headers = {'Cookie': 'ASP.NET_SessionId=%s' % session_id}

        # merge the provided options (if any) with the global DEFAULTS
        self._options = _merge(self._DEFAULTS, options)

        # intializes each resource, injecting this client object into the constructor
        for name, Klass in list(RESOURCE_CLASSES.items()):
            setattr(self, name, Klass(self))

        # load client information to get country code
        self._client_information = self.client.get_client_information()
        self._country_code = self._client_information.get('Country') or ''

    def _authenticate(
            self,
            username,
            password,
            applicationid,
            identityid=None
    ):
        client = SudsClient(self._services['Authenticate'], faults=self._faults)
        cred = client.factory.create('Credential')
        cred.Username = username
        cred.Password = password
        cred.ApplicationId = applicationid
        cred.IdentityId = identityid
        return client.service.Login(cred)

    def _authenticate_by_token(self, token_id, applicationid):
        client = SudsClient(self._services['Authenticate'])
        token = client.factory.create('Token')
        token.Id = token_id
        token.ApplicationId = applicationid
        passport = client.service.AuthenticateByToken(token)

        return passport.SessionId

    def _get_client(self, name):
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

    def _get(self, method, params, **options):
        """Parse GET request options and dispatches a request."""
        return_values = options.pop('return_values', None)

        try:
            if return_values:
                result = method(params, return_values)
            else:
                result = method(params)
        except WebFault as ex:
            raise exceptions.WebFault(
                message=ex.fault.faultstring,
                detail=ex.fault.detail,
                faultcode=ex.fault.faultcode,
                params=params
            )

        # message = api.last_received()
        # text = message.children[0].children[0].children[0].children[1].text

        if type(result) is Text:
            return str(result)
        elif type(result) is bool:
            result = result
        elif type(result) is str:
            result = result
        elif type(result[0]) is list:
            result = result[0][0]
        data = node_to_dict(result)
        return data

    def _get_collection(self, method, params, **options):
        """
        Parse GET request options for a collection endpoint and dispatches a request.
        """
        # create output
        output = dict(
            count=0,
            results=[]
        )

        # execute -> backend
        return_values = options.pop('return_values', None)
        try:
            if return_values:
                results = method(params, return_values)
            else:
                results = method(params)
        except WebFault as ex:
            raise exceptions.WebFault(
                message=ex.fault.faultstring,
                detail=ex.fault.detail,
                faultcode=ex.fault.faultcode,
                params=params
            )

        # check response
        # assert status == 200, 'Status is %s' % status
        if type(results) is Text:
            output['results'] = [str(results), ]
            return output

        # raise Exception if result is anything but a List
        assert type(results[0]) is list, 'Expected list from API, got %s' % type(results[0])

        # Convert to JSON
        for result in results[0]:
            data = node_to_dict(result)
            output['results'].append(data)
        output['count'] = len(output['results'])
        return output


def _merge(*objects):
    """Merge one or more objects into a new object"""
    result = {}
    [result.update(obj) for obj in objects]
    return result
