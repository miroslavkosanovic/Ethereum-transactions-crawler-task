# Ethereum-transactions-crawler-task
An application that allows a user to view transaction data from the Ethereum blockchain associated with a specific wallet address W that the user inputs, starting with block B. 

The application gets iformation on:
    Wallets (adresses)
    Amounts of ETH associated with transactions made to and from the given Wallet W 

Then it proceeds to show them in a simple human-readable way (ideally through a web page).

Also the application, given a date in YYYY-MM-DD format, returns the exact value of ETH/other tokens that were available on the given adress a YYYY-MM-DD 00:00 UTC time.

# To run this web scraping application 
Prerequisites: Python version 3.0 or later,pip ("curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py", "python get-pip.py"), Flask ("pip install flask"), requests("pip install requests")

1. Clone the repository
3. Run main.py ("python main.py")
4. Enter localhost:5000 in your web browser