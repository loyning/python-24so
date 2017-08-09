class Time:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Time'

    def get_hours(self, **kwargs):
        """
        Valid params are in HourSearch

        - Status        HourStatus
        - TypeOfWorkId  int
        - ContactId     int
        - StopTime      DateTime
        - ProjectId     int
        """
        api = self._client._get_client(self._service)

        params = api.factory.create('HourSearch')
        for key, value in kwargs.iteritems():
            setattr(params, key, value)

        method = api.service.GetHours

        return self._client._get_collection(method, params)
