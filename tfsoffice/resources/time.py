class Time:
    def __init__(self, client=None):
        self.client = client
        self.service = 'Time'

    def get_hours(self, **kwargs):
        """
        Valid params are in HourSearch

        - Status        HourStatus
        - TypeOfWorkId  int
        - ContactId     int
        - StopTime      DateTime
        - ProjectId     int
        """
        api = self.client.get_client(self.service)

        params = api.factory.create('HourSearch')
        for key, value in kwargs.iteritems():
            setattr(params, key, value)

        method = api.service.GetHours

        return self.client.get_collection(method, params)
