class Transactions:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Transaction'

    def get_transaction_types(self):
        api = self._client._get_client(self._service)

        method = api.service.GetTransactionTypes

        return self._client._get_collection(method, None)

    def get_transactions(self, date_start, date_end, system_type='InvoiceSupplier'):

        api = self._client._get_client(self._service)

        tss = api.factory.create('TransactionSystemType')
        if system_type not in tss:
            raise AttributeError('Wrong SystemType: {}'.format(system_type))

        params = api.factory.create('TransactionSearchParameters')
        params.DateStart = date_start
        params.DateEnd = date_end
        params.SystemType = tss[system_type]

        # transactions = api.service.GetTransactions(searchParams=params)

        method = api.service.GetTransactions

        return self._client._get_collection(method, params)
