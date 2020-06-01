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

        years = list(set([re.sub(r'-\d\d-\d\d', '', e['date']) for e in entries]))

        if len(years) > 1:
            raise ValueError('Multiple years found in entries')

        year = int(years[0])

        data = dict(
            allow_difference=True,
            direct_ledger=False,
            save_option=1,
            bundle_name='{} {}'.format(bundle_prefix, datetime.datetime.today().isoformat()),
            entries=entries,
            location=location,
            transaction_type_no=transaction_type_no,
        )

        if bundle_name:
            data['bundle_name'] = bundle_name

        bundle = self.create_bundle(data, year)
        bundles = [bundle]

        bundlelist = self.create_bundlelist(data, bundles, years)

        return self.save_bundle_list(bundlelist)

    def save_entries_to_ledger(self, entries, images=[], bundle_prefix='AI', location='Journal', bundle_name=None, transaction_type_no=1, prohibit_multiple_years=True):
        if images:
            res = self._client.attachment.upload_files(images, location=location)
            for e in entries:
                e['stamp_no'] = res['StampNo']

        years = list(set([self.get_entry_year(e) for e in entries]))

        if len(years) > 1 and prohibit_multiple_years:
            raise ValueError('Multiple years found in entries')

        data = dict(
            allow_difference=False,
            direct_ledger=True,
            save_option=0,  # direct to ledger
            bundle_name='{} {}'.format(bundle_prefix, datetime.datetime.today().isoformat()),
            entries=entries,
            location=location,
            transaction_type_no=transaction_type_no,
        )

        if bundle_name:
            data['bundle_name'] = bundle_name

        if prohibit_multiple_years:
            # bundles has just one bundle
            year = years[0]
            bundle = self.create_bundle(data, year)
            bundles = [bundle]

            bundlelist = self.create_bundlelist(data, bundles, years)

            return self.save_bundle_list(bundlelist)
        else:
            # collect each created bundle while iterating over years
            bundles = list([self.create_bundle(data, year) for year in years])

            bundlelist = self.create_bundlelist(data, bundles, years)

            return self.save_bundle_list(bundlelist)

    def print_entries(self, entries):
        accounts = self._client.accounts.get_taxcode_list()['results']
        account_list = dict([(row['TaxNo'], row) for row in accounts])

        for row in entries:
            vat_account = account_list[str(row['tax_no'])]
            print((row['comment'][:40].ljust(40), row['amount'], row['tax_no'], vat_account['AccountNo']))

    def get_entry_year(self, entry):
        date = entry.get('date', None)

        if date is None:
            return datetime.datetime.today().year
        else:
            year_as_string = re.sub(r'-\d\d-\d\d', '', date)
            return int(year_as_string)

    def select_entries_for_year(self, entries, year):
        return [e for e in entries if self.get_entry_year(e) == year]

    def partition_entries_by_invoice_stamp_no(self, entries):
        entry_lists = []

        for stamp_no in set([e.get('stamp_no', None) for e in entries]):
            entry_lists.append(
                [e for e in entries if e.get('stamp_no', None) == stamp_no]
            )

        return entry_lists

    def create_bundle(self, data, year):
        api = self._client._get_client(self._service)

        # Attachments
        # attachments = {}

        # cached stamp
        # cache_stamp = None

        #
        # BUNDLE
        #
        bundle = api.factory.create('Bundle')
        bundle.Vouchers = api.factory.create('ArrayOfVoucher')

        # The YearId is set to the current year of the bundle. e.g. 2017.
        bundle.YearId = year or int(datetime.datetime.today().year)
        # Can be defined for either Bundle or Voucher. This is an entry type.
        # The No property from GetTransactionTypes is used.
        bundle.Sort = int(data.get('transaction_type_no', 1))

        # The name of the bundle.
        bundle.Name = data.get('bundle_name', None)

        # BundleDirectAccounting:
        # This is only applicable when saving journal data (see SaveOption).
        #
        # - If set to false it automatically calculates VAT.
        #   (here, `save_option` is 0 when direct-to-ledger)
        #
        # - If set to true it does not calculate VAT.
        #   (when not direct-to-ledger, bundle.BundleDirectAccounting is not set here)
        if data.get('save_option', 1) == 1:
            bundle.BundleDirectAccounting = False

        entries_as_flat_list = data.get('entries', [])
        all_entries_in_year = self.select_entries_for_year(entries_as_flat_list, bundle.YearId)
        entries_in_year_by_invoice = self.partition_entries_by_invoice_stamp_no(all_entries_in_year)

        # Get the next available TransactionNo, within a given year
        entry_id = api.factory.create('EntryId')
        today = datetime.datetime.today()
        entry_id.Date = datetime.datetime(bundle.YearId, today.month, today.day)
        entry_id.SortNo = 3  # incoming invoice/creditnote
        entry_id.EntryNo = 1  # temp value
        entry_id = api.service.GetEntryId(entry_id)

        #
        # Find unique invoices in entries
        #
        # invoice_refs = list(set([entry['invoice_refno'] for entry in entries]))

        for pos, entries_in_year_for_invoice in enumerate(entries_in_year_by_invoice):

            #
            # VOUCHER / invoice entries in given year / transaction
            #
            # This the transaction number of the voucher.
            voucher = api.factory.create('Voucher')

            voucher.Entries = api.factory.create('ArrayOfEntry')

            # Can be defined for either Bundle or Voucher. This is an entry type. The No property from
            # GetTransactionTypes is used.
            voucher.Sort = int(data.get('transaction_type_no', 1))

            voucher.TransactionNo = entry_id.EntryNo + pos

            for row in entries_in_year_for_invoice:
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

        return bundle


    def create_bundlelist(self, data, bundles, years):
        api = self._client._get_client(self._service)

        if len(data.get('entries', [])) == 0:
            raise Exception('No entried found.')

        entries = data.get('entries', [])

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

        # add this single bundle to bundlelist

        # and add each bundle to bundlelist
        for bundle in bundles:
            bundlelist.Bundles.Bundle.append(bundle)

        return bundlelist

    def save_bundle_list(self, bundlelist):
        last_transaction_number_by_stamp_number = {}
        stamp_numbers_for_transaction_number = {}

        for bundle in bundlelist.Bundles.Bundle:
            for voucher in bundle.Vouchers.Voucher:
                for entry in voucher.Entries.Entry:
                    if entry.StampNo:
                        last_transaction_number_by_stamp_number[entry.StampNo] = voucher.TransactionNo
                        stamp_numbers_for_transaction_number = self.append_to_list_for_key(stamp_numbers_for_transaction_number, voucher.TransactionNo, entry.StampNo)

        stamp_numbers = list(last_transaction_number_by_stamp_number.keys())
        cache_stamp = stamp_numbers[0] if len(stamp_numbers) else None

        response = self.do_save_bundle_list(bundlelist, stamp_numbers_for_transaction_number, last_transaction_number_by_stamp_number, stamp_numbers, cache_stamp)

        return response

    def do_save_bundle_list(self, bundlelist, stamp_numbers_for_transaction_number, last_transaction_number_by_stamp_number, stamp_numbers, cache_stamp):
        api = self._client._get_client(self._service)
        method = api.service.SaveBundleList

        response = self._client._get(method, bundlelist)

        # Include extra data
        response['transaction_ids'] = last_transaction_number_by_stamp_number
        response['stamp_numbers'] = stamp_numbers
        response['stamp_numbers_for_transaction_number'] = stamp_numbers_for_transaction_number
        response['stamp_no'] = cache_stamp

        return response

    def append_to_list_for_key(self, dictionary, key, new_value):
        values = dictionary.get(key, [])
        values.append(new_value)
        dictionary[key] = list(set(values))

        return dictionary
