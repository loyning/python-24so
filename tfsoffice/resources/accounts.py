import datetime


class Accounts:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Account'

    def get_account_list(self):
        api = self._client._get_client(self._service)

        method = api.service.GetAccountList

        return self._client._get_collection(method, None)

    # def get_entry_id(self):
    #     api = self._client._get_client(self._service)

    #     method = api.service.GetEntryId

    #     param = api.factory.create('EntryId')

    #     return self._client._get(method, param)

    def save_bundle_list(self, data):
        # data = dict(
        #     allow_difference=True,
        #     direct_ledger=False,
        #     save_option=1,
        #     bundle_name='API Test #2',
        #     entries=[
        #         dict(
        #             customer_id=1,
        #             account_no=4350,
        #             date="2017-11-1",
        #             due_date="2017-11-15",
        #             amount=666.00,
        #             currency_id="NOK",  # defaults to NOK
        #             currency_rate=None,  # optional
        #             currency_unit=None,  # optional
        #             department_id=None,  # optional
        #             project_id=None,  # optional
        #             invoice_refno=None,  # optional
        #             tax_no=1,
        #             bankaccount='22222222222',
        #             comment="#13132",  # optional
        #         ),
        #         dict(
        #             customer_id=1,
        #             account_no=4360,
        #             date="2017-11-2",
        #             due_date="2017-11-16",
        #             amount=777.00,
        #             currency_id="NOK",
        #             currency_rate=None,
        #             currency_unit=None,
        #             tax_no=1,
        #             bankaccount='22222222222',
        #             comment="#13132",
        #         ),
        #     ]
        # )

        api = self._client._get_client(self._service)
        method = api.service.SaveBundleList

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

        #
        # BUNDLE
        #
        bundles = {}
        for row in data.get('entries', []):
            year = row['date'][:4]
            if year in bundles:
                bundle = bundles[year]
            else:
                bundle = api.factory.create('Bundle')

                # The YearId is set to the current year of the bundle. e.g. 2017.
                bundle.YearId = int(year)

                # Can be defined for either Bundle or Voucher. This is an entry type.
                # The No property from GetTransactionTypes is used.
                bundle.Sort = 1

                # The name of the bundle.
                bundle.Name = data.get('bundle_name', None)

                # If set to false it automatically calculates VAT. If set to true it does not calculate VAT.
                # This is only applicable when saving journal data (see SaveOption).
                if bundlelist.SaveOption:
                    bundle.BundleDirectAccounting = False
                bundles[year] = bundle

            #
            # VOUCHER
            #
            # This the transaction number of the voucher.
            voucher = api.factory.create('Voucher')

            # You can get the next available number by sending a request to GetEntryId.
            voucher.TransactionNo = 1

            # Can be defined for either Bundle or Voucher. This is an entry type. The No property from
            # GetTransactionTypes is used.
            voucher.Sort = 1

            #
            # ENTRY
            #
            entry = api.factory.create('Entry')
            entry.CustomerId = row['customer_id']
            entry.AccountId = row['account_no']
            entry.Date = datetime.datetime.strptime(row['date'], '%Y-%m-%d')
            entry.DueDate = datetime.datetime.strptime(row['due_date'], '%Y-%m-%d')
            if row.get('period', None):
                entry.Period = row['period']
            entry.Amount = row['amount']
            entry.CurrencyId = row.get('currency_id', 'NOK')
            if row.get('currency_rate', None):
                entry.CurrencyRate = row['currency_rate']
            if row.get('currency_unit', None):
                entry.CurrencyUnit = row['currency_unit']
            if row.get('department_id', None):
                entry.Department = row['department_id']
            if row.get('project_id', None):
                entry.Department = row['project_id']
            if row.get('invoice_refno', None):
                entry.InvoiceReferenceNo = row['invoice_refno']
            if row.get('invoice_kid', None):
                entry.InvoiceKid = row['invoice_kid']
            entry.TaxNo = row.get('tax_no', 'NOK')
            entry.BankAccountNo = row.get('bankaccount', None)

            if row.get('comment', None):
                entry.Comment = row['comment']
            # entry.StampNo = 0

            # add entry to voucher
            voucher.Entries.Entry.append(entry)

            # add voucher to bundle
            bundle.Vouchers.Voucher.append(voucher)

        # add bundle to bundlelist
        bundlelist.Bundles.Bundle.append(bundle)

        status, output = method(bundlelist)
        if status == 200:
            return status, output

        message = api.last_received()
        text = message.children[0].children[0].children[0].children[1].text
        return status, text
        # return self._client._get(method, bundlelist)
