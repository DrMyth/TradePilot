import importlib.util
import os
import sys

base_path = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, base_path)

def import_files(folder):
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith("__")]
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                rel_path = os.path.relpath(os.path.join(root, file), base_path)
                module_path = rel_path.replace(os.path.sep, ".").replace(".py", "")
                try:
                    importlib.import_module(module_path)
                except Exception as e:
                    print(f"Failed to import {module_path}: {e}")

import_files(base_path)
