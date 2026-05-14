import time
import os
import json
import xml.etree.ElementTree as ET
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core

def extract_screen_texts(xml_path):
    """Extract all visible text from the current XML dump."""
    texts = []
    try:
        tree = ET.parse(xml_path)
        for node in tree.iter('node'):
            text = node.attrib.get('text', '').strip()
            desc = node.attrib.get('content-desc', '').strip()
            # Only collect meaningful text
            content = text if text else desc
            if content and len(content) > 2 and content not in texts:
                texts.append(content)
    except Exception as e:
        print(f"XML parse error: {e}")
    return texts

def extract_and_merge(max_scrolls=10, return_texts=False):
    """Scroll through the feed, extract text per screen, and merge into a structured JSON list."""
    print("Starting step-by-step structured extraction...")
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    temp_xml = os.path.join(output_dir, "temp_extract.xml")
    
    global_items = []
    seen_texts = set()
    
    for i in range(max_scrolls):
        print(f"\n[Screen {i+1}/{max_scrolls}] Dumping UI...")
        adb_core.dump_ui(temp_xml)
        
        screen_texts = extract_screen_texts(temp_xml)
        
        new_items_found = False
        # Very simple heuristic: Treat consecutive text blocks as related data
        # In a real RPA, this would use precise resource-id or positional bounding box grouping
        for text in screen_texts:
            if text not in seen_texts and "Sort By" not in text and "Delivery" not in text:
                seen_texts.add(text)
                global_items.append(text)
                new_items_found = True
                try:
                    print(f"  + Extracted: {text}")
                except UnicodeEncodeError:
                    print(f"  + Extracted: [Unicode Text]")
                
        if not new_items_found and i > 1:
            print("No new items found on this screen. Reached the end of the list!")
            break
            
        print("Scrolling down...")
        adb_core.swipe(540, 1800, 540, 600, duration=800)
        time.sleep(2) # wait for render
        
    print(f"\n[Success] Extracted {len(global_items)} unique data nodes.")
    
    if return_texts:
        try: os.remove(temp_xml)
        except: pass
        return global_items
        
    output_json = os.path.join(output_dir, "extracted_restaurants.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({"total": len(global_items), "items": global_items}, f, ensure_ascii=False, indent=2)
        
    print(f"Data saved to {output_json}")
    
    try: os.remove(temp_xml)
    except: pass
