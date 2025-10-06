import requests
import json

response = requests.post(
    "http://localhost:8000/v1/completions",
    headers={"Content-Type": "application/json"},
    data=json.dumps({
        "model": "mistralai/Mistral-Small-24B-Instruct-2501",
        "prompt": "Explain the concept of reinforcement learning in simple terms.",
        "max_tokens": 500
    })
)

print(response.json()["choices"][0]["text"])
