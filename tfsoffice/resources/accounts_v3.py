import datetime
import re


class AccountsV3:
    def __init__(self, client=None):
        self._client = client
        self._service = 'AccountVersionThree'

    # NOTE - save_option 0 (and direct_ledger and allow_difference)
    # For _Posting_ invoices directly to General Ledger
    def save_entries_to_ledger(self, entries, images=[], bundle_prefix='AI', location='Journal', bundle_name=None, transaction_type_no=1, entry_series_id=3):
        """
        POST entries
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
            ignore_warnings=True,
            allow_difference=False,
            direct_ledger=True,
            save_option=0,  # direct to ledger
            bundle_name='{} {}'.format(bundle_prefix, datetime.datetime.today().isoformat()),
            entries=entries,
            location=location,
            year=year,
            transaction_type_no=transaction_type_no,
            entry_series_id=entry_series_id,
        )

        if bundle_name:
            data['bundle_name'] = bundle_name

        return self.save_bundle_list(data)

    # NOTE - save_option 1 is hard-coded already on bundlelist (check other fns above)
    #      - that also would have the effect of setting to this in the code below:
    #        `bundle.BundleDirectAccounting = False`
    #      - see comments on other hard-coded values in the function below
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

        # A new setting available in /Economy/Account/V003/AccountService.asmx?WSD
        #
        # Setting this _to True by default_, as a workaround to issues on 24SO side,
        # until we move to their REST API:
        # "This is the fastest way for us to proceed since there [is] a lot of
        # business logic behind warnings."
        #
        # Note that this could miss some warnings or errors, perhaps including
        # rounding errors, but we won't know until this is tested against their
        # service.
        bundlelist.IgnoreWarnings = data.get('ignore_warnings', True)

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
        # previously, this was 3 (still is the default, denoting incoming invoice/creditnote)
        entry_id.SortNo = data['entry_series_id']
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
                # TODO AccountNo; is value same as here ('account_no')
                #                 or need to use AccountNo from Account ?
                #
                # AccountId is replaced by AccountNo in Account/V003:
                # https://api-beta.24sevenoffice.com/Economy/Account/V003/AccountService.asmx?WSDL
                entry.AccountNo = row.get('account_no', None)
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

        # TODO - here capture request XML and response and return both in an array
        # Note that response is mutated here as a way to provide data; could do that for request, too.
        response = self._client._get(method, bundlelist)
        response['transaction_ids'] = transaction_numbers
        response['stamp_numbers'] = stamp_numbers
        # response['bundlelist'] = bundlelist
        response['stamp_no'] = cache_stamp

        return response
