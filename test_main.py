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
    
    def test_retrieve_balance_at_date(self):
        # Test valid inputs
        wallet_address = "0x1234567890123456789012345678901234567890"
        check_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        balance_eth = retrieve_balance_at_date(wallet_address, check_date)
        self.assertIsInstance(balance_eth, float)

        # Test check date before wallet creation
        wallet_creation_date = datetime(2022, 1, 1)
        with self.assertRaises(ValueError):
            retrieve_balance_at_date(wallet_address, wallet_creation_date)

        # Test check date after today
        future_date = datetime.today().replace(year=2025)
        with self.assertRaises(ValueError):
            retrieve_balance_at_date(wallet_address, future_date)


if __name__ == '__main__':
    unittest.main()
