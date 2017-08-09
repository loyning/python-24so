class _Projects:
    def __init__(self, client=None):
        self.client = client
        self.service = 'Project'

    def find_by_id(self, project_id, params={}, **options):
        api = self.client.get_client(self.service)

        method = api.service.GetSingleProject
        params = project_id

        return self.client.get(method, params, **options)

    def find_by_name(self, name, params={}, **options):
        api = self.client.get_client(self.service)

        params = api.factory.create('ProjectSearch')
        params.Search = name

        method = api.service.GetProjectList

        return self.client.get_collection(method, params, **options)

    def find_by_customerid(self, customerid, params={}, **options):
        api = self.client.get_client(self.service)

        params = api.factory.create('ProjectSearch')
        params.CustomerId = customerid

        method = api.service.GetProjectList

        return self.client.get_collection(method, params, **options)

    def find_mine(self, params={}, **options):
        api = self.client.get_client(self.service)

        params = api.factory.create('ProjectSearch')
        params.MyProjects = True

        method = api.service.GetProjectList

        return self.client.get_collection(method, params, **options)
