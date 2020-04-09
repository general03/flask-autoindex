"""
.. list-table::
   :widths: 1 99

"""
import os
import re

for filename in sorted(os.listdir(os.path.dirname(__file__))):
    if not filename.endswith(".png"):
        continue
    __doc__ += "   * - .. image:: _static/{0}\n" \
               "     - {0}\n".format(filename)

