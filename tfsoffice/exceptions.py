class WebFault(Exception):
    def __init__(self, message, detail, faultcode, params=None):
        self.detail = detail
        self.faultcode = faultcode
        self.message = message
        self.params = params

    def __str__(self):
        return self.message


class TooManyResultsException(Exception):
    pass
