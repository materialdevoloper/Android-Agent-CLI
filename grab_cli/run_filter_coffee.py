import sys
import os
import time

sys.path.append('C:/Users/User/llm_playground/pixel7_apps_cli')
import adb_core
from grab_cli import json_extractor

def run_chain():
    print("Launching Grab...")
    adb_core.run_adb("shell am force-stop com.grabtaxi.passenger")
    time.sleep(1)
    adb_core.run_adb("shell am start -n com.grabtaxi.passenger/com.grab.pax.newface.common.alias.DefaultLauncherAlias")
    
    adb_core.wait_for_text(["Food", "Mart", "Transport"], timeout=20)
    adb_core.dismiss_popups()
    adb_core.click_text("Food")
    
    print("Waiting for Food page...")
    adb_core.wait_for_text(["Search", "Search for a dish", "What shall we deliver?"], timeout=20)
    
    print("Searching for filter coffee...")
    adb_core.click_text("What shall we deliver?")
    time.sleep(1)
    
    # Safe input
    adb_core.paste_text("filter coffee")
    adb_core.run_adb("shell input keyevent 66") # enter
    
    print("Waiting for results...")
    adb_core.wait_for_text(["Sort", "Filter", "Delivery fee", "coffee"], timeout=20)
    time.sleep(3) # Wait for images to load
    
    print("Extracting data...")
    json_extractor.extract_and_merge(max_scrolls=5)

if __name__ == "__main__":
    run_chain()
