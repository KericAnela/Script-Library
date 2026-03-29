from pathlib import Path
import subprocess
import platform
import os
import yaml
import sys

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

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
                print(f"Error: The path '{custom_path}' does not exist. Please try again.")
                clear_screen()
        
        elif choice == '3':
            clear_screen()
            return Path(os.path.abspath(os.sep))
        
        else:
            clear_screen()
            print("Invalid selection. Please enter 1, 2, or 3.")

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        return {
            "search": {
                "extensions": [".py"],
                "ignore_folders": ["__pycache__", ".git"],
                "ignore_files": [Path(__file__).name]
            }
        }
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def find_python_scripts(base_path, config):
    try:
        search_cfg = config.get("search", {})
        extensions = tuple(search_cfg.get("extensions", [".py"]))
        ignore_folders = set(search_cfg.get("ignore_folders", []))
        ignore_files = set(search_cfg.get("ignore_files", []))

        found_files = []
        
        print("Scanning, this may take a moment...")

        for root, dirs, files in os.walk(str(base_path)):
            dirs[:] = [d for d in dirs if d not in ignore_folders and not d.startswith('.')]

            for file in files:
                if file.endswith(extensions) and file not in ignore_files:
                    full_path = Path(root) / file
                    found_files.append(full_path)

                if len(found_files) % 50 == 0:
                    sys.stdout.write(f"\rFound {len(found_files)} scripts so far...")
                    sys.stdout.flush()

        clear_screen()
        
        print(f"Search complete. Found {len(found_files)} files in total.")
        return found_files

    except PermissionError:
        print("Permission denied in some directories.")
        return found_files
    except OSError as e:
        print(f"System error accessing {base_path}: {e}")

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

    python_files = find_python_scripts(base_path, config)

    if not python_files:
        print(f"\nNo Python scripts found in {base_path}")
        return
    
    for index, file_path in enumerate(python_files, 1):
        print(f"{index:3}. {file_path.name:<30} inside of {file_path.parent.name}.")
    
    try:
        user_input = input("\nEnter the number to run (or 0 to exit): ")
        if not user_input.strip():
            return
            
        choice = int(user_input)
        
        if 1 <= choice <= len(python_files):
            launch_script(python_files[choice - 1])
        elif choice == 0:
            print("Now exiting...")
        else:
            print("Invalid selection.")
            
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()