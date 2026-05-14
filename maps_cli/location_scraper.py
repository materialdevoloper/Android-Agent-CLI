import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core

def execute_search(query):
    """Open Google Maps via Deep-Link Intent to search directly (supports Unicode)."""
    import urllib.parse
    print(f"Opening Google Maps and searching for: {query}")
    adb_core.run_adb("shell input keyevent 224") # Wake up
    time.sleep(1)
    adb_core.run_adb("shell input swipe 540 2000 540 500") # Unlock
    time.sleep(1)
    
    # Force stop Maps to ensure a clean state
    adb_core.run_adb("shell am force-stop com.google.android.apps.maps")
    time.sleep(1)
    
    # URL Encode the query to support Japanese/Chinese
    formatted_query = urllib.parse.quote(query)
    
    # Fire the deep-link intent
    print(f"Firing Deep-Link Intent for: {query}")
    adb_core.run_adb(f'shell am start -a android.intent.action.VIEW -d "geo:0,0?q={formatted_query}" com.google.android.apps.maps')
    
    print("Waiting for Maps to load and execute search...")
    time.sleep(8) # Give it time to fly to Tokyo and render results
    print("Search executed. Waiting for your read-results command.")

def read_results():
    """Close the bottom sheet (if it's an ad) and read the results."""
    print("Sending BACK key to dismiss any single-location ad cards...")
    adb_core.run_adb("shell input keyevent 4")
    time.sleep(2)
    
    # We can also swipe up now to expand the actual list if needed
    print("Expanding the actual results list...")
    adb_core.swipe(540, 1800, 540, 400, duration=500)
    time.sleep(2)
    
    dump_path = "maps_result.xml"
    adb_core.dump_ui(dump_path)
    
    print(f"Scraped UI dumped to {dump_path}. Extracting readable names:")
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(dump_path)
        root = tree.getroot()
        for node in root.iter('node'):
            text = node.attrib.get('text', '').strip()
            if text and len(text) > 3:
                # Safe print to avoid CMD GBK encoding errors
                safe_text = text.encode('gbk', 'ignore').decode('gbk')
                if safe_text:
                    print(f"- {safe_text}")
    except Exception as e:
        print(f"Error extracting XML locally: {e}")
    
    return True

def sort_results(by):
    """Sort the maps results. Supports 'top_rated' or 'distance'."""
    print(f"Sorting results by: {by}")

    if by == "top_rated":
        print("Finding 'Top rated' chip...")
        adb_core.wait_and_click_text("Top rated")
    elif by == "distance":
        print("Finding 'Relevance' dropdown...")
        if adb_core.wait_and_click_text("Relevance"):
            print("Selecting 'Distance'...")
            adb_core.wait_and_click_text("Distance")
    else:
        print("Unsupported sort option.")
        return False
    return True

def scrape_details(auto=True):
    """Scroll the current place details page and stitch it."""
    print("Scraping details of the current place...")
    adb_core.dismiss_popups()
    from utils_cli import auto_scroller
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    output_filepath = os.path.join(output_dir, "place_details.png")
    
    auto_scroller.scroll_and_stitch(
        max_scrolls=20 if auto else 3,
        auto_stop=auto,
        output_filepath=output_filepath,
        work_dir=output_dir
    )
    print(f"Details saved to {output_filepath}")
    return True

def scrape_list(scrolls=3):
    """Scroll the search results list (bottom sheet) and stitch it."""
    print("Scraping search results list...")
        
    adb_core.dismiss_popups()
    
    # Expand the bottom sheet to cover more area
    # Swiping from the top of the bottom sheet (around Y=900 in high density) ensures we grab the handle
    print("Expanding the list by pulling the handle up...")
    adb_core.swipe(540, 900, 540, 200, duration=400)
    time.sleep(2)
    # Give it one more swipe just in case it didn't fully expand
    adb_core.swipe(540, 1800, 540, 400, duration=400)
    time.sleep(2)
    
    from utils_cli import auto_scroller
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    output_filepath = os.path.join(output_dir, "search_results_list.png")
    
    auto_scroller.scroll_and_stitch(
        max_scrolls=scrolls,
        auto_stop=False,  # Usually infinite load, so use fixed scrolls
        output_filepath=output_filepath,
        work_dir=output_dir
    )
    print(f"List saved to {output_filepath}")
    return True
