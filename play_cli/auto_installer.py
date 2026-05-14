import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core

def install_app(package_id):
    """Open Play Store to the package page, tap Install, and verify success."""
    print(f"Opening Play Store for package: {package_id}")
    adb_core.run_adb("shell input keyevent 224") # Wake up
    time.sleep(1)
    adb_core.run_adb("shell input swipe 540 2000 540 500") # Unlock
    time.sleep(1)
    
    adb_core.run_adb(f'shell am start -a android.intent.action.VIEW -d "market://details?id={package_id}"')
    
    print("Detecting app state...")
    dump_path = "temp_play_dump.xml"
    action_taken = False
    
    # 1. State Detection (Wait up to 15 seconds for page to load)
    for _ in range(15):
        adb_core.dump_ui(dump_path)
        # If it's already installed, the button says "Open" or "Uninstall"
        if adb_core.find_text_bounds(dump_path, "Open") or adb_core.find_text_bounds(dump_path, "Uninstall"):
            print("[SUCCESS] App is already installed (Detected 'Open' or 'Uninstall').")
            action_taken = True
            break
            
        # If it needs installation, the button says "Install"
        install_bounds = adb_core.find_text_bounds(dump_path, "Install")
        if install_bounds:
            print("Found 'Install' button. Tapping...")
            x = (install_bounds[0] + install_bounds[2]) // 2
            y = (install_bounds[1] + install_bounds[3]) // 2
            adb_core.tap(x, y)
            
            # 2. Final Verification Node (Long Polling for 120s)
            print("Installation started. Verifying final state (Timeout 120s)...")
            if adb_core.wait_for_text("Open", timeout=120):
                print("[SUCCESS] Installation verified! 'Open' button appeared.")
                action_taken = True
                break
            else:
                print("[ERROR] Installation timed out or failed.")
                action_taken = False
                break
                
        time.sleep(1)
            
    try:
        os.remove(dump_path)
    except:
        pass
        
    if not action_taken:
        print("[FAILED] Could not determine state or install button not found.")
        return False
        
    return True
