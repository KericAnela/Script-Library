from pathlib import Path
import subprocess
import platform
import os
import yaml
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def clear_screen():
    if os.name == 'nt':
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

def get_target_directory():
    while True:
        print("Directory Selection:")
        print("1. Scan current folder (and subfolders)")
        print("2. Scan a specific custom path")
        print("3. Scan entire computer (WARNING: Slow/Requires Permissions)")
        
        choice = input("Select an option (1-3): ").strip()

        if choice == '1':
            return Path.cwd()
        
        elif choice == '2':
            custom_path = input("Enter the full path (or 0 to go back): ").strip().strip('"')
            
            if custom_path == '0':
                clear_screen()
                continue 
            
            path_obj = Path(custom_path)
            if path_obj.exists() and path_obj.is_dir():
                clear_screen()
                return path_obj
            else:
                print(f"Error: The path '{custom_path}' does not exist. Please try again.\n")
        
        elif choice == '3':
            clear_screen()
            return Path(os.path.abspath(os.sep))
        
        else:
            clear_screen()
            print("Invalid selection. Please enter 1, 2, or 3.\n")

# Loads configuration rules from config.yaml
def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        return {
            "search": {
                "extensions": [".py"],
                "ignore_folders": ["__pycache__", ".git", "node_modules", "venv", ".venv", "Windows", "proc", "sys", "$Recycle.Bin"],
                "ignore_files": [Path(__file__).name]
            }
        }
    
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}. Using default configuration.")
        return {}

# Worker function to scan an individual subdirectory tree
def _scan_subtree(subtree_path, extensions, ignore_folders, ignore_files, found_files, lock):
    local_files = []
    try:
        for root, dirs, files in os.walk(str(subtree_path), topdown=True):
            dirs[:] = [d for d in dirs if d not in ignore_folders and not d.startswith('.')]

            for file in files:
                if file.endswith(extensions) and file not in ignore_files:
                    local_files.append(Path(root) / file)
                    
                    with lock:
                        found_files.append(local_files[-1])
                        if len(found_files) % 50 == 0:
                            sys.stdout.write(f"\rFound {len(found_files)} scripts so far...")
                            sys.stdout.flush()
    except (PermissionError, OSError):
        pass

# Script search engine
def find_scripts(base_path, config):
    search_cfg = config.get("search", {})
    extensions = tuple(search_cfg.get("extensions", [".py"]))
    ignore_folders = set(search_cfg.get("ignore_folders", []))
    ignore_files = set(search_cfg.get("ignore_files", []))
    
    # Automatically ignore heavy system folders
    if base_path == Path(os.path.abspath(os.sep)):
        if platform.system() == "Windows":
            ignore_folders.update({"Windows", "Program Files", "Program Files (x86)", "$Recycle.Bin", "System Volume Information", "Recovery"})
        else:
            ignore_folders.update({"proc", "sys", "dev", "run", "etc", "Library", "System"})

    found_files = []
    lock = threading.Lock()

    print("Scanning...")

    try:
        # Get top-level contents of base_path
        with os.scandir(base_path) as entries:
            subdirs_to_scan = []
            for entry in entries:
                if entry.name.startswith('.') or entry.name in ignore_folders:
                    continue
                if entry.is_dir(follow_symlinks=False):
                    subdirs_to_scan.append(entry.path)
                elif entry.is_file(follow_symlinks=False):
                    if entry.name.endswith(extensions) and entry.name not in ignore_files:
                        found_files.append(Path(entry.path))

        # Scan subdirectories in parallel
        max_threads = min(32, (os.cpu_count() or 4) * 2)
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [
                executor.submit(_scan_subtree, sub_path, extensions, ignore_folders, ignore_files, found_files, lock)
                for sub_path in subdirs_to_scan
            ]
            for future in as_completed(futures):
                future.result()

        clear_screen()
        print(f"Search complete. Found {len(found_files)} files in total.")
        return found_files

    except PermissionError:
        print("\nPermission denied at root level. Returning partial results.")
        return found_files
    except OSError as e:
        print(f"\nSystem error accessing {base_path}: {e}")
        return found_files

def launch_script(selected_script):
    script_path = str(selected_script.absolute())
    script_dir = str(selected_script.parent)
    current_os = platform.system()

    print(f"Launching: {selected_script.name}...\n")

    if current_os == "Windows":
        subprocess.Popen(f'start cmd /K python "{script_path}"', cwd=script_dir, shell=True)
    elif current_os == "Darwin":
        cmd = f'tell application "Terminal" to do script "python3 \'{script_path}\'"'
        subprocess.Popen(['osascript', '-e', cmd])
    else:
        subprocess.Popen(['x-terminal-emulator', '-e', 'python3', script_path], cwd=script_dir)

def main():
    clear_screen()

    config = load_config()
    base_path = get_target_directory()
    
    if base_path is None:
        return
    
    clear_screen()
    if not base_path.exists() or not base_path.is_dir():
        print(f"Error: '{base_path}' is not a valid directory.")
        return

    script_files = find_scripts(base_path, config)

    if not script_files:
        print(f"\nNo matching scripts found in {base_path}")
        return
    
    for index, file_path in enumerate(script_files, 1):
        print(f"{index:3}. {file_path.name:<30}    inside of {file_path.parent.name}.")
    
    try:
        user_input = input("\nEnter the number to run (or 0 to exit): ")
        if not user_input.strip():
            return
            
        choice = int(user_input)
        
        if 1 <= choice <= len(script_files):
            launch_script(script_files[choice - 1])
        elif choice == 0:
            print("Now exiting...")
        else:
            print("Invalid selection.")
            
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()