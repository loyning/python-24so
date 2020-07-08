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

    def _get_test_entries(self):

        invoice_ref = datetime.date.today().toordinal()

        entries = [
            dict(
                # link_id='internal id',  # must be GUID - xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
                customer_id=1,
                account_no=4350,

                # invoice fields
                date="2018-01-20",
                due_date="2018-01-30",
                department_id=None,  # optional
                project_id=None,  # optional
                invoice_refno=invoice_ref,  # optional
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
                invoice_refno=invoice_ref,  # optional
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
                invoice_refno=invoice_ref,  # optional
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

        return entries

    # def post_invoice(self, entries, bundle_name=None, doc_type='invoice'):
    #     # POST - direct to ledger
    #     # allow_difference = False
    #     # direct_ledger = True
    #     # save_option = 0

    #     pass

    # def transfer_invoices(self, invoices, bundle_name=None):

    #     # location = 'Journal'

    #     if not bundle_name:
    #         bundle_prefix = 'AI'
    #         bundle_name = '{} {}'.format(bundle_prefix, datetime.datetime.today().isoformat())

    #     # TRANSFER
    #     allow_difference = True
    #     direct_ledger = False
    #     save_option = 1

    #     # The bundle year is set to the current year of the bundle. e.g. 2017.
    #     bundle_year = 2019

    #     bundle_list = dict(
    #         allow_difference=allow_difference,
    #         direct_ledger=direct_ledger,
    #         save_option=save_option,
    #         bundle=dict(
    #             name=bundle_name,
    #             year=bundle_year,
    #             sort=1,  # invoice / credit note The No property from GetTransactionTypes is used.
    #             vouchers=[
    #                 dict(  # invoice
    #                     sort=1,  # invoice / credit note The No property from GetTransactionTypes is used.
    #                     entries=[
    #                         dict(
    #                             position=0,  # ordering 0 - X
    #                             customer_id=None,  # tfso customer id
    #                             account_no=None,  # cost account nr
    #                             date=None,  # issue date
    #                             due_date=None,
    #                             period=None,  # accrual
    #                             amount=None,
    #                             currency_id='NOK',
    #                             currency_unit=1,
    #                             currency_rate=1,
    #                             project_id=None,
    #                             invoice_refno=None,
    #                             invoice_kid=None,
    #                             tax_no=None,
    #                             bankaccount=None,
    #                             comment=None,
    #                             stamp_no=None,  # attachment / image
    #                             link_id=None,
    #                         )
    #                     ],
    #                 )
    #             ]
    #         )
    #     )
    #     return bundle_list

    def save_entries_as_bundle(self, entries, images=[], bundle_prefix='AI', location='Journal', bundle_name=None, transaction_type_no=1):
        """
        TRANSFER

        Marcin uploads images and sets stamp_no in entries
        """
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
            year=year,
            transaction_type_no=transaction_type_no,
        )

        if bundle_name:
            data['bundle_name'] = bundle_name

        return self.save_bundle_list(data)

    def save_entries_to_ledger(self, entries, images=[], bundle_prefix='AI', location='Journal', bundle_name=None, transaction_type_no=1):
        if images:
            res = self._client.attachment.upload_files(images, location=location)
            for e in entries:
                e['stamp_no'] = res['StampNo']

        year = list(set([re.sub(r'-\d\d-\d\d', '', e['date']) for e in entries]))
        if len(year) > 1:
            raise ValueError('Multiple years found in entries')
        year = int(year[0])

        data = dict(
            allow_difference=False,
            direct_ledger=True,
            save_option=0,  # direct to ledger
            bundle_name='{} {}'.format(bundle_prefix, datetime.datetime.today().isoformat()),
            entries=entries,
            location=location,
            year=year,
            transaction_type_no=transaction_type_no,
        )

        if bundle_name:
            data['bundle_name'] = bundle_name

        return self.save_bundle_list(data)

    def print_entries(self, entries):
        accounts = self._client.accounts.get_taxcode_list()['results']
        account_list = dict([(row['TaxNo'], row) for row in accounts])

        for row in entries:
            vat_account = account_list[str(row['tax_no'])]
            print((row['comment'][:40].ljust(40), row['amount'], row['tax_no'], vat_account['AccountNo']))

    def create_bundlelist(self, data):
        api = self._client._get_client(self._service)

        if len(data.get('entries', [])) == 0:
            raise Exception('No entried found.')

        entries = data.get('entries', [])

        # group entries by stamp_no to get unique invoices
        invoices = []
        for stamp_no in set([e.get('stamp_no', None) for e in entries]):
            invoices.append(
                [e for e in entries if e.get('stamp_no', None) == stamp_no]
            )

        # get bank details about the vendor
        customer_ids = list(set([e['customer_id'] for e in entries]))
        giro_numbers = list(set([e['giro_number'] for e in entries]))

        if self._client._country_code.upper() == 'SE' and customer_ids and giro_numbers:
            # load vendor to get payment info from CRM
            vendor = self._client.companies.find_by_id(customer_ids[0])

            # if giro number does not match value in CRM - change it
            if vendor.get('BankAccountNo') != giro_numbers[0]:
                stored_value = vendor.get('BankAccountNo').replace('-', '')
                giro_number = giro_numbers[0].replace('-', '')

                if stored_value == giro_number:
                    for e in entries:
                        e['bankaccount'] = vendor.get('BankAccountNo')
                print(entries)

        #
        # Add CurrencyRate to entries
        #
        try:
            rate_res = self._client.client.get_currency_list()
            if rate_res['count'] >= 1:
                rates = dict([(x['Symbol'], x['Rate']) for x in rate_res['results']])
                for entry in entries:
                    entry['currency_rate'] = rates.get(entry['currency_id'], None) or None

        except Exception as ex:
            print('ERROR getting currency_rate: %s' % ex)

        #
        # BUNDLE LIST
        #
        bundlelist = api.factory.create('BundleList')

        bundlelist.Bundles = api.factory.create('ArrayOfBundle')

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
        # attachments = {}

        # cached stamp
        # cache_stamp = None

        transaction_numbers = []

        #
        # BUNDLE
        #
        bundle = api.factory.create('Bundle')
        bundle.Vouchers = api.factory.create('ArrayOfVoucher')

        # The YearId is set to the current year of the bundle. e.g. 2017.
        bundle.YearId = int(data.get('year', datetime.datetime.today().year))
        # Can be defined for either Bundle or Voucher. This is an entry type.
        # The No property from GetTransactionTypes is used.
        bundle.Sort = int(data.get('transaction_type_no', 1))

        # The name of the bundle.
        bundle.Name = data.get('bundle_name', None)

        # BundleDirectAccounting: If set to false it automatically calculates VAT. If set to true it does not calculate VAT.
        # This is only applicable when saving journal data (see SaveOption).
        if bundlelist.SaveOption:
            bundle.BundleDirectAccounting = False

        # Get the next available TransactionNo
        entry_id = api.factory.create('EntryId')
        today = datetime.datetime.today()
        entry_id.Date = datetime.datetime(data['year'], today.month, today.day)
        entry_id.SortNo = 3  # incoming invoice/creditnote
        entry_id.EntryNo = 1  # temp value
        entry_id = api.service.GetEntryId(entry_id)

        #
        # Find unique invoices in entries
        #
        # invoice_refs = list(set([entry['invoice_refno'] for entry in entries]))

        for pos, invoice in enumerate(invoices):

            #
            # VOUCHER / invoice
            #
            # This the transaction number of the voucher.
            voucher = api.factory.create('Voucher')

            voucher.Entries = api.factory.create('ArrayOfEntry')

            # Can be defined for either Bundle or Voucher. This is an entry type. The No property from
            # GetTransactionTypes is used.
            voucher.Sort = int(data.get('transaction_type_no', 1))

            voucher.TransactionNo = entry_id.EntryNo + pos
            transaction_numbers.append(voucher.TransactionNo)

            for row in invoice:
                #
                # ENTRY / a single transaction
                #
                entry = api.factory.create('Entry')
                if row.get('position', None) is not None:
                    entry.SequenceId = row.get('position', None)
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
                entry.StampNo = row.get('stamp_no', None)

                if row.get('link_id', None):
                    entry.LinkId = row['link_id']

                # add entry to voucher
                voucher.Entries.Entry.append(entry)

            # add voucher to bundle
            bundle.Vouchers.Voucher.append(voucher)

        # add bundle to bundlelist
        bundlelist.Bundles.Bundle.append(bundle)
        return bundlelist

    def save_bundle_list(self, data):
        api = self._client._get_client(self._service)
        method = api.service.SaveBundleList

        bundlelist = self.create_bundlelist(data)

        transaction_numbers = {}

        for bundle in bundlelist.Bundles.Bundle:
            for voucher in bundle.Vouchers.Voucher:
                for entry in voucher.Entries.Entry:
                    if entry.StampNo:
                        transaction_numbers[entry.StampNo] = voucher.TransactionNo

        stamp_numbers = list(transaction_numbers.keys())

        cache_stamp = stamp_numbers[0] if len(stamp_numbers) else None

        response = self._client._get(method, bundlelist)
        response['transaction_ids'] = transaction_numbers
        response['stamp_numbers'] = stamp_numbers
        # response['bundlelist'] = bundlelist
        response['stamp_no'] = cache_stamp

        return response
