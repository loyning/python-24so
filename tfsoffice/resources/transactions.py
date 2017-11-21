class Transactions:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Transaction'

    def get_transaction_types(self):
        api = self._client._get_client(self._service)

        method = api.service.GetTransactionTypes

        return self._client._get_collection(method, None)

