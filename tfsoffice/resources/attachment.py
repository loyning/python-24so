import base64
from io import BytesIO


class Attachment:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Attachment'

    def upload_file(self, path, location='Journal'):
        api = self._client._get_client(self._service)

        if path.lower().endswith('.jpeg') or path.lower().endswith('.jpg'):
            filetype = 'Jpeg'
        elif path.lower().endswith('.png'):
            filetype = 'Png'
        elif path.lower().endswith('.tif') or path.lower().endswith('.tiff'):
            filetype = 'Tiff'
        else:
            raise AttributeError('Filetype not supported')

        types = api.factory.create('ImageType')
        if not hasattr(types, filetype):
            raise AttributeError('Filetype not supported')
        loc = api.factory.create('AttachmentLocation')
        if not hasattr(loc, location):
            raise AttributeError('Location not supported')

        # load file from disk
        with open(path, 'rb') as f:
            content = f.read()

        file_obj = api.service.Create(filetype)
        file_obj.FrameInfo = api.factory.create('ArrayOfImageFrameInfo')

        # create one frame per image
        frame = api.factory.create('ImageFrameInfo')
        frame.Id = 1  # PAGE_NO = always 1
        frame.Status = 0
        frame.StampNo = api.service.GetStampNo()

        # add the frame/image to the file object via the array of image frame info
        file_obj.FrameInfo.ImageFrameInfo.append(frame)

        # max chunk size
        # max_length = api.service.GetMaxRequestLength()
        max_length = 2500

        # upload the files
        offset = 0
        while offset <= len(content):
            # extract next part of the content
            part = content[offset:offset + max_length]
            # part = part.encode('base64')
            part = base64.b64encode(part)
            # print('uploading offset = {}, bytes = {}'.format(offset, len(part)))

            api.service.AppendChunk(file_obj, part, offset)

            offset += max_length

        # print('All chunks uploaded OK')
        api.service.Save(file_obj, location)

        return dict(
            Id=file_obj.Id,
            Type=file_obj.Type,
            StampNo=frame.StampNo,
            Location=location,
        )
        # return self._client._get_collection(method, None)

    def upload_files(self, images, location='Journal'):
        api = self._client._get_client(self._service)

        loc = api.factory.create('AttachmentLocation')
        if not hasattr(loc, location):
            raise AttributeError('Location not supported')

        stamp_no = api.service.GetStampNo()
        files = []

        for frame_no, path in enumerate(images):
            if path.lower().endswith('.jpeg') or path.lower().endswith('.jpg'):
                filetype = 'Jpeg'
            elif path.lower().endswith('.png'):
                filetype = 'Png'
            elif path.lower().endswith('.tif') or path.lower().endswith('.tiff'):
                filetype = 'Tiff'
            else:
                raise AttributeError('Filetype not supported')

            types = api.factory.create('ImageType')
            if not hasattr(types, filetype):
                raise AttributeError('Filetype not supported')

            # load file from disk
            with open(path, 'rb') as f:
                content = f.read()

            file_obj = api.service.Create(filetype)
            file_obj.FrameInfo = api.factory.create('ArrayOfImageFrameInfo')

            # create one frame per image
            frame = api.factory.create('ImageFrameInfo')
            frame.Id = 1
            frame.Status = 0
            frame.StampNo = stamp_no

            # add the frame/image to the file object via the array of image frame info
            file_obj.FrameInfo.ImageFrameInfo.append(frame)

            # max chunk size
            # max_length = api.service.GetMaxRequestLength()
            max_length = 2500

            # upload the files
            offset = 0
            while offset <= len(content):
                # extract next part of the content
                part = content[offset:offset + max_length]
                # part = part.encode('base64')
                part = base64.b64encode(part)
                # print('uploading offset = {}, bytes = {}'.format(offset, len(part)))

                api.service.AppendChunk(file_obj, part, offset)

                offset += max_length

            # print('All chunks uploaded OK')
            api.service.Save(file_obj, location)

            files.append(file_obj)

        return dict(
            # Id=file_obj.Id,
            # Type=file_obj.Type,
            StampNo=stamp_no,
            Location=location,
        )
        # return self._client._get_collection(method, None)

    def download_stamp_no(self, stamp_no):
        api = self._client._get_client(self._service)

        maxlength = api.service.GetMaxRequestLength()

        fsp = api.factory.create('FileSearchParameters')
        fsp.StampNo.int.append(stamp_no)

        fileinfo = api.service.GetFileInfo(fsp)

        filesize = api.service.GetSize(fileinfo[0])

        content = ''
        for offset in range(0, filesize, maxlength):
            data = api.service.DownloadChunk(fileinfo[0], offset, maxlength)
            content += base64.b64decode(data)
        data = api.service.DownloadChunk(fileinfo[0], offset, filesize - offset)
        content += base64.b64decode(data)

        buf = BytesIO(content)
        return buf
