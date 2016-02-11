import datetime
import base64
import sys
import os
sys.path.append('.')
from tfsoffice import TwentyFour  # noqa
username = raw_input('Username/email: ')
password = raw_input('Password: ')
applicationid = raw_input('Application id: ')
crm = TwentyFour(username.strip(), password.strip(), applicationid.strip())
client = crm.get_client('Attachment')

search = client.factory.create('FileSearchParameters')

search.AttachmentRegisteredAfter = datetime.datetime(2011, 1, 1)
search.HasStampNo = True
search.FileApproved = True
status, results = client.service.GetFileInfo(search)

status, maxbuffer = client.service.GetMaxRequestLength()

for imagefile in results.ImageFile:
    status, size = client.service.GetSize(imagefile)
    print 'file is %s bytes' % size

    # generate filename
    customername = 'ukjent'
    invoicedate = ''
    if imagefile.StampMeta:
        for tmp in imagefile.StampMeta.KeyValuePair:
            if tmp.Key == 'CustomerName' and tmp.Value:
                customername = tmp.Value
            elif tmp.Key == 'InvoiceDate':
                invoicedate = tmp.Value

    if not os.path.exists(customername):
        os.mkdir(customername)
    filename = '%s/%s-stamp-%s.%s' % (customername, invoicedate, imagefile.StampNo, imagefile.Type.lower())
    if os.path.exists(filename):
        print '%s already downloaded' % filename
        continue

    print 'Downloading: ', filename

    out = open(filename, 'wb')
    pos = 0
    while pos <= size:
        print 'read from', pos, 'of', size,
        status, raw = client.service.DownloadChunk(imagefile, pos, maxbuffer)
        pos += maxbuffer
        print 'done',
        data = base64.decodestring(raw)
        out.write(data)
        print ' write '
    out.flush()
    out.close()
