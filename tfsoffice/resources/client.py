class Client:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Client'

    def get_department_list(self):
        api = self._client._get_client(self._service)

        params = None
        return_values = api.factory.create('Department')
        params = api.factory.create('Department')

        method = api.service.GetDepartmentList

        return self._client._get_collection(method, params)
        return self._client._get_collection(method, params, return_values=return_values)

    def get_currency_list(self):
        api = self._client._get_client(self._service)

        params = None

        method = api.service.GetCurrencyList

        return self._client._get_collection(method, params)

    def get_users(self):
        api = self._client._get_client(self._service)

        params = None

        method = api.service.GetUsers

        return self._client._get_collection(method, params)

    def get_client_information(self):
        api = self._client._get_client(self._service)

        params = None

        method = api.service.GetClientInformation

        return self._client._get(method, params)

    def get_vat_type_list(self):
        api = self._client._get_client(self._service)

        params = None

        method = api.service.GetVatTypeList

        return self._client._get_collection(method, params)

    # def register_payment(self, payment, params={}, **options):
    #     api = self._client._get_client(self._service)

    #     method = api.service.RegisterInvoicePayment

    #     return self._client._get(method, payment, **options)

    # def register_payments(self, payments, params={}, **options):
    #     api = self._client._get_client(self._service)

    #     params = api.factory.create('ArrayOfPayment')
    #     params.Payment.extend(payments)

    #     method = api.service.RegisterInvoicePayments

    #     return self._client._get_collection(method, params, **options)
