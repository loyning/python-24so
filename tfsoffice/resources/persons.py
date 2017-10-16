import datetime


class Persons:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Person'

    def find_by_id(self, id, args={}, **options):
        api = self._client._get_client(self._service)

        params = api.factory.create('PersonSearchParameters')
        params.Id = id

        method = api.service.GetPersonsDetailed

        return self._client._get(method, params, **options)

    def find_by_name(self, name, args={}, **options):
        api = self._client._get_client(self._service)

        params = api.factory.create('PersonSearchParameters')
        params.Name = name

        method = api.service.GetPersons

        return self._client._get_collection(method, params, **options)

    def find_by_email(self, email, args={}, **options):
        api = self._client._get_client(self._service)

        params = api.factory.create('PersonSearchParameters')
        params.Email = email

        method = api.service.GetPersons

        return self._client._get_collection(method, params, **options)

    def search(self, **kwargs):
        """
        Valid parameters: Id, Name, ConsumerPersonNo, IsEmployee, CustomerId, EmployeeId, ChangedAfter, Email
        """
        valid_keys = ['Id', 'Name', 'ConsumerPersonNo', 'IsEmployee', 'CustomerId', 'EmployeeId', 'ChangedAfter', 'Email']
        for key in kwargs:
            if key not in valid_keys:
                raise AttributeError('Not a valid search parameter: "{}"'.format(key))

        api = self._client._get_client(self._service)

        params = api.factory.create('PersonSearchParameters')
        if 'IsEmployee' in kwargs:
            is_employee = kwargs.pop('IsEmployee')
            state = api.factory.create('TriState')
            if is_employee:
                params.IsEmployee = state['True']
            else:
                params.IsEmployee = state['False']

        if 'ChangedAfter' in kwargs:
            changed_after = kwargs.pop('ChangedAfter')
            if not isinstance(changed_after, datetime.date) or isinstance(changed_after, datetime.datetime):
                raise AttributeError('ChangedAfter must be a valid datetime.date/datetime.datetime instance.')
            params.ChangedAfter = changed_after

        for key in kwargs:
            setattr(params, key, kwargs.get(key))

        method = api.service.GetPersons

        return self._client._get_collection(method, params, **kwargs)

    def list_employees(self, params={}, **options):
        api = self._client._get_client(self._service)

        state = api.factory.create('TriState')

        params = api.factory.create('PersonSearchParameters')
        params.IsEmployee = state['True']

        method = api.service.GetPersonIdsByUserName

        return self._client._get_collection(method, params, **options)

    def find_by_username(self, username):
        api = self._client._get_client(self._service)

        method = api.service.GetPersonIdsByUserName

        return self._client._get_collection(method, username)
