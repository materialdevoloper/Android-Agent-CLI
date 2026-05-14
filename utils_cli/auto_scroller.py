import os
import sys
import time
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core

def stitch_images(image_paths, output_filepath, direction="vertical", crop_top=120, crop_bottom=120):
    """Stitch a list of images into one big image with smart cropping of system bars."""
    images = [Image.open(p) for p in image_paths]
    if not images:
        return None
        
    processed_images = []
    for i, im in enumerate(images):
        width, height = im.size
        # Smart cropping logic to remove top status bar and bottom nav bar
        # First image: keep top, crop bottom
        # Middle images: crop top and bottom
        # Last image: crop top, keep bottom
        if len(images) > 1:
            if i == 0:
                box = (0, 0, width, height - crop_bottom)
            elif i == len(images) - 1:
                box = (0, crop_top, width, height)
            else:
                box = (0, crop_top, width, height - crop_bottom)
            processed_images.append(im.crop(box))
        else:
            processed_images.append(im)
            
    widths, heights = zip(*(i.size for i in processed_images))
    
    if direction == "vertical":
        total_height = sum(heights)
        max_width = max(widths)
        new_im = Image.new('RGB', (max_width, total_height))
        y_offset = 0
        for im in processed_images:
            new_im.paste(im, (0, y_offset))
            y_offset += im.size[1]
    else: # horizontal
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new('RGB', (total_width, max_height))
        x_offset = 0
        for im in processed_images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    new_im.save(output_filepath)
    print(f"Successfully saved stitched {direction} image to {output_filepath}")
    return output_filepath

def is_same_screen(img_path1, img_path2):
    """Compare two screenshots ignoring the top status bar and bottom nav bar."""
    try:
        im1 = Image.open(img_path1)
        im2 = Image.open(img_path2)
        box = (0, 400, im1.width, int(im1.height * 0.8))
        return im1.crop(box).tobytes() == im2.crop(box).tobytes()
    except Exception:
        return False

def scroll_and_stitch(max_scrolls, auto_stop, output_filepath, work_dir, direction="vertical"):
    """
    Scroll the screen taking screenshots and stitching them smartly.
    Supports 'vertical' or 'horizontal' scrolling.
    """
    print(f"Starting {direction} scroll capture (Auto-detect end: {auto_stop})...")
    image_paths = []
    os.makedirs(work_dir, exist_ok=True)
    
    for i in range(max_scrolls + 1):
        filename = os.path.join(work_dir, f"temp_screen_{i}.png")
        print(f"Capturing screen {i}...")
        adb_core.screencap(filename)
        image_paths.append(filename)

        if auto_stop and i > 0:
            if is_same_screen(image_paths[-2], image_paths[-1]):
                print("End reached! Detected no screen change.")
                image_paths.pop()
                os.remove(filename)
                break

        if i < max_scrolls:
            print("Scrolling...")
            if direction == "vertical":
                # Scroll down (swipe up)
                adb_core.swipe(540, 1800, 540, 400, duration=800)
            else:
                # Scroll right (swipe left)
                adb_core.swipe(900, 1000, 100, 1000, duration=800)
            time.sleep(2) # Wait for UI to render
    
    print("Stitching screenshots with smart cropping...")
    stitch_images(image_paths, output_filepath, direction=direction)
    
    # Clean up
    for p in image_paths:
        try:
            os.remove(p)
        except:
            pass

    return output_filepath
