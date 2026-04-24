from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "ai-predictor"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    features = np.array([[
        data["cpu_usage"],
        data["memory_usage"],
        data["error_rate"],
        data["response_time_ms"]
    ]])
    features_scaled = scaler.transform(features)
    prediction = model.predict(features_scaled)[0]
    probability = model.predict_proba(features_scaled)[0][1]
    return jsonify({
        "failure_predicted": bool(prediction),
        "failure_probability": round(float(probability), 4),
        "recommendation": "HEAL" if prediction else "OK"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
