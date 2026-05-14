import base64
import requests
import json
import os
import re

LM_STUDIO_URL = "http://localhost:12345/v1/chat/completions"

from PIL import Image
import io

def encode_image_to_base64(image_path, max_size=768):
    try:
        with Image.open(image_path) as img:
            # Resize image to avoid massive token usage / empty string failures
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error resizing image: {e}")
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

def extract_restaurants(image_path, output_json_path=None):
    """Sends the image to local LM Studio and returns structured JSON."""
    if not os.path.exists(image_path):
        print(f"[Error] Image not found: {image_path}")
        return False

    print(f"Loading image {image_path} and sending to local Vision Model...")
    base64_image = encode_image_to_base64(image_path)
    
    prompt = """You are a precise data extraction bot.
Analyze this screenshot from a food delivery app (Grab) and extract all restaurant listings.
For each restaurant, extract:
- "name": The name of the restaurant.
- "rating": The star rating (if available, else null).
- "delivery_time": The estimated delivery time string (if available, else null).
- "discount": Any discount or promo text (e.g. '30% off', 'Free delivery', else null).

Output ONLY a raw JSON array of objects. Do not wrap in markdown or backticks. Example:
[
  {
    "name": "Meet Mala Noodles",
    "rating": "4.6 (584)",
    "delivery_time": "51 mins",
    "discount": "40% off"
  }
]"""

    payload = {
        "model": "local-model", # LM Studio usually ignores this if a model is loaded
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.1, # Keep it deterministic
        "max_tokens": 1500
    }

    try:
        response = requests.post(LM_STUDIO_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
        response.raise_for_status()
        result_text = response.json()['choices'][0]['message']['content'].strip()
        
        # Clean up possible markdown wrappers if the model ignores the instruction
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        result_text = result_text.strip()
        
        # Validate JSON
        data = json.loads(result_text)
        
        if output_json_path:
            os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[Success] Extracted {len(data)} restaurants to {output_json_path}")
            
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to connect to LM Studio: {e}")
        print("Make sure LM Studio is running on http://localhost:1234 with a vision model loaded.")
        return False
    except json.JSONDecodeError as e:
        print(f"[Error] Model output was not valid JSON: {e}")
        print(f"Raw Output:\n{result_text}")
        return False
