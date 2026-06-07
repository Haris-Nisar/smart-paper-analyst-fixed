import os
import sys

# Ensure project root is on sys.path so local packages can be imported reliably.
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Import the Streamlit application module.
import modules.app as app_module

if __name__ == "__main__":
    app_module.main()
