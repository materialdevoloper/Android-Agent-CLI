import sys
import os
import time

sys.path.append('C:/Users/User/llm_playground/pixel7_apps_cli')
import adb_core
from grab_cli import vision_extractor
from grab_cli import json_merger

def run_vision_chain(scrolls=3):
    print("Starting Vision Extraction Chain...")
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    json_dir = os.path.join(output_dir, "vision_jsons")
    os.makedirs(json_dir, exist_ok=True)
    
    # Clean previous jsons
    for f in os.listdir(json_dir):
        os.remove(os.path.join(json_dir, f))
        
    for i in range(scrolls):
        img_path = os.path.join(output_dir, f"vision_feed_{i}.png")
        json_path = os.path.join(json_dir, f"vision_feed_{i}.json")
        
        print(f"\n[Screen {i+1}] Capturing screenshot...")
        adb_core.screencap(img_path)
        
        print(f"[Screen {i+1}] Extracting via Qwen Vision...")
        vision_extractor.extract_restaurants(img_path, json_path)
        
        print("Scrolling down...")
        adb_core.swipe(540, 1800, 540, 600, duration=800)
        time.sleep(2)
        
    print("\nMerging Vision JSONs...")
    final_json = os.path.join(output_dir, "final_vision_coffee.json")
    json_merger.merge_json_files(json_dir, final_json)

if __name__ == "__main__":
    run_vision_chain()
