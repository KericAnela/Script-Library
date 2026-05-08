import os
import pytest
from src.scanner import scan_directory

def test_scanner_ignores_init_and_finds_scripts(tmp_path):
    test_dir = tmp_path / "my_scripts"
    test_dir.mkdir()
    
    valid_script = test_dir / "hi hi.py"
    valid_script.write_text("print('hey :)')")
    
    init_file = test_dir / "__init__.py"
    init_file.write_text("# This is a package file, not a runnable script")

    found_scripts = scan_directory(str(test_dir))

    assert len(found_scripts) == 1, f"Expected 1 script, but found: {found_scripts}"
    
    assert "hi hi.py" in found_scripts[0]
    
    for script_path in found_scripts:
        assert "__init__.py" not in script_path, "Scanner should have ignored __init__.py"