# Script-Library

A lightweight Python utility designed to discover and launch local Python scripts interactively. It features cross-platform terminal spawning and a customizable search scope controlled via a YAML configuration file.

## Features

- **Interactive Script Discovery:** Scan your current working directory, a custom path, or your entire computer for Python scripts.
- **Cross-Platform Launcher:** Automatically opens and executes selected scripts in a new terminal window (supports Windows Command Prompt, macOS Terminal, and Linux emulators).
- **Configurable Scope:** Easily manage file extensions, ignore folders (like `.git` or `__pycache__`), and exclusions via `config.yaml`.

## Getting Started

### Prerequisites
- Python 3.x
- PyYAML (`pip install pyyaml`)

### Usage
```bash
# Clone the repository
git clone https://github.com/KericAnela/Script-Library.git
cd Script-Library

# Install dependencies
pip install pyyaml

# Run the utility
python main.py
