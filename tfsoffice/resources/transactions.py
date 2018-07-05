class Transactions:

    def __init__(self, client=None):
        self._client = client
        self._service = 'Transaction'

    def get_transaction_types(self):
        api = self._client._get_client(self._service)

        method = api.service.GetTransactionTypes

        return self._client._get_collection(method, None)

    def get_transactions(self, date_start, date_end, system_type='Miscellaneous', invoice_no=None, project_id=None, transaction_type_id=None, customer_id=None, stamp_no=None, account_no_start=None, account_no_end=None, transaction_no_start=None, transaction_no_end=None, has_invoice_id=None):

        api = self._client._get_client(self._service)

        tss = api.factory.create('TransactionSystemType')
        if system_type not in tss:
            raise AttributeError('Wrong SystemType: {}'.format(system_type))

        params = api.factory.create('TransactionSearchParameters')
        params.AccountNoStart = account_no_start
        params.AccountNoEnd = account_no_end
        params.CustomerId = customer_id
        params.DateStart = date_start
        params.DateEnd = date_end
        params.HasInvoiceId = has_invoice_id
        params.InvoiceNo = invoice_no
        params.ProjectId = project_id
        params.TransactionNoStart = transaction_no_start
        params.TransactionNoEnd = transaction_no_end
        params.TransactionTypeId = transaction_type_id
        params.StampNo = stamp_no
        params.SystemType = tss[system_type]

        # transactions = api.service.GetTransactions(searchParams=params)

        method = api.service.GetTransactions

        return self._client._get_collection(method, params)
