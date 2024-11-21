from flask import Flask, jsonify, request
import uuid
from datetime import datetime

app = Flask(__name__)

# Temporary in-memory databases for accounts and transactions
accounts = {}
transactions = {}

# Helper function: Create a transaction entry
def create_transaction(account_id, amount, transaction_type, recipient_id=None):
    transaction_id = str(uuid.uuid4())
    transactions[transaction_id] = {
        "account_id": account_id,
        "type": transaction_type,
        "amount": amount,
        "timestamp": datetime.now().isoformat(),
        "recipient_id": recipient_id,
    }
    return transaction_id

# Endpoint: Create a new account
@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    username = data.get("username")
    initial_balance = data.get("initial_balance", 0)

    if username in accounts:
        return jsonify({"error": "Account already exists"}), 400

    account_id = str(uuid.uuid4())
    accounts[username] = {
        "id": account_id,
        "balance": initial_balance,
        "created_at": datetime.now().isoformat()
    }

    create_transaction(account_id, initial_balance, "Account Creation")
    return jsonify({"message": "Account created successfully", "account_id": account_id}), 201

# Endpoint: Get account balance
@app.route('/balance/<username>', methods=['GET'])
def get_balance(username):
    account = accounts.get(username)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    return jsonify({"balance": account["balance"]}), 200

# Endpoint: Deposit money
@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    username = data.get("username")
    amount = data.get("amount")

    if username not in accounts:
        return jsonify({"error": "Account not found"}), 404
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    accounts[username]["balance"] += amount
    create_transaction(accounts[username]["id"], amount, "Deposit")
    return jsonify({"message": "Deposit successful", "balance": accounts[username]["balance"]}), 200

# Endpoint: Withdraw money
@app.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    username = data.get("username")
    amount = data.get("amount")

    if username not in accounts:
        return jsonify({"error": "Account not found"}), 404
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    if accounts[username]["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    accounts[username]["balance"] -= amount
    create_transaction(accounts[username]["id"], -amount, "Withdrawal")
    return jsonify({"message": "Withdrawal successful", "balance": accounts[username]["balance"]}), 200

# Endpoint: Transfer money between accounts
@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_user = data.get("from_user")
    to_user = data.get("to_user")
    amount = data.get("amount")

    if from_user not in accounts or to_user not in accounts:
        return jsonify({"error": "One or both accounts not found"}), 404
    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    if accounts[from_user]["balance"] < amount:
        return jsonify({"error": "Insufficient balance"}), 400

    accounts[from_user]["balance"] -= amount
    accounts[to_user]["balance"] += amount

    create_transaction(accounts[from_user]["id"], -amount, "Transfer", accounts[to_user]["id"])
    create_transaction(accounts[to_user]["id"], amount, "Transfer", accounts[from_user]["id"])

    return jsonify({"message": "Transfer successful"}), 200

# Endpoint: Get all transactions for a user
@app.route('/transactions/<username>', methods=['GET'])
def get_transactions(username):
    account = accounts.get(username)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    account_id = account["id"]
    user_transactions = [
        txn for txn in transactions.values() if txn["account_id"] == account_id
    ]

    return jsonify({"transactions": user_transactions}), 200

# Endpoint: Get account statement
@app.route('/account_statement/<username>', methods=['GET'])
def account_statement(username):
    account = accounts.get(username)
    if not account:
        return jsonify({"error": "Account not found"}), 404

    account_id = account["id"]
    user_transactions = [
        txn for txn in transactions.values() if txn["account_id"] == account_id
    ]

    statement = {
        "account_id": account_id,
        "username": username,
        "balance": account["balance"],
        "transactions": user_transactions,
        "created_at": account["created_at"]
    }

    return jsonify(statement), 200

# Endpoint: Delete an account
@app.route('/delete_account', methods=['DELETE'])
def delete_account():
    data = request.json
    username = data.get("username")

    if username in accounts:
        del accounts[username]
        return jsonify({"message": "Account deleted successfully"}), 200
    return jsonify({"error": "Account not found"}), 400

# Endpoint: View all accounts and their information
@app.route('/view_all_accounts', methods=['GET'])
def view_all_accounts():
    return jsonify(accounts), 200

# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
