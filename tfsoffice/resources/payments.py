class Payments:
    def __init__(self, client=None):
        self._client = client
        self._service = 'Payment'

    def get_payment(self):
        api = self._client._get_client(self._service)
        payment = api.factory.create('Payment')
        return payment

    def register_payment(self, payment, params={}, **options):
        api = self._client._get_client(self._service)

        method = api.service.RegisterInvoicePayment

        return self._client._get(method, payment, **options)

    def register_payments(self, payments, params={}, **options):
        api = self._client._get_client(self._service)

        params = api.factory.create('ArrayOfPayment')
        params.Payment.extend(payments)

        method = api.service.RegisterInvoicePayments

        return self._client._get_collection(method, params, **options)
