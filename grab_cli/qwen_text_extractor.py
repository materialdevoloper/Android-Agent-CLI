import requests
import json
import xml.etree.ElementTree as ET

def extract_texts_from_xml(xml_path):
    texts = []
    tree = ET.parse(xml_path)
    for node in tree.iter('node'):
        text = node.attrib.get('text', '').strip()
        desc = node.attrib.get('content-desc', '').strip()
        content = text if text else desc
        if content and len(content) > 1 and content not in texts:
            texts.append(content)
    return texts

def extract_with_qwen(xml_path):
    texts = extract_texts_from_xml(xml_path)
    raw_text = "\n".join(texts)
    
    prompt = f"""You are a data extraction bot.
Here is a list of scraped texts from a cafe's menu page on a food delivery app.
Please extract all the coffee/drinks items.
For each item, output:
- "name": Item name
- "price": Price (if available)

Output ONLY a JSON array. Example:
[
  {{"name": "Iced Latte", "price": "150"}}
]

Raw scraped texts:
{raw_text}
"""

    payload = {
        "model": "local-model",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        res = requests.post("http://localhost:12345/v1/chat/completions", json=payload)
        output = res.json()['choices'][0]['message']['content'].strip()
        
        if output.startswith("```json"):
            output = output[7:-3]
        elif output.startswith("```"):
            output = output[3:-3]
            
        data = json.loads(output)
        
        with open("nip_cafe_menu.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print("Success! Extracted JSON saved to nip_cafe_menu.json")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_with_qwen("nip_cafe_dump.xml")
