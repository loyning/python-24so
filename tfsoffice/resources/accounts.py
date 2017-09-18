class Accounts:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Account'

    def get_account_list(self,):
        api = self._client._get_client(self._service)

        method = api.service.GetAccountList

        return self._client._get_collection(method, None)
