class Companies:
    def __init__(self, client=None):
        self.client = client
        self.service = 'Company'

    def _get_return_values(self, api):
        return_values = api.factory.create('ArrayOfString')
        return_values.string = ['OrganizationNumber', 'Owner', 'Name', 'FirstName', 'NickName',
                                'Country', 'Status',
                                'APIException', 'Note', 'InvoiceLanguage',
                                'Type', 'Username', 'IncorporationDate',
                                'DateCreated', 'DateChanged', 'Status', 'BankAccountNo',
                                'TypeGroup', 'IndustryId', 'MemberNo',
                                'DistributionMethod', 'EmailAddresses', 'Addresses',
                                'PhoneNumbers', 'Maps', 'Relations', 'CurrencyId']
        return return_values

    def find_by_id(self, company_id, params={}, **options):
        api = self.client.get_client(self.service)

        return_values = self._get_return_values(api)

        params = api.factory.create('CompanySearchParameters')
        params.CompanyId = company_id

        method = api.service.GetCompanies

        return self.client.get(method, params, return_values=return_values, **options)

    def find_by_name(self, name, params={}, **options):
        api = self.client.get_client(self.service)
        return_values = self._get_return_values(api)

        params = api.factory.create('CompanySearchParameters')
        params.CompanyName = name

        method = api.service.GetCompanies

        return self.client.get_collection(method, params, return_values=return_values, **options)

    def find_by_date_changed(self, changed, params={}, **options):
        api = self.client.get_client(self.service)
        return_values = self._get_return_values(api)

        params = api.factory.create('CompanySearchParameters')
        params.ChangedAfter = changed

        method = api.service.GetCompanies

        return self.client.get_collection(method, params, return_values=return_values, **options)
