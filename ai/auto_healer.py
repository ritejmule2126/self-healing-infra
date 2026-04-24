#!/usr/bin/env python3
import time, requests, subprocess
from datetime import datetime

AI_API      = "http://ai-predictor-svc.self-healing.svc.cluster.local:8000"
APP_METRICS = "http://self-healing-api-svc.self-healing.svc.cluster.local/metrics"
NAMESPACE   = "self-healing"
DEPLOYMENT  = "self-healing-api"
INTERVAL    = 30
THRESHOLD   = 0.75

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def get_metrics():
    try:
        r = requests.get(APP_METRICS, timeout=5)
        d = r.json()
        return {"cpu_usage": d.get("cpu_usage", 0),
                "memory_usage": d.get("memory_usage", 0),
                "error_rate": 0.5, "response_time_ms": 200}
    except Exception as e:
        log(f"Metrics error: {e}")
        return None

def predict(metrics):
    try:
        r = requests.post(f"{AI_API}/predict", json=metrics, timeout=5)
        return r.json()
    except Exception as e:
        log(f"Prediction error: {e}")
        return None

def restart_failed_pods():
    r = subprocess.run([
        "kubectl","get","pods","-n",NAMESPACE,
        "--field-selector=status.phase!=Running",
        "-o","jsonpath={.items[*].metadata.name}"
    ], capture_output=True, text=True)
    for pod in r.stdout.strip().split():
        if pod:
            subprocess.run(["kubectl","delete","pod",pod,"-n",NAMESPACE])
            log(f"Deleted crashed pod: {pod}")

def scale(replicas):
    subprocess.run(["kubectl","scale","deployment",DEPLOYMENT,
                    "-n",NAMESPACE,f"--replicas={replicas}"])
    log(f"Scaled {DEPLOYMENT} to {replicas} replicas")

def rolling_restart():
    subprocess.run(["kubectl","rollout","restart",
                    f"deployment/{DEPLOYMENT}","-n",NAMESPACE])
    log(f"Rolling restart triggered on {DEPLOYMENT}")

def heal(prob):
    if prob > 0.90:
        log(f"CRITICAL ({prob:.0%}) — rolling restart + scale to 4")
        rolling_restart()
        time.sleep(30)
        scale(4)
    elif prob > THRESHOLD:
        log(f"HIGH ({prob:.0%}) — restarting crashed pods + scale to 4")
        restart_failed_pods()
        scale(4)

def main():
    log("Auto-Healer started")
    consecutive = 0
    while True:
        metrics = get_metrics()
        if metrics:
            log(f"CPU={metrics['cpu_usage']:.1f}% MEM={metrics['memory_usage']:.1f}%")
            pred = predict(metrics)
            if pred:
                prob = pred["failure_probability"]
                rec  = pred["recommendation"]
                log(f"AI says: {rec} (probability={prob:.0%})")
                if rec == "HEAL":
                    consecutive += 1
                    if consecutive >= 2:
                        heal(prob)
                        consecutive = 0
                else:
                    consecutive = 0
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
