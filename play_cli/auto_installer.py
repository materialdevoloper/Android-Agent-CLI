import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import adb_core

def install_app(package_id):
    """Open Play Store to the package page and tap Install."""
    print(f"Opening Play Store for package: {package_id}")
    adb_core.run_adb("shell input keyevent 224") # Wake up
    time.sleep(1)
    adb_core.run_adb("shell input swipe 540 2000 540 500") # Unlock
    time.sleep(1)
    
    adb_core.run_adb(f'shell am start -a android.intent.action.VIEW -d "market://details?id={package_id}"')
    
    print("Waiting for Play Store to load...")
    time.sleep(5)
    
    dump_path = "temp_play_dump.xml"
    for _ in range(3):
        adb_core.dump_ui(dump_path)
        bounds = adb_core.find_text_bounds(dump_path, "Install")
        if bounds:
            x = (bounds[0] + bounds[2]) // 2
            y = (bounds[1] + bounds[3]) // 2
            print(f"Found 'Install' button. Tapping at ({x}, {y})")
            adb_core.tap(x, y)
            
            # Wait for install to finish
            print("Installation started. Monitoring progress...")
            return True
        else:
            print("Install button not found. App might be already installed or loading...")
            time.sleep(3)
            
    try:
        os.remove(dump_path)
    except:
        pass
        
    return False
