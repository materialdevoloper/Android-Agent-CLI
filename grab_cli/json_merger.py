import os
import glob
import json

def merge_json_files(json_dir, output_file):
    """Reads all JSON files in json_dir, merges them, and removes duplicates by name."""
    if not os.path.exists(json_dir):
        print(f"[Error] Directory not found: {json_dir}")
        return False
        
    all_restaurants = []
    seen_names = set()
    
    files = glob.glob(os.path.join(json_dir, "*.json"))
    if not files:
        print(f"No JSON files found in {json_dir}")
        return False
        
    print(f"Found {len(files)} JSON files. Merging...")
    
    for file_path in sorted(files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                print(f"[Warning] Skipping {file_path}: root is not a list")
                continue
                
            for item in data:
                name = item.get("name")
                if not name:
                    continue
                    
                # Normalize name for deduplication
                norm_name = str(name).strip().lower()
                if norm_name not in seen_names:
                    seen_names.add(norm_name)
                    all_restaurants.append(item)
        except Exception as e:
            print(f"[Warning] Failed to process {file_path}: {e}")
            
    print(f"\n[Success] Merged and deduplicated down to {len(all_restaurants)} unique restaurants.")
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"total": len(all_restaurants), "restaurants": all_restaurants}, f, ensure_ascii=False, indent=2)
        
    print(f"Final merged data saved to: {output_file}")
    return all_restaurants

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        merge_json_files(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python json_merger.py <input_dir> <output_file>")
