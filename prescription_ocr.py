# prescription_ocr.py
# Gemma 4 E2B OCR via llama-server + regex verification.

import requests
import base64
import json
import re
from prescription_verifier import cross_validate_drugs, display_verification

LLAMA_SERVER = "http://127.0.0.1:8080/v1/chat/completions"


def extract_drugs_from_image(image_path):
    """
    Two-stage extraction:
      Stage A: Gemma 4 E2B extracts drugs (LLM flexibility)
      Stage B: Regex verifies (deterministic reliability)
    """
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    prompt_text = (
        "You are reading a prescription. Extract ALL medicine names. "
        "Indian prescriptions use abbreviations: T.=Tablet, Cap.=Capsule, "
        "BD=twice daily, OD=once daily, TDS=three times daily. "
        "Output ONLY a JSON list like: "
        "[{\"name\": \"DrugName\", \"dose\": \"2mg\", \"freq\": \"BD\"}]. "
        "Do NOT invent names."
    )

    payload = {
        "model": "gemma-4-E2B-it",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt_text},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]
        }]
    }

    response = requests.post(LLAMA_SERVER, json=payload)
    result = response.json()
    raw_content = result["choices"][0]["message"]["content"]

    print(f"[OCR RAW] {raw_content[:200]}...")

    # Parse JSON from LLM output
    match = re.search(r'\[.*\]', raw_content, re.DOTALL)
    llm_drugs = []
    if match:
        try:
            llm_drugs = json.loads(match.group())
        except json.JSONDecodeError:
            pass

    if not llm_drugs:
        # Fallback: split by lines
        llm_drugs = [{"name": line.strip()} for line in raw_content.split('\n')
                     if line.strip() and not line.startswith('[')]

    print(f"[LLM] Extracted {len(llm_drugs)} drugs")

    # Stage B: Regex verification
    verified = cross_validate_drugs(llm_drugs, raw_content)
    summary = display_verification(verified)

    return verified, summary


if __name__ == "__main__":
    import sys
    image_path = sys.argv[1] if len(sys.argv) > 1 else \
        r"D:\Iqoo_Practice_Project\imagesFolder\prescription-template_x.png"
    verified, summary = extract_drugs_from_image(image_path)
    print(json.dumps(verified, indent=2))