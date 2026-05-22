import os
import re

def extract_save_steam_id():
    target_folder = input("Enter the path to the folder containing the .lua files: ").strip()

    # check directory exists
    if not os.path.isdir(target_folder):
        print(f"Error: Directory '{target_folder}' does not exist.")
        return
    
    # FIXED REGEX: Changed (?. to (?: for a valid non-capturing group
    pattern = re.compile(
        r'(?:addappid|setManifestid)\s*\(\s*(\d+)|(?:--\s*AppID\s*(\d+))',
        re.IGNORECASE
    )

    # isolate description inside comments
    comment_pattern = re.compile(r'--\s*(.*)$')

    home_dir = os.path.expanduser("~")
    output_file = os.path.join(home_dir, "extracted_steam_ids.txt")

    global_results = {}

    print(f"\nScanning .lua files in: {target_folder}")
    print("-" * 60)

    for root, dirs, files in os.walk(target_folder):
        for file in files:
            if file.endswith(".lua"):
                file_path = os.path.join(root, file)
                files_ids = {}

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            match = pattern.search(line)
                            if match:
                                steam_id = match.group(1) if match.group(1) else match.group(2)

                                # extract description from comment on the same line
                                comment_match = comment_pattern.search(line)
                                comment_info = ""
                                if comment_match:
                                    comment_text = comment_match.group(1).strip()
                                    # skip generic comments
                                    if "generated on" not in comment_text.lower() and not comment_text.lower().startswith("appid"):
                                        comment_info = comment_text

                                if steam_id not in files_ids or (comment_info and not files_ids[steam_id]):
                                    files_ids[steam_id] = comment_info

                    if files_ids:
                        global_results[file] = files_ids

                except Exception as e:
                    print(f"Could not read file {file}: {e}")

    # write the formatted output to home directory
    if global_results:
        try:
            with open(output_file, 'w', encoding='utf-8') as out:
                out.write("=== EXTRACTED STEAM APP IDS REPORT ===\n\n")
                for file, ids_map in global_results.items():
                    out.write(f"File: {file}\n")
                    out.write("-" * 50 + "\n")
                    # sort id numerically
                    for s_id in sorted(ids_map.keys(), key=int):
                        note = ids_map[s_id]
                        if note:
                            out.write(f"   ID: {s_id}  |  Note: {note}\n")
                        else:
                            out.write(f"   ID: {s_id}\n")
                    out.write("\n")
            
            print("Scan completed successfully!")
            print(f"Results have been saved to: {output_file}")
        
        except Exception as e:
            print(f"Error while saving the output file: {e}")
    else:
        print("No Steam App IDs found matching the criteria in the specified folder.")

if __name__ == "__main__":
    extract_save_steam_id()