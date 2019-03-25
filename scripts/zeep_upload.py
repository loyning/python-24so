import base64
from zeep import Client
from zeep.plugins import HistoryPlugin

# LOGIN
auth = Client('https://api.24sevenoffice.com/authenticate/v001/authenticate.asmx?WSDL')
auth_factory = auth.type_factory('ns0')
# Select AI 2
cred = auth_factory.Credential(Username='aitest@mailinator.com', Password='jij-S4Ss', ApplicationId='825d89ae-5049-4058-bba2-6e29b3728f59', IdentityId='310d5fd3-0002-4047-a03b-0000009b00eb')

session_id = auth.service.Login(cred)

# UPLOAD
history = HistoryPlugin()

api = Client('https://webservices.24sevenoffice.com/Economy/Accounting/Accounting_V001/AttachmentService.asmx?WSDL', plugins=[history, ])
api.transport.session.headers['Cookie'] = 'ASP.NET_SessionId=%s' % session_id

factory = api.type_factory('ns0')

location = 'Journal'
path = '/Users/rune/Downloads/Scam+Alert-640x360 (1).jpg'
filetype = 'Jpeg'

image_type = factory.ImageType(filetype)

# load file from disk
with open(path, 'rb') as f:
    content = f.read()

file_obj = api.service.Create(filetype)
file_obj.FrameInfo = factory.ArrayOfImageFrameInfo()

# create one frame per image
frame = factory.ImageFrameInfo(Id=1, Status=0, StampNo=api.service.GetStampNo())

file_obj.FrameInfo.ImageFrameInfo.append(frame)

max_length = 2000 * 1024
offset = 0
while offset <= len(content):
    # extract next part of the content
    part = content[offset:offset + max_length]
    # part = part.encode('base64')
    part = base64.b64encode(part)
    # print('uploading offset = {}, bytes = {}'.format(offset, len(part)))

    api.service.AppendChunk(file_obj, part, offset)

    offset += max_length

location = factory.AttachmentLocation('Journal')
api.service.Save(file_obj, location)
