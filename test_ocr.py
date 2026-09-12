
import requests
import base64
import json

# Path to your image
IMAGE_PATH = r"D:\Iqoo_Practice_Project\imagesFolder\prescription-template_x.png"

# Read and encode the image
with open(IMAGE_PATH, "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode()

# Build the request
payload = {
    "model": "gemma-4-E2B-it",
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "You are reading a prescription. Extract ALL medicine names you can see. Indian prescriptions use abbreviations: T. = Tablet, Cap. = Capsule, BD = twice daily, OD = once daily, TDS = three times daily. Output ONLY a JSON list like: [{\"name\": \"DrugName\", \"dose\": \"2mg\", \"freq\": \"BD\"}]. If unclear, write uncertain. Do NOT invent names."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_b64}"
                    }
                }
            ]
        }
    ]
}

# Send to llama-server
response = requests.post(
    "http://127.0.0.1:8080/v1/chat/completions",
    json=payload
)

# Print the result
result = response.json()
print(json.dumps(result, indent=2))

# Also print just the content
print("\n" + "="*60)
print("EXTRACTED CONTENT:")
print("="*60)
print(result["choices"][0]["message"]["content"])
