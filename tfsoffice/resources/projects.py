class Projects:
    def __init__(self, client=None):
        self.client = client
        self.service = 'Project'

    def find_by_id(self, project_id, params={}, **options):
        #
        # WITH ZEEP
        # client = zeep.Client(wsdl, transport=transport)
        # return client.service.GetSingleProject(project_id)
        #
        api = self.client.get_client(self.service)

        method = api.service.GetSingleProject
        params = project_id

        return self.client.get(method, params, **options)

    def find_by_name(self, name, detailed=False, **options):
        api = self.client.get_client(self.service)

        params = api.factory.create('ProjectSearch')
        params.Search = name

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self.client.get_collection(method, params, **options)

    def find_by_customerid(self, customerid, detailed=False, **options):
        api = self.client.get_client(self.service)

        params = api.factory.create('ProjectSearch')
        params.CustomerId = customerid

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self.client.get_collection(method, params, **options)

    def find_mine(self, detailed=False, **options):
        api = self.client.get_client(self.service)

        params = api.factory.create('ProjectSearch')
        params.MyProjects = True

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self.client.get_collection(method, params, **options)

    def find_by_date_changed(self, changed, detailed=False, **options):
        """
        Find project by ChangedAfter

        Returns a list of Projects
        """
        api = self.client.get_client(self.service)

        params = api.factory.create('ProjectSearch')
        params.ChangedAfter = changed

        if detailed:
            method = api.service.GetProjectsDetailed
        else:
            method = api.service.GetProjectList

        return self.client.get_collection(method, params, **options)
