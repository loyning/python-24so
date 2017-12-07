import base64


class Attachment:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Attachment'

    def upload_image(self, path, location='Journal'):
        if path.lower().endswith('.jpeg') or path.lower().endswith('.jpg'):
            filetype = 'Jpeg'
        elif path.lower().endswith('.png'):
            filetype = 'Png'
        elif path.lower().endswith('.tif') or path.lower().endswith('.tiff'):
            filetype = 'Tiff'
        elif path.lower().endswith('.pdf'):
            filetype = 'Pdf'
        else:
            raise AttributeError('Filetype not supported')

        with open(path, 'rb') as f:
            content = base64.b64encode(f.read())

        return self.upload_content(content, filetype, location)

    def upload_content(self, content, filetype, location='Journal'):
        api = self._client._get_client(self._service)

        types = api.factory.create('ImageType')
        if not hasattr(types, filetype):
            raise AttributeError('Filetype not supported')
        loc = api.factory.create('AttachmentLocation')
        if not hasattr(loc, location):
            raise AttributeError('Location not supported')

        file_obj = api.service.Create(filetype)

        frame = api.factory.create('ImageFrameInfo')
        frame.Id = 1  # PAGE_NO = always 1
        frame.Status = 0
        frame.StampNo = api.service.GetStampNo()

        file_obj.FrameInfo = api.factory.create('ArrayOfImageFrameInfo')

        file_obj.FrameInfo.ImageFrameInfo.append(frame)

        # upload the file
        api.service.AppendChunk(file_obj, content, 0)

        api.service.Save(file_obj, location)

        return dict(
            Id=file_obj.Id,
            Type=file_obj.Type,
            StampNo=frame.StampNo
        )
        # return self._client._get_collection(method, None)
