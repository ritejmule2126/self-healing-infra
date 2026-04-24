import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

records = []
for i in range(5000):
    cpu = np.random.normal(30, 10)
    memory = np.random.normal(40, 15)
    error_rate = np.random.exponential(0.5)
    response_time = np.random.normal(200, 50)

    is_failure = 0
    if random.random() < 0.2:
        cpu = min(100, cpu + np.random.uniform(40, 60))
        memory = min(100, memory + np.random.uniform(30, 50))
        error_rate += np.random.uniform(5, 15)
        response_time += np.random.uniform(500, 2000)
        is_failure = 1

    records.append({
        "cpu_usage": max(0, min(100, cpu)),
        "memory_usage": max(0, min(100, memory)),
        "error_rate": max(0, error_rate),
        "response_time_ms": max(0, response_time),
        "failure": is_failure
    })

df = pd.DataFrame(records)
df.to_csv("training_data.csv", index=False)
print(f"Generated {len(df)} records")
print(f"Failure rate: {df['failure'].mean():.1%}")
