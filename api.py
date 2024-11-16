from flask import Flask, jsonify, request

app = Flask(__name__)

# دیتابیس موقت برای ذخیره حساب‌های بانکی
accounts = {
    "user1": {"balance": 1000},
    "user2": {"balance": 1500}
}

@app.route('/balance/<username>', methods=['GET'])
def get_balance(username):
    if username in accounts:
        return jsonify({"balance": accounts[username]["balance"]}), 200
    else:
        return jsonify({"error": "Account not found"}), 404

@app.route('/deposit', methods=['POST'])
def deposit():
    data = request.json
    username = data.get("username")
    amount = data.get("amount")

    if username in accounts and amount > 0:
        accounts[username]["balance"] += amount
        return jsonify({"message": "Deposit successful", "balance": accounts[username]["balance"]}), 200
    return jsonify({"error": "Invalid request"}), 400

@app.route('/withdraw', methods=['POST'])
def withdraw():
    data = request.json
    username = data.get("username")
    amount = data.get("amount")

    if username in accounts and amount > 0 and accounts[username]["balance"] >= amount:
        accounts[username]["balance"] -= amount
        return jsonify({"message": "Withdrawal successful", "balance": accounts[username]["balance"]}), 200
    return jsonify({"error": "Insufficient balance or invalid request"}), 400

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.json
    from_user = data.get("from_user")
    to_user = data.get("to_user")
    amount = data.get("amount")

    if from_user in accounts and to_user in accounts and amount > 0 and accounts[from_user]["balance"] >= amount:
        accounts[from_user]["balance"] -= amount
        accounts[to_user]["balance"] += amount
        return jsonify({"message": "Transfer successful"}), 200
    return jsonify({"error": "Transfer failed"}), 400
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
