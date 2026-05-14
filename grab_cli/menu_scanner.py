import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core
from utils_cli import auto_scroller

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")

def scan_menu(scrolls=2, auto=False):
    """
    Scroll the Grab menu taking screenshots and stitching them.
    If auto=True, ignores `scrolls` and scrolls until the bottom is reached.
    """
    max_scrolls = 20 if auto else scrolls
    output_filepath = os.path.join(OUTPUT_DIR, "full_menu.png")
    
    auto_scroller.scroll_and_stitch(
        max_scrolls=max_scrolls,
        auto_stop=auto,
        output_filepath=output_filepath,
        work_dir=OUTPUT_DIR
    )

if __name__ == "__main__":
    scan_menu(auto=True)

