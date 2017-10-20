class Authenticate:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Authenticate'

    def login(self, username, password, applicationid, identityid=None):
        api = self._client._get_client(self._service)

        credential = api.factory.create('Credential')
        credential.ApplicationId = applicationid
        credential.IdentityId = identityid
        credential.Username = username
        credential.Password = password

        status, session_id = api.service.Login(credential)
        assert status == 200, 'Cannot authenticate with 24so, Status is not OK: %s' % status

        self._client._clients = {}
        self._client._headers = {'Cookie': 'ASP.NET_SessionId=%s' % session_id}
        return session_id

    def has_session(self):
        api = self._client._get_client(self._service)

        method = api.service.HasSession

        return self._client._get_collection(method, None)

    def get_identities(self):
        api = self._client._get_client(self._service)

        method = api.service.GetIdentities

        return_values = api.factory.create('ArrayOfIdentity')

        return self._client._get_collection(method, None, return_values=return_values)

    def set_identity(self, identity):
        api = self._client._get_client(self._service)

        method = api.service.SetIdentity

        params = api.factory.create('Identity')
        params.Id = identity.get('Id')
        params.Client.Id = identity.get('Client').get('Id', None)
        params.Client.Name = identity.get('Client').get('Name', None)
        params.IsCurrent = identity.get('IsCurrent', None)
        params.IsDefault = identity.get('IsDefault', None)
        params.IsProtected = identity.get('IsProtected', None)

        for key in identity.get('User', {}):
            setattr(params.User, key, identity['User'][key])

        for serverdata in identity.get('Servers', {}).get('Server', []):
            server = api.factory.create('Server')
            server.Id = serverdata.get('Id', None)
            server.Type = serverdata.get('Type', None)
            params.Servers.Server.append(server)

        return self._client._get(method, params)

    def set_identity_by_id(self, identityid):
        api = self._client._get_client(self._service)

        method = api.service.SetIdentityById

        return self._client._get(method, identityid)
