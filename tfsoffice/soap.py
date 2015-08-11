import logging
from suds.client import Client
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('suds.client').setLevel(logging.INFO)

# http://developer.24sevenoffice.com/#apiauthenticate
# http://developer.24sevenoffice.com/category/dev/#apiinvoiceservice
# http://developer.24sevenoffice.com/diverse/apiinvoiceservice-datatypes/
# http://developer.24sevenoffice.com/diverse/apicompanyservice-datatypes/
# http://developer.24sevenoffice.com/hidden/webserviceprojectservice/


class TwentyFour(object):
    _session_id = None
    _headers = None
    _faults = False
    _services = {
        'Authenticate':
            'https://api.24sevenoffice.com/authenticate/' +
            'v001/authenticate.asmx?WSDL',
        'Project':
            'http://webservices.24sevenoffice.com/Project/V001/' +
            'ProjectService.asmx?WSDL',
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
    }
    _clients = {}

    def __init__(self, username, password, applicationid, faults=False):
        self._faults = faults

        # authenticate
        status, session_id = self._authenticate(
            username, password, applicationid)
        assert status == 200, 'Status is not OK: %s' % status
        logging.debug('Authenticated OK as %s' % username)
        # store session id
        self._session_id = session_id
        self._headers = {'Cookie': 'ASP.NET_SessionId=%s' % self._session_id}

    def _authenticate(
            self,
            username,
            password,
            applicationid,
            identityId="00000000-0000-0000-0000-000000000000"
    ):
        client = Client(self._services['Authenticate'], faults=self._faults)
        cred = client.factory.create('Credential')
        cred.ApplicationId = applicationid
        # cred.IdentityId = identityId
        cred.Username = username
        cred.Password = password
        return client.service.Login(cred)

    def getClient(self, name):
        if name in self._clients:
            return self._clients[name]

        # Create a new client
        self._clients[name] = Client(
            self._services[name],
            faults=self._faults,
            headers=self._headers)
        logging.debug('Created new service: %s' % name)
        return self._clients[name]

    def createProject(self, name):
        r'''
        Project
        '''
        client = self.getClient('Project')
        ProjectNameType = client.factory.create('ProjectNameType')

        # create empty project
        project = client.factory.create('Project')
        project.Name = name
        project.NameDisplay = ProjectNameType
        project.Version = 1  # no rights management
        status, project_id = client.service.SaveProject(project)
        assert status == 200, 'SaveProject is not ok: %s' % status
        logging.info('Created new project: %s' % project_id)

        # return project
        status, project = client.service.GetSingleProject(project_id)
        assert status == 200, 'GetSingleProject is not ok: %s' % status

        return project

    def saveProject(self, project):
        r'''
        Project
        '''
        client = self.getClient('Project')
        status, result = client.service.SaveProject(project)
        assert status == 200, 'SaveProject is not ok: %s' % status
        print '-- SaveProject OK (update) --'
        logging.info('Project [%s] saved' % project.Id)

    def findProject(self, **kwargs):
        r'''
        Only accepts ONE parameter at a time.
        CustomerId int
        Search string
        ChangedAfter datetime
        StartedAfter datetime
        StartedBefore datetime
        MyProjects bool
        AllOpenProjects bool
        http://developer.24sevenoffice.com/hidden/webserviceprojectservicev001-datatypes/
        '''
        # get project client
        client = self.getClient('Project')

        # create a basic search
        projectSearch = client.factory.create('ProjectSearch')
        for key, value in kwargs.iteritems():
            setattr(projectSearch, key, value)

        # search for projects
        status, projects = client.service.GetProjectList(projectSearch)
        assert status == 200, 'GetProjectList failed: %s' % status
        if 'Project' not in projects:
            return None
        projects = [p for p in projects.Project]
        return projects

    def listCompanies(self, **kwargs):
        r'''
        List companies by:
        CustomerId
        CompanyName (do not use *)
        ChangedAfter
        '''
        # validate params
        assert kwargs.get('CompanyId') \
            or kwargs.get('CompanyName') \
            or kwargs.get('ChangedAfter'), \
            'No valid CompanySearchParameters '\
            '(CompanyId|CompanyName|ChangedAfter)'

        client = self.getClient('Company')

        # returnProperties
        ArrayOfString = client.factory.create('ArrayOfString')
        ArrayOfString.string = ['Owner', 'Name', 'FirstName', 'Country',
                                'APIException', 'Note', 'InvoiceLanguage',
                                'Type', 'Username', 'IncorporationDate',
                                'DateCreated', 'Status', 'BankAccountNo',
                                'TypeGroup', 'IndustryId', 'MemberNo',
                                'DistributionMethod', 'EmailAddresses',
                                'PhoneNumbers', 'Maps', 'Relations']

        params = client.factory.create('CompanySearchParameters')
        for key, value in kwargs.iteritems():
            setattr(params, key, value)

        status, result = client.service.GetCompanies(params, ArrayOfString)
        assert status == 200, 'GetCompanies failed: %s' % status

        if 'Company' not in result:
            return None
        return [c for c in result.Company]

    def saveCompany(self, name, companyType='Supplier', **kwargs):
        r'''
        Create or update a Company
        set parameter Id to update an existing company
        '''
        client = self.getClient('Company')

        CompanyType = client.factory.create('CompanyType')
        CurrencyType = client.factory.create('CurrencyType')

        company = client.factory.create('Company')
        company.Name = name
        company.Type = getattr(CompanyType, companyType)  # default: Leverandor
        company.Country = 'NO'
        company.InvoiceLanguage = 'NO'
        company.CurrencyId = CurrencyType.NOK

        # email
        company.EmailAddresses.Work.Value = kwargs.pop('email_work', None)
        company.EmailAddresses.Invoice.Value = kwargs.pop(
            'email_invoice', None)

        # phone
        company.PhoneNumbers.Work.Value = kwargs.pop('phone', None)

        # apply kwargs
        for key, value in kwargs.iteritems():
            setattr(company, key, value)

        # Send a list of companies
        ArrayOfCompany = client.factory.create('ArrayOfCompany')
        ArrayOfCompany.Company = [company, ]

        # Save/store companies in the list
        status, result = client.service.SaveCompanies(ArrayOfCompany)
        assert status == 200, 'SaveCompanies failed: %s' % status

        if 'Company' not in result:
            return []
        return [c for c in result.Company]

    def listCompanyCategories(self, CompanyId):
        client = self.getClient('Company')
        status, result = client.service.GetCustomerCategories(CompanyId)
        assert status == 200, 'GetCustomerCategories failed: %s' % status
        if 'int' not in result:
            return []
        return result.int

    def saveCompanyCategories(self, CompanyId, categories):
        client = self.getClient('Company')

        available_categories = self.listCategories()

        ArrayOfKeyValuePair = client.factory.create('ArrayOfKeyValuePair')
        for cat in categories:
            KeyValuePair = client.factory.create('KeyValuePair')
            for tmp in available_categories:
                if tmp.Name == cat:
                    print 'Adding category: %s - %s' % (tmp.Id, tmp.Name)
                    KeyValuePair.Key = tmp.Id
                    KeyValuePair.Value = CompanyId
                    ArrayOfKeyValuePair.KeyValuePair.append(KeyValuePair)

        status, result = client.service.SaveCustomerCategories(ArrayOfKeyValuePair)
        assert status == 200, 'SaveCustomerCategories failed: %s' % status
        return result

    def listCategories(self):
        client = self.getClient('Company')
        status, result = client.service.GetCategories()
        assert status == 200, 'GetCategories failed: %s' % status
        return [c for c in result.Category]
