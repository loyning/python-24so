class Projects:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Project'

    def find_by_id(self, project_id):
        api = self._client._get_client(self._service)
        #
        # WITH ZEEP
        # client = zeep.Client(wsdl, transport=transport)
        # return client.service.GetSingleProject(project_id)
        #
        method = api.service.GetSingleProject
        params = project_id

        return self._client._get(method, params)

    def find_by_name(self, name, detailed=False):
        api = self._client._get_client(self._service)

        params = api.factory.create('ProjectSearch')
        params.Search = name

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self._client._get_collection(method, params)

    def find_by_customerid(self, customerid, detailed=False):
        api = self._client._get_client(self._service)

        params = api.factory.create('ProjectSearch')
        params.CustomerId = customerid

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self._client._get(method, params)

    def find_mine(self, detailed=False):
        api = self._client._get_client(self._service)

        params = api.factory.create('ProjectSearch')
        params.MyProjects = True

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self._client._get_collection(method, params)

    def find_by_date_changed(self, changed, detailed=False, **options):
        """
        Find project by ChangedAfter

        Returns a list of Projects
        """
        api = self._client._get_client(self._service)

        params = api.factory.create('ProjectSearch')
        params.ChangedAfter = changed

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self._client._get_collection(method, params)

    def list(self, **options):
        """
        Find project by ChangedAfter

        Returns a list of Projects
        """
        api = self._client._get_client(self._service)

        method = api.service.GetProjectNameList

        return_values = api.factory.create('ProjectShort')

        return self._client._get_collection(method, None, return_values=return_values)
