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

    # scan-menu command
    scan_parser = subparsers.add_parser("scan-menu", help="Scroll through the menu and stitch screenshots")
    scan_parser.add_argument("--scrolls", type=int, default=2, help="Number of times to scroll down (if not using auto)")
    scan_parser.add_argument("--auto", action="store_true", help="Automatically detect bottom of the list and stop")

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

    elif args.command == "scan-menu":
        menu_scanner.scan_menu(scrolls=args.scrolls, auto=args.auto)
    
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
