class Attachment:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Attachment'

    def upload_image(self, content, filetype, location='Journal'):
        api = self._client._get_client(self._service)

        types = api.factory.create('ImageType')
        if not hasattr(types, filetype):
            raise AttributeError('Filetype not supported')

        file_obj = api.service.Create(filetype)
        loc = api.factory.create('AttachmentLocation')
        if not hasattr(loc, location):
            raise AttributeError('Location not supported')

        # upload the file
        api.service.AppendChunk(file_obj, content, 0)

        api.service.Save(file_obj, location)

        return dict(
            Id=file_obj.Id,
            Type=file_obj.Type,
            StampNo=file_obj.StampNo
        )
        # return self._client._get_collection(method, None)
