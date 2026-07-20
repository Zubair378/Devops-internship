from flask import Flask, jsonify
import socket

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "good idea"})

@app.route('/info')
def info():
    return jsonify({
        "service": "frontend",
        "developer": "Zubair",
        "version": "1.0.0",
        "hostname": socket.gethostname()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
