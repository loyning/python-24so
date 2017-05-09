class Payments:
    def __init__(self, client=None):
        self.client = client
        self.service = 'Payment'

    def get_payment(self):
        api = self.client.get_client(self.service)
        payment = api.factory.create('Payment')
        return payment

    def register_payment(self, payment, params={}, **options):
        api = self.client.get_client(self.service)

        method = api.service.RegisterInvoicePayment

        return self.client.get(method, payment, **options)

    def register_payments(self, payments, params={}, **options):
        api = self.client.get_client(self.service)

        params = api.factory.create('ArrayOfPayment')
        params.Payment.extend(payments)

        method = api.service.RegisterInvoicePayments

        return self.client.get_collection(method, params, **options)
