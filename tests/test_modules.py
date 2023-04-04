import inspect
import sys
from importlib.metadata import version

import autonomous


def test_imports():
    with open("/var/tmp/requirements-freeze.txt") as fptr:
        print(fptr.read())

    submodules = inspect.getmembers(autonomous)
    print("\n====members====\n")
    for name, module in submodules:
        if "builtins" not in name:
            print(name, module)
            
    print("\n====sys.path====\n")
    for p in sys.path:
        print(p)

    print("\n====version====\n")
    version("autonomous")
    print(autonomous.__version__)
