import os
import sys
import time
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core

def stitch_images(image_paths, output_filepath):
    """Vertically stitch a list of images into one big image."""
    images = [Image.open(p) for p in image_paths]
    
    # Calculate dimensions
    widths, heights = zip(*(i.size for i in images))
    total_height = sum(heights)
    max_width = max(widths)

    new_im = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    for im in images:
        new_im.paste(im, (0, y_offset))
        y_offset += im.size[1]

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    new_im.save(output_filepath)
    print(f"Successfully saved stitched image to {output_filepath}")
    return output_filepath

def is_same_screen(img_path1, img_path2):
    """Compare two screenshots ignoring the top status bar and bottom nav bar."""
    try:
        im1 = Image.open(img_path1)
        im2 = Image.open(img_path2)
        # Crop middle section to ignore dynamic clocks or bottom bars
        # Pixel 7 is 1080x2400. Let's crop X: 0-1080, Y: 400-2000
        box = (0, 400, im1.width, int(im1.height * 0.8))
        return im1.crop(box).tobytes() == im2.crop(box).tobytes()
    except Exception:
        return False

def scroll_and_stitch(max_scrolls, auto_stop, output_filepath, work_dir):
    """
    Scroll the screen taking screenshots and stitching them.
    If auto_stop=True, stops when the bottom is reached.
    """
    print(f"Starting scroll capture (Auto-detect bottom: {auto_stop})...")
    image_paths = []
    os.makedirs(work_dir, exist_ok=True)
    
    for i in range(max_scrolls + 1):
        filename = os.path.join(work_dir, f"temp_screen_{i}.png")
        print(f"Capturing screen {i}...")
        adb_core.screencap(filename)
        image_paths.append(filename)

        # If auto_stop is enabled and it's not the first screen, check if we've hit the bottom
        if auto_stop and i > 0:
            if is_same_screen(image_paths[-2], image_paths[-1]):
                print("Bottom reached! Detected no screen change.")
                # The last image is a duplicate, so we remove it
                image_paths.pop()
                os.remove(filename)
                break

        if i < max_scrolls:
            print("Scrolling down...")
            adb_core.swipe(540, 1800, 540, 400, duration=800)
            time.sleep(2) # Wait for UI to render
    
    print("Stitching screenshots...")
    stitch_images(image_paths, output_filepath)
    
    # Clean up intermediate screenshots
    for p in image_paths:
        try:
            os.remove(p)
        except:
            pass

    return output_filepath
