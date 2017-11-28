import datetime


class Companies:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Company'

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

    def find_by_id(self, company_id):
        api = self._client._get_client(self._service)

        return_values = self._get_return_values(api)

        params = api.factory.create('CompanySearchParameters')
        params.CompanyId = company_id

        method = api.service.GetCompanies

        return self._client._get(method, params, return_values=return_values)

    def find_by_name(self, name):
        api = self._client._get_client(self._service)
        return_values = self._get_return_values(api)

        params = api.factory.create('CompanySearchParameters')
        params.CompanyName = name

        method = api.service.GetCompanies

        return self._client._get_collection(method, params, return_values=return_values)

    def find_by_date_changed(self, changed):
        api = self._client._get_client(self._service)
        return_values = self._get_return_values(api)

        params = api.factory.create('CompanySearchParameters')
        params.ChangedAfter = changed

        method = api.service.GetCompanies

        return self._client._get_collection(method, params, return_values=return_values)

    def list(self):
        api = self._client._get_client(self._service)
        return_values = self._get_return_values(api)

        beginning_of_time = datetime.datetime(1970, 1, 1)

        params = api.factory.create('CompanySearchParameters')
        params.ChangedAfter = beginning_of_time

        method = api.service.GetCompanies

        return self._client._get_collection(method, params, return_values=return_values)
