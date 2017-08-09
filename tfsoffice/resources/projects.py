class Projects:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Project'

    def find_by_id(self, project_id):
        api = self._client._get_client(self._service)

        method = api.service.GetSingleProject
        params = project_id

        return self._client._get(method, params)

    def find_by_name(self, name):
        api = self._client._get_client(self._service)

        params = api.factory.create('ProjectSearch')
        params.Search = name

        method = api.service.GetProjectList

        return self._client._get_collection(method, params)

    def find_by_customerid(self, customerid):
        api = self._client._get_client(self._service)

        params = api.factory.create('ProjectSearch')
        params.CustomerId = customerid

        method = api.service.GetProjectList

        return self._client._get(method, params)

    def find_mine(self):
        api = self._client._get_client(self._service)

        params = api.factory.create('ProjectSearch')
        params.MyProjects = True

        method = api.service.GetProjectList

        return self._client._get_collection(method, params)
