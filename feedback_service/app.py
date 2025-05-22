from flask import Flask, request, jsonify

app = Flask(__name__)

feedbacks = []

@app.route('/feedback', methods=['POST'])
def add_feedback():
    data = request.json
    feedbacks.append(data)
    return jsonify({"status": "ok", "feedback": data}), 201

@app.route('/feedback', methods=['GET'])
def get_feedback():
    return jsonify(feedbacks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)