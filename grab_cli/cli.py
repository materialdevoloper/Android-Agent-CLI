import argparse
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core
import menu_scanner

def main():
    parser = argparse.ArgumentParser(description="Grab-CLI Phone Automation Framework")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # launch command
    launch_parser = subparsers.add_parser("launch", help="Launch the Grab app natively")

    # open-food command
    food_parser = subparsers.add_parser("open-food", help="Launch Grab and enter the Food Delivery page")

    # search command
    search_parser = subparsers.add_parser("search", help="Search for a specific dish or restaurant")
    search_parser.add_argument("--query", type=str, required=True, help="Search query (e.g. Chinese)")
    search_parser.add_argument("--auto-scroll", action="store_true", help="Automatically scroll and stitch results after searching")

    # scan-menu command
    scan_parser = subparsers.add_parser("scan-menu", help="Scroll through the menu and stitch screenshots")
    scan_parser.add_argument("--scrolls", type=int, default=2, help="Number of times to scroll down (if not using auto)")
    scan_parser.add_argument("--auto", action="store_true", help="Automatically detect bottom of the list and stop")

    # extract-vision command
    extract_parser = subparsers.add_parser("extract-vision", help="Extract JSON from an image using local LM Studio")
    extract_parser.add_argument("--image", type=str, required=True, help="Path to the screenshot image")
    extract_parser.add_argument("--output", type=str, required=True, help="Path to save the extracted JSON")

    # merge-json command
    merge_parser = subparsers.add_parser("merge-json", help="Merge multiple JSON files and remove duplicates")
    merge_parser.add_argument("--dir", type=str, required=True, help="Directory containing JSON files")
    merge_parser.add_argument("--output", type=str, required=True, help="Path to save the merged JSON")

    # enter-shop command
    enter_parser = subparsers.add_parser("enter-shop", help="Scroll and find a specific shop to enter")
    enter_parser.add_argument("--name", type=str, required=True, help="Shop name to find and tap")

    # add-to-cart command
    cart_parser = subparsers.add_parser("add-to-cart", help="Smartly find an item, select options, and add to basket")
    cart_parser.add_argument("--item", type=str, required=True, help="Item name to add")
    cart_parser.add_argument("--options", type=str, help="Comma-separated list of options to select (e.g. 'Iced,Less Sweet')")

    # extract-shop-menu command
    extract_menu_parser = subparsers.add_parser("extract-shop-menu", help="Scroll the shop menu and extract all items using local Qwen")

    # tap command
    tap_parser = subparsers.add_parser("tap", help="Tap on a specific coordinate or text")
    tap_parser.add_argument("--x", type=int, help="X coordinate")
    tap_parser.add_argument("--y", type=int, help="Y coordinate")
    tap_parser.add_argument("--text", type=str, help="Text to search and tap on")

    # screencap command
    cap_parser = subparsers.add_parser("screencap", help="Take a single screenshot")
    cap_parser.add_argument("--out", type=str, default="screen.png", help="Output filename")

    args = parser.parse_args()

    if args.command == "launch":
        print("Launching Grab app...")
        adb_core.run_adb("shell monkey -p com.grabtaxi.passenger -c android.intent.category.LAUNCHER 1")
        time.sleep(3)
        print("Grab app launched.")

    elif args.command == "open-food":
        print("[Step 1] Launching Grab app...")
        adb_core.run_adb("shell am force-stop com.grabtaxi.passenger")
        time.sleep(1)
        adb_core.run_adb("shell am start -n com.grabtaxi.passenger/com.grab.pax.newface.common.alias.DefaultLauncherAlias")
        
        print("[Step 1] Waiting for Grab Homepage to load...")
        if not adb_core.wait_for_text(["Food", "Mart", "Transport", "Activity"], timeout=20):
            print("[Error] Failed to load Grab Homepage.")
            sys.exit(1)
            
        print("[Step 1] Grab Homepage loaded. Clicking 'Food'...")
        adb_core.dismiss_popups()
        if not adb_core.click_text("Food"):
            print("[Error] Could not find 'Food' button.")
            sys.exit(1)
            
        print("[Step 1] Waiting for Food Delivery page to load...")
        if not adb_core.wait_for_text(["Search", "Cuisines", "Offers", "Delivering to", "Search for a dish", "What shall we deliver?"], timeout=20):
            print("[Error] Failed to enter Food Delivery page.")
            sys.exit(1)
            
        print("[Success] Entered Food delivery page!")

    elif args.command == "search":
        print(f"[Step 2] Clicking search box...")
        # Try both common placeholders
        if not adb_core.click_text("What shall we deliver?") and not adb_core.click_text("Search for a dish"):
            print("[Error] Could not find search bar on the screen.")
            sys.exit(1)
            
        time.sleep(1) # wait for keyboard/input box to appear
        print(f"[Step 2] Typing query: '{args.query}' and verifying...")
        
        # Robust Input Verification Loop
        input_success = False
        for attempt in range(3):
            adb_core.paste_text(args.query)
            time.sleep(1)
            
            # Dump UI and verify if the exact query text is in the search box
            temp_xml = "temp_verify_input.xml"
            adb_core.dump_ui(temp_xml)
            if adb_core.find_text_bounds(temp_xml, args.query):
                print(f"[Step 2] Input verification passed on attempt {attempt + 1}.")
                input_success = True
                try: os.remove(temp_xml)
                except: pass
                break
            else:
                print(f"[Warning] Input verification failed on attempt {attempt + 1}. Expected: '{args.query}'. Clearing and retrying...")
                # Clear text box with backspaces
                for _ in range(25):
                    adb_core.run_adb("shell input keyevent 67")
                try: os.remove(temp_xml)
                except: pass
                time.sleep(1)
                
        if not input_success:
            print("[Error] Failed to input search query correctly after 3 attempts.")
            sys.exit(1)
            
        adb_core.run_adb("shell input keyevent 66") # Press Enter
        
        print("[Step 2] Waiting for search results to load...")
        # 'Sort' and 'Filter' usually appear on the search results page
        if not adb_core.wait_for_text(["Sort", "Filter", "Delivery fee", args.query], timeout=20):
            print("[Error] Search results did not load.")
            sys.exit(1)
            
        print("[Success] Search results loaded!")
        
        if args.auto_scroll:
            print("[Step 4] --auto-scroll enabled! Triggering scan-menu to extract results...")
            menu_scanner.scan_menu(auto=True)

    elif args.command == "scan-menu":
        menu_scanner.scan_menu(scrolls=args.scrolls, auto=args.auto)
    
    elif args.command == "enter-shop":
        print(f"Entering shop '{args.name}'...")
        if not adb_core.find_and_tap(args.name):
            print("[Error] Could not enter shop.")
            sys.exit(1)
        print(f"[Success] Entered {args.name}!")
        
    elif args.command == "add-to-cart":
        print(f"Finding item '{args.item}'...")
        if not adb_core.find_and_tap(args.item):
            print("[Error] Could not find item on menu.")
            sys.exit(1)
            
        print("[Success] Tapped item. Waiting for options page...")
        import time
        time.sleep(3)
        
        if args.options:
            options = [opt.strip() for opt in args.options.split(",")]
            for opt in options:
                print(f"Selecting option: {opt}...")
                adb_core.dump_ui("temp_options.xml")
                bounds = adb_core.find_text_bounds("temp_options.xml", opt)
                if bounds:
                    adb_core.tap((bounds[0]+bounds[2])//2, (bounds[1]+bounds[3])//2)
                    print(f"Tapped '{opt}'")
                    time.sleep(1)
                else:
                    print(f"[Warning] Option '{opt}' not found on screen.")
                try: os.remove("temp_options.xml")
                except: pass
                
        print("Looking for Add to Basket button...")
        adb_core.dump_ui("temp_add.xml")
        bounds = adb_core.find_text_bounds("temp_add.xml", "Add to Basket")
        if bounds:
            adb_core.tap((bounds[0]+bounds[2])//2, (bounds[1]+bounds[3])//2)
            print("[Success] Added to basket!")
        else:
            print("[Error] Could not find 'Add to Basket' button.")
        try: os.remove("temp_add.xml")
        except: pass
        
    elif args.command == "extract-shop-menu":
        print("Extracting full shop menu using Qwen...")
        import json_extractor
        import qwen_text_extractor
        import os
        
        # Scrape all text nodes by scrolling to the bottom
        all_texts = json_extractor.extract_and_merge(max_scrolls=10, return_texts=True)
        
        # Pass the consolidated text to Qwen
        raw_text = "\n".join(all_texts)
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
        import requests
        payload = {
            "model": "local-model",
            "messages": [{"role": "user", "content": prompt}]
        }
        try:
            print("Sending to local Qwen model...")
            res = requests.post("http://localhost:12345/v1/chat/completions", json=payload)
            output = res.json()['choices'][0]['message']['content'].strip()
            
            if output.startswith("```json"):
                output = output[7:-3]
            elif output.startswith("```"):
                output = output[3:-3]
                
            output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "json", "full_menu.json")
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"[Success] Full menu JSON saved to {output_path}")
        except Exception as e:
            print(f"[Error] Failed to extract JSON: {e}")
            
        return
        import vision_extractor
        vision_extractor.extract_restaurants(args.image, args.output)

    elif args.command == "merge-json":
        import json_merger
        json_merger.merge_json_files(args.dir, args.output)

    elif args.command == "tap":
        if args.x is not None and args.y is not None:
            print(f"Tapping at ({args.x}, {args.y})")
            adb_core.tap(args.x, args.y)
        elif args.text:
            print(f"Searching for text '{args.text}'...")
            adb_core.dump_ui("temp_dump.xml")
            bounds = adb_core.find_text_bounds("temp_dump.xml", args.text)
            if bounds:
                x = (bounds[0] + bounds[2]) // 2
                y = (bounds[1] + bounds[3]) // 2
                print(f"Found '{args.text}' at {bounds}. Tapping ({x}, {y})")
                adb_core.tap(x, y)
            else:
                print(f"Text '{args.text}' not found on screen.")
        else:
            print("Please provide either --x/--y or --text.")

    elif args.command == "screencap":
        adb_core.screencap(args.out)
        print(f"Screenshot saved to {args.out}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
