import importlib.util
import os

# Get the current directory of Load.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the modules in Libs
libs_path = os.path.join(current_dir, "..", "Libs")
Design_path = os.path.join(libs_path, "Design.py")
PathLib_path = os.path.join(libs_path, "PathLib.py")

# Load the modules dynamically
Design_spec = importlib.util.spec_from_file_location("Design", Design_path)
Design = importlib.util.module_from_spec(Design_spec)
Design_spec.loader.exec_module(Design)

PathLib_spec = importlib.util.spec_from_file_location("PathLib", PathLib_path)
PathLib = importlib.util.module_from_spec(PathLib_spec)
PathLib_spec.loader.exec_module(PathLib)


