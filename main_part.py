from pathlib import Path
import subprocess
import platform
import os
import yaml

def get_target_directory():
    print("1. Scan current folder (and subfolders)")
    print("2. Scan a specific custom path")
    print("3. Scan entire computer (WARNING: Slow/Requires Permissions)")
    
    choice = input("Select an option (1-3): ")

    if choice == '1':
        return Path.cwd()
    elif choice == '2':
        custom_path = input("Enter the full path: ").strip().strip('"')
        return Path(custom_path)
    elif choice == '3':
        return Path(os.path.abspath(os.sep))
    
    print("Invalid choice, defaulting to current folder.")
    return Path.cwd()

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
    search_cfg = config.get("search", {})
    extensions = set(search_cfg.get("extensions", [".py"]))
    ignore_folders = set(search_cfg.get("ignore_folders", []))
    ignore_files = set(search_cfg.get("ignore_files", []))

    found_files = []
    
    try:
        for path in base_path.rglob("*"):
            if not path.is_file():
                continue
            
            if any(folder in path.parts for folder in ignore_folders):
                continue
                
            if path.suffix.lower() in extensions and path.name not in ignore_files:
                found_files.append(path)
                
        return found_files

    except PermissionError:
        print("Permission denied in some directories.")
        return found_files

def launch_script(selected_script):
    script_path = str(selected_script.absolute())
    script_dir = str(selected_script.parent)
    current_os = platform.system()

    print(f"Launching: {selected_script.name}...\n")

    if current_os == "Windows":
        subprocess.Popen(['start', 'cmd', '/K', 'python', script_path], 
                         cwd=script_dir, shell=True)
    elif current_os == "Darwin":  # macOS
        cmd = f'tell application "Terminal" to do script "python3 \'{script_path}\'"'
        subprocess.Popen(['osascript', '-e', cmd])
    else:  # Linux
        subprocess.Popen(['x-terminal-emulator', '-e', 'python3', script_path], 
                         cwd=script_dir)

def main():
    config = load_config()
    base_path = get_target_directory()
    
    if not base_path.exists() or not base_path.is_dir():
        print(f"Error: '{base_path}' is not a valid directory.")
        return

    python_files = find_python_scripts(base_path, config)

    if not python_files:
        print("No Python scripts found.")
        return

    for index, file_path in enumerate(python_files, 1):
        print(f"{index}. {file_path.name} (in {file_path.parent.name})")

    try:
        user_input = input("\nEnter the number to run (0 to exit): ")
        choice = int(user_input)
        
        if 1 <= choice <= len(python_files):
            launch_script(python_files[choice - 1])
        elif choice == 0:
            print("Exiting.")
        else:
            print("Invalid selection.")
            
    except ValueError:
        print("Please enter a valid number.")

if __name__ == "__main__":
    main()