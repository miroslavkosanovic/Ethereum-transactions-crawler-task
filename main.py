import requests, os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from datetime import datetime

# Set up Flask web application
app = Flask(__name__)

load_dotenv()
# Etherscan API key 
etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
infura_api_key = os.getenv("INFURA_API_KEY")

BNB_TOKEN_ADDRESS = '0xB8c77482e45F1F44dE1745F52C74426C631bDD52'
STETH_TOKEN_ADDRESS = '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84'

def wei_to_eth(wei):
    return wei / 1e18

def retrieve_transaction_data(wallet_address, starting_block):
    try:
        # todo: check if starting_block else don't pass or pass 1 
        #  todo: make sure its 
        # create helper function to check wallet_address 
        #  create helper funciton to check starting_block 
        #  Unit test: when no wallet is passed 
        # unit test: no start_block is passed 
        #  unit test: api is down - error message

        # Check if starting_block is provided and a non-negative number
        if not starting_block:
            starting_block = 1
        elif not starting_block.isdigit() or int(starting_block) < 0:
            raise ValueError("Invalid starting block number")


        # Retrieve the transaction data using the Etherscan API
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&startblock={starting_block}&endblock=latest&sort=asc&apikey={etherscan_api_key}"

        response = requests.get(url)
        data = response.json()

        if data.get("status") == "1" and data.get("result") is not None:
            transactions = data["result"]

            # Convert the value from Wei to ETH in each transaction
            for tx in transactions:
                tx["value_eth"] = wei_to_eth(int(tx["value"]))
            return transactions
        else:
            error_message = data.get("message", "Unknown error")
            raise ValueError(f"Failed to retrieve transaction data: {error_message}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError("Failed to connect to the Etherscan API:", str(e))

def retrieve_wallet_creation_date(wallet_address):
    try:
        # Retrieve the earliest transaction for the wallet using the Etherscan API
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=latest&sort=asc&apikey={etherscan_api_key}"
        response = requests.get(url)
        data = response.json()

        if data.get("status") == "1" and data.get("result") is not None:
            transactions = data["result"]
            if len(transactions) > 0:
                earliest_timestamp = int(transactions[0]["timeStamp"])
                wallet_creation_date = datetime.fromtimestamp(earliest_timestamp)
                return wallet_creation_date
            else:
                raise ValueError("No transactions found for the wallet")

        else:
            error_message = data.get("message", "Unknown error")
            raise ValueError(f"Failed to retrieve transaction data: {error_message}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError("Failed to connect to the Etherscan API:", str(e))

def retrieve_balance_at_date(wallet_address, check_date):
    # todo: helper function - sanitize date: 
    # not too far in the past 
    # not in the future 
    # constrains to the date of creation: error message if too far in the past 

    try:
        wallet_creation_date = retrieve_wallet_creation_date(wallet_address)
        if check_date < wallet_creation_date:
            raise ValueError("Invalid check date: Date is before wallet creation")

        # Convert the date to Unix timestamp
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if check_date > today:
            raise ValueError("Invalid check date. Please enter a date on or before today.")
        
        unix_timestamp = int(check_date.timestamp())
                
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'eth_blockNumber',
        }

        response = requests.post(infura_api_key, json=payload) 
        data = response.json()

        if "result" in data:
            # Get the balance in Wei
            balance_wei = int(data["result"], 16)

            return balance_wei
        else:
            error_message = data.get("error", "Unknown error") 
            # todo Unit Test 
            raise ValueError(f"Failed to retrieve balance: {error_message}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError("Failed to connect to the Ethereum JSON-RPC API:", str(e))

# sanitize wallet_address 
# sanitize token_contract_address
def retrieve_token_balance(wallet_address, token_contract_address):
    try:
        # Retrieve the token balance using the Ethereum JSON-RPC API        
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'eth_call',
            'params': [
                {
                    'to': token_contract_address,
                    'data': f'0x70a08231000000000000000000000000{wallet_address[2:]}' 
                },
                'latest'
            ],
        }

        # todo: check what happens if no headers is passed 
        response = requests.post(infura_api_key, json=payload)
        data = response.json()

        if 'result' in data:
            result = data['result']
            if result == '0x':
                # Token balance is zero
                return 0
            else:
                # Get the token balance in Wei
                token_balance_wei = int(result, 16)
                return token_balance_wei
        else:
            error_message = data.get("error", "Unknown error")
            raise ValueError(f"Failed to retrieve token balance: {error_message}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError("Failed to connect to the Ethereum JSON-RPC API:", str(e))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        wallet_address = request.form['wallet_address']
        starting_block = request.form['starting_block']
        
        # trow exception if no wallet_address
        # sanitize starting_block 
        try:
            transactions = retrieve_transaction_data(wallet_address, starting_block)

            if not transactions:
                return render_template("index.html", error_message="No transactions found.")

            wallet_data = [{"date": datetime.fromtimestamp(int(tx["timeStamp"])),
                    "value": wei_to_eth(float(tx["value"])), 
                }
                for tx in transactions
            ]
            return render_template("transaction_data.html", transactions=transactions, wallet_data=wallet_data)

        except (ValueError, ConnectionError) as e:
            return render_template("index.html", error_message=str(e))

    return render_template("index.html")

@app.route('/balance', methods=['POST'])
def balance():
    if request.method == 'POST':
        wallet_address = request.form['wallet_address']
        check_date = request.form['check_date']
        try:
            check_date = datetime.strptime(check_date, "%Y-%m-%d")
            balance_wei = retrieve_balance_at_date(wallet_address, check_date)
            balance_eth = balance_wei / 1e18 #helper function to calculate eth

            # Retrieve token balances
            token_balances = {
                'Bnb': retrieve_token_balance(wallet_address, BNB_TOKEN_ADDRESS),  
                'stETH': retrieve_token_balance(wallet_address, STETH_TOKEN_ADDRESS) 
                        }
            return render_template("balance.html", wallet_address=wallet_address, check_date=check_date, eth_balance_eth=balance_eth, token_balances=token_balances)

        except (ValueError, ConnectionError) as e:
            return render_template("balance.html", error_message=str(e))

    return render_template("balance.html")
if __name__ == '__main__':
    app.run(debug=True)
