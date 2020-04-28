# import importlib
import zipimport
import os.path
import sys
from PySide2 import QtWidgets

HERE = os.path.dirname(os.path.abspath(__file__))
print(f"loading from {HERE}")
sys.path.insert(0, HERE)

# lt1 = importlib.import_module("loadtest1.loadtest")
# print(f"Loaded test 1; dir {dir(lt1)}")
#
# importer = zipimport.zipimporter('loadtest2.zip')
# lt2 = importer.load_module('loadtest')
# print(f"Loaded test 2; dir {dir(lt2)}")

importer = zipimport.zipimporter('loadtest3.modus')
lt3 = importer.load_module('loadtest')
print(f"Loaded test 3; dir {dir(lt3)}")


app = QtWidgets.QApplication()
# lt1 = lt1.DisplayCard("Load 1")
# lt2 = lt2.DisplayCard("Load 2")
lt3 = lt3.DisplayCard("Load 3")

app.exec_()
