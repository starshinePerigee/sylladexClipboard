"""this only exists so i don't have to dick with atom-python-run settings"""

import os
import importlib

print("executing files from: " + os.getcwd())

files = os.listdir()

new = "sylladex.py"
for file in files:
    if os.path.getmtime(file) > os.path.getmtime(new) and \
    "proto" in file:
        new = file

importlib.import_module(new.split('.')[0])
