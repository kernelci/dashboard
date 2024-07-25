import os
import glob
import importlib
import sys


current_dir = os.path.dirname(__file__)
modules = glob.glob(os.path.join(current_dir, "*.py"))

for module in modules:
    module_name = os.path.basename(module)[:-3]
    if module_name != "__init__":
        imported_module = importlib.import_module(f'.{module_name}', package=__name__)

        for attribute_name in dir(imported_module):
            if not attribute_name.startswith('_'):
                setattr(sys.modules[__name__], attribute_name, getattr(imported_module, attribute_name))


del os, glob, importlib, sys, current_dir, modules, module_name, imported_module, attribute_name
