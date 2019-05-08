"""this only exists so i don't have to dick with atom-python-run settings.

It executes-via-import the main function, unless one of the prototype
modules was updated more recently. Call this in atom-python-run"""

import os
import importlib

print("executing files from: " + os.getcwd())

files = os.listdir()

default = "sylladex.py"
new = default
for file in files:
    if os.path.getmtime(file) > os.path.getmtime(new):
        if "proto" in file:
            new = file
        else:
            new = default

importlib.import_module(new.split('.')[0])

# TODO: add support for test modules also
