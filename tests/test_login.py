import unittest

from tfsoffice import Client, exceptions


class TestPDF(unittest.TestCase):
    def test_login_error(self):
        with self.assertRaises(exceptions.WebFault):
            Client(None, None, None)

if __name__ == '__main__':
    unittest.main()
