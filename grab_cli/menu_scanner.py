import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core
from utils_cli import auto_scroller

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

def scan_menu(scrolls=2, auto=False):
    """
    Scroll the Grab menu taking screenshots and stitching them.
    If auto=True, ignores `scrolls` and scrolls until the bottom is reached.
    """
    print("Checking for popups and loading state...")
    
    # 1. Dismiss any popups like "Rate your trip", "GrabUnlimited promo"
    adb_core.dismiss_popups()
    
    # 2. Wait for common menu keywords to ensure the page has loaded
    # Usually merchant pages have 'Menu', 'Delivery', or a cart icon
    print("Waiting for menu to load...")
    # Give it up to 15 seconds to load the page
    if not adb_core.wait_for_text(["Menu", "Delivery", "Basket", "Sort", "Chinese"], timeout=15):
        print("Warning: Menu indicators not found. Page might still be loading or we are on the wrong page.")
        print("Proceeding anyway, but screenshots might be blank.")
    else:
        print("Menu fully loaded!")
        
    # Give it an extra second for images to finish popping in
    time.sleep(1)

    max_scrolls = 20 if auto else scrolls
    output_filepath = os.path.join(OUTPUT_DIR, "full_menu.png")
    
    print(f"Starting scroll and stitch... Output will be saved to {output_filepath}")
    auto_scroller.scroll_and_stitch(
        max_scrolls=max_scrolls,
        auto_stop=auto,
        output_filepath=output_filepath,
        work_dir=OUTPUT_DIR
    )

if __name__ == "__main__":
    scan_menu(auto=True)

