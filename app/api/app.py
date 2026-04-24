from flask import Flask, jsonify
import psutil
import time
import random

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({
        "service": "Self-Healing API",
        "version": "1.0.0",
        "status": "running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "api"})

@app.route("/metrics")
def metrics():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    return jsonify({
        "cpu_usage": cpu,
        "memory_usage": memory,
        "timestamp": time.time()
    })

@app.route("/simulate/spike")
def simulate_spike():
    end_time = time.time() + 10
    while time.time() < end_time:
        _ = [x**2 for x in range(10000)]
    return jsonify({"message": "CPU spike simulated for chaos testing"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
