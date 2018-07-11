import datetime
import re


class Accounts:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Account'

    def get_account_list(self):
        api = self._client._get_client(self._service)

        method = api.service.GetAccountList

        return self._client._get_collection(method, None)

    def get_taxcode_list(self):
        api = self._client._get_client(self._service)

        method = api.service.GetTaxCodeList

        return self._client._get_collection(method, None)

    def get_entry_id(self, year):
        api = self._client._get_client(self._service)

        method = api.service.GetEntryId

        param = api.factory.create('EntryId')
        param.Date = datetime.date(year, 1, 1)
        param.SortNo = 1

        return self._client._get(method, param)

    def get_type_list(self):
        api = self._client._get_client(self._service)

        method = api.service.GetTypeList

        return self._client._get_collection(method, None)

    def _get_test_bundle(self, imagepath=None, location='Journal'):
        data = dict(
            allow_difference=True,
            direct_ledger=False,
            save_option=1,
            bundle_name='AI {}'.format(datetime.datetime.today().isoformat()),
            entries=[
                dict(
                    # link_id='internal id',  # must be GUID - xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                    customer_id=1,
                    account_no=4350,

                    # invoice fields
                    date="2018-01-20",
                    due_date="2018-01-30",
                    department_id=None,  # optional
                    project_id=None,  # optional
                    invoice_refno=123,  # optional
                    bankaccount='28002222222',
                    currency_id="NOK",  # defaults to NOK
                    currency_rate=None,  # optional
                    currency_unit=None,  # optional

                    amount=1000,
                    tax_no=1,
                    # imagepath='/path/to/and/image',
                    comment="#13132",  # optional
                ),
                dict(
                    # link_id='internal id',  # must be GUID - xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                    customer_id=1,
                    account_no=4350,

                    # invoice fields
                    date="2018-01-20",
                    due_date="2018-01-30",
                    department_id=None,  # optional
                    project_id=None,  # optional
                    invoice_refno=123,  # optional
                    bankaccount='28002222222',
                    currency_id="NOK",  # defaults to NOK
                    currency_rate=None,  # optional
                    currency_unit=None,  # optional

                    amount=250,
                    tax_no=1,
                    # imagepath='/path/to/and/image',
                    comment="#13132",  # optional
                ),
                dict(
                    # link_id='internal id',  # must be GUID - xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                    customer_id=1,
                    account_no=2400,

                    # invoice fields
                    date="2018-01-20",
                    due_date="2018-01-30",
                    department_id=None,  # optional
                    project_id=None,  # optional
                    invoice_refno=123,  # optional
                    bankaccount='28002222222',
                    currency_id="NOK",  # defaults to NOK
                    currency_rate=None,  # optional
                    currency_unit=None,  # optional

                    amount=-1250,
                    tax_no=0,
                    # imagepath='/path/to/and/image',
                    comment="#13132",  # optional
                ),
            ]
        )

        if imagepath:
            result = self._client.attachment.upload_file(imagepath, location)
            stamp_no = result['StampNo']

            for e in data['entries']:
                e['stamp_no'] = stamp_no

        return data

    def save_entries_as_bundle(self, entries, images=[], bundle_prefix='AI', location='Journal', bundle_name=None):
        if images:
            res = self._client.attachment.upload_files(images, location=location)
            for e in entries:
                e['stamp_no'] = res['StampNo']

        year = list(set([re.sub(r'-\d\d-\d\d', '', e['date']) for e in entries]))
        if len(year) > 1:
            raise ValueError('Multiple years found in entries')
        year = int(year[0])

        data = dict(
            allow_difference=True,
            direct_ledger=False,
            save_option=1,
            bundle_name='{} {}'.format(bundle_prefix, datetime.datetime.today().isoformat()),
            entries=entries,
            location=location,
            year=year
        )

        if bundle_name:
            data['bundle_name'] = bundle_name

        return self.save_bundle_list(data)

    def save_entries_to_ledger(self, entries, images=[], bundle_prefix='AI', location='Journal', bundle_name=None):
        if images:
            res = self._client.attachment.upload_files(images, location=location)
            for e in entries:
                e['stamp_no'] = res['StampNo']

        year = list(set([re.sub(r'-\d\d-\d\d', '', e['date']) for e in entries]))
        if len(year) > 1:
            raise ValueError('Multiple years found in entries')
        year = int(year[0])

        data = dict(
            allow_difference=True,
            direct_ledger=True,
            save_option=0,
            bundle_name='{} {}'.format(bundle_prefix, datetime.datetime.today().isoformat()),
            entries=entries,
            location=location,
            year=year
        )

        if bundle_name:
            data['bundle_name'] = bundle_name

        return self.save_bundle_list(data)

    def save_bundle_list(self, data):
        api = self._client._get_client(self._service)
        method = api.service.SaveBundleList

        # attachment location
        location = data.get('location', 'Journal')

        if len(data.get('entries', [])) == 0:
            raise Exception('No entried found.')

        entries = data.get('entries', [])

        #
        # BUNDLE LIST
        #
        bundlelist = api.factory.create('BundleList')
        # Allow difference in credit/debit balance.
        # This is only applicable when saving journal data (see SaveOption) below.
        # Default value is false.
        bundlelist.AllowDifference = data.get('allow_difference', True)

        # DirectLedger
        # If set to false use customer ledger. If set to true use account that is set directly.
        bundlelist.DirectLedger = data.get('direct_ledger', False)

        # SaveOption
        # Can be either 1 or 0.
        # Setting 1 saves the bundle as a journal which can then be reviewed and edited on the 24SevenOffice web site.
        # Setting 0 saves the bundle directly to the ledger.
        bundlelist.SaveOption = data.get('save_option', 1)

        # Attachments
        attachments = {}

        # cached stamp
        cache_stamp = None

        #
        # BUNDLE
        #
        bundle = api.factory.create('Bundle')

        # The YearId is set to the current year of the bundle. e.g. 2017.
        bundle.YearId = int(data.get('year', datetime.datetime.today().year))
        # Can be defined for either Bundle or Voucher. This is an entry type.
        # The No property from GetTransactionTypes is used.
        bundle.Sort = 1

        # The name of the bundle.
        bundle.Name = data.get('bundle_name', None)

        # BundleDirectAccounting: If set to false it automatically calculates VAT. If set to true it does not calculate VAT.
        # This is only applicable when saving journal data (see SaveOption).
        if bundlelist.SaveOption:
            bundle.BundleDirectAccounting = False

        # Get the next available TransactionNo
        entry_id = api.factory.create('EntryId')
        entry_id.Date = datetime.datetime.today()
        entry_id.SortNo = 3  # incoming invoice/creditnote
        entry_id.EntryNo = 1  # temp value
        entry_id = api.service.GetEntryId(entry_id)

        #
        # Find unique invoices in entries
        #
        invoice_refs = list(set([entry['invoice_refno'] for entry in entries]))

        for pos, invoice_ref in enumerate(invoice_refs):
            #
            # VOUCHER / invoice
            #
            # This the transaction number of the voucher.
            voucher = api.factory.create('Voucher')

            # Can be defined for either Bundle or Voucher. This is an entry type. The No property from
            # GetTransactionTypes is used.
            voucher.Sort = 1

            voucher.TransactionNo = entry_id.EntryNo + pos

            voucher_entries = [e for e in entries if e['invoice_refno'] == invoice_ref]

            for row in voucher_entries:
                #
                # ENTRY / a single transaction
                #
                entry = api.factory.create('Entry')
                entry.CustomerId = row.get('customer_id', None)
                entry.AccountId = row.get('account_no', None)
                if row.get('date', None):
                    entry.Date = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
                if row.get('due_date', None):
                    entry.DueDate = datetime.datetime.strptime(row['due_date'], '%Y-%m-%d')
                entry.Period = row.get('period', None)
                entry.Amount = row.get('amount', None)  # this is the amount INCL VAT
                entry.CurrencyId = row.get('currency_id', 'NOK')
                entry.CurrencyRate = row.get('currency_rate', None)
                entry.CurrencyUnit = row.get('currency_unit', None)
                entry.DepartmentId = row.get('department_id', None)
                entry.ProjectId = row.get('project_id', None)
                entry.InvoiceReferenceNo = row.get('invoice_refno', None)
                entry.InvoiceOcr = row.get('invoice_kid', None)
                entry.TaxNo = row.get('tax_no', 0)
                entry.BankAccountNo = row.get('bankaccount', None)
                entry.Comment = row.get('comment', None)

                # attachments
                entry.StampNo = row.get('stamp_no', cache_stamp)
                imagepath = row.get('imagepath', None)
                if row.get('stamp_no', cache_stamp):
                    entry.StampNo = row.get('stamp_no', cache_stamp)

                elif imagepath:
                    # print('Found attachment: ', imagepath)
                    if imagepath not in attachments:
                        print('Uploading attachment...')
                        result = self._client.attachment.upload_file(imagepath, location)
                        attachments[imagepath] = result['StampNo']
                    entry.StampNo = attachments[imagepath]

                else:
                    # create a stamp number
                    # print('create stamp number')
                    att = self._client._get_client('Attachment')
                    cache_stamp = att.service.GetStampNo()
                    # print('Created stamp number: ', entry.StampNo)
                cache_stamp = entry.StampNo

                if row.get('link_id', None):
                    entry.LinkId = row['link_id']

                # add entry to voucher
                voucher.Entries.Entry.append(entry)

            # add voucher to bundle
            bundle.Vouchers.Voucher.append(voucher)

        # add bundle to bundlelist
        bundlelist.Bundles.Bundle.append(bundle)

        return self._client._get(method, bundlelist)
