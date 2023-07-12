import unittest
from datetime import datetime
from main import (
    retrieve_transaction_data,
    retrieve_wallet_creation_date,
    retrieve_balance_at_date
)

class TestMain(unittest.TestCase):
    def test_retrieve_transaction_data(self):
        # Test valid inputs
        wallet_address = "0x1234567890123456789012345678901234567890"
        starting_block = "1000000"
        transactions = retrieve_transaction_data(wallet_address, starting_block)
        self.assertIsInstance(transactions, list)

        # Test invalid starting block
        invalid_starting_block = "-100"
        with self.assertRaises(ValueError):
            retrieve_transaction_data(wallet_address, invalid_starting_block)

    def test_retrieve_wallet_creation_date(self):
        # Test valid inputs
        wallet_address = "0x1234567890123456789012345678901234567890"
        creation_date = retrieve_wallet_creation_date(wallet_address)
        self.assertIsInstance(creation_date, datetime)

        # Test invalid wallet address
        invalid_wallet_address = ""
        with self.assertRaises(ValueError):
            retrieve_wallet_creation_date(invalid_wallet_address)


if __name__ == '__main__':
    unittest.main()
