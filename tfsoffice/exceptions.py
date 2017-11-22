class WebFault(Exception):
    def __init__(self, message, detail, faultcode):
        self.detail = detail
        self.faultcode = faultcode
        self.message = message


class TooManyResultsException(Exception):
    pass
