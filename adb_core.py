import subprocess
import time
import xml.etree.ElementTree as ET
import os

ADB_PATH = os.environ.get("ADB_PATH", "adb")
DEVICE_ID = os.environ.get("ADB_DEVICE_ID", "")

def run_adb(cmd):
    """Run an ADB command and return its output."""
    device_arg = f"-s {DEVICE_ID} " if DEVICE_ID else ""
    full_cmd = f'"{ADB_PATH}" {device_arg}{cmd}'
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ADB Error: {result.stderr}")
    return result.stdout.strip()

def tap(x, y):
    """Simulate a tap at (x, y)."""
    run_adb(f"shell input tap {x} {y}")

def swipe(x1, y1, x2, y2, duration=500):
    """Simulate a swipe from (x1, y1) to (x2, y2)."""
    run_adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")

def dump_ui(output_path="current_ui.xml"):
    """Dump the UI hierarchy to a local file."""
    run_adb("shell uiautomator dump /data/local/tmp/dump.xml")
    run_adb(f"pull /data/local/tmp/dump.xml {output_path}")

def screencap(output_path="screen.png"):
    """Capture a screenshot to a local file."""
    device_arg = f"-s {DEVICE_ID} " if DEVICE_ID else ""
    full_cmd = f'"{ADB_PATH}" {device_arg}exec-out screencap -p > "{output_path}"'
    subprocess.run(full_cmd, shell=True)

def parse_bounds(bounds_str):
    """Parse a bounds string '[x1,y1][x2,y2]' into a tuple (x1, y1, x2, y2)."""
    bounds_str = bounds_str.replace("][", ",").replace("[", "").replace("]", "")
    return tuple(map(int, bounds_str.split(",")))

def find_text_bounds(xml_path, search_text):
    """Find the bounding box of a node containing the search_text (or any text in the list)."""
    if isinstance(search_text, str):
        search_texts = [search_text]
    else:
        search_texts = search_text
        
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        for node in root.iter('node'):
            text = node.attrib.get('text', '')
            content_desc = node.attrib.get('content-desc', '')
            for st in search_texts:
                if st.lower() in text.lower() or st.lower() in content_desc.lower():
                    return parse_bounds(node.attrib.get('bounds'))
    except Exception as e:
        print(f"Error parsing XML: {e}")
    return None

def click_text(search_text):
    """Semantically find a text on screen and click its center."""
    print(f"Locating '{search_text}' via XML DOM...")
    # Use a temporary xml file in the current directory
    temp_xml = "temp_click_dump.xml"
    dump_ui(temp_xml)
    bounds = find_text_bounds(temp_xml, search_text)
    if bounds:
        x1, y1, x2, y2 = bounds
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        print(f"Found '{search_text}' at {bounds}. Tapping ({center_x}, {center_y}).")
        tap(center_x, center_y)
        try:
            os.remove(temp_xml)
        except:
            pass
        return True
    
    print(f"Could not find '{search_text}' on the screen.")
    try:
        os.remove(temp_xml)
    except:
        pass
    return False

def wait_for_text(search_text, timeout=10):
    """Wait for a specific text to appear on screen (polling)."""
    print(f"Waiting for '{search_text}' to appear (timeout {timeout}s)...")
    start_time = time.time()
    temp_xml = "temp_wait_dump.xml"
    while time.time() - start_time < timeout:
        dump_ui(temp_xml)
        if find_text_bounds(temp_xml, search_text):
            print(f"[OK] Found '{search_text}'!")
            try:
                os.remove(temp_xml)
            except:
                pass
            return True
        time.sleep(1)
    
    print(f"[ERROR] Timeout waiting for '{search_text}'.")
    try:
        os.remove(temp_xml)
    except:
        pass
    return False

def wait_and_click_text(search_text, timeout=10):
    """Wait for text to appear and then click it."""
    if wait_for_text(search_text, timeout):
        return click_text(search_text)
    return False

def dismiss_popups():
    """Attempt to clear common blocking popups."""
    common_dismiss_texts = ["No thanks", "Not now", "Skip", "Dismiss"]
    for text in common_dismiss_texts:
        if click_text(text):
            print(f"Dismissed popup using button: '{text}'")
            time.sleep(1)
            return True
    return False


def find_and_tap(text, max_scrolls=10):
    """Scroll down until text is found, then tap it."""
    for i in range(max_scrolls):
        print(f"Looking for '{text}' (Scroll {i})...")
        dump_ui("temp_find.xml")
        bounds = find_text_bounds("temp_find.xml", text)
        if bounds:
            x = (bounds[0] + bounds[2]) // 2
            y = (bounds[1] + bounds[3]) // 2
            print(f"Found '{text}' at {bounds}. Tapping ({x}, {y})")
            tap(x, y)
            try: os.remove("temp_find.xml")
            except: pass
            return True
        print("Not found, scrolling down...")
        swipe(540, 1800, 540, 600, duration=800)
        time.sleep(2)
        try: os.remove("temp_find.xml")
        except: pass
    
    print(f"Could not find '{text}' after {max_scrolls} scrolls.")
    return False

def paste_text(text):
    print(f"Injecting text safely: {text}")
    for char in text:
        if char == ' ':
            run_adb("shell input keyevent 62") # Space
        else:
            run_adb(f"shell input text '{char}'")
        time.sleep(0.05)

