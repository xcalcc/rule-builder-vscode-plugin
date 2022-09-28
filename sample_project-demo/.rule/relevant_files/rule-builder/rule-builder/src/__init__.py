import sys
import os

path = os.path.realpath(os.path.join(__file__, os.pardir))
if path not in sys.path:
    sys.path.insert(0, path) # including path if not exist
