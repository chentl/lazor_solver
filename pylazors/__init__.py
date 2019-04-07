import sys

if sys.version_info[0] < 3 or sys.version_info[1] < 6:
    raise Exception('Must be using at least Python 3.6')
