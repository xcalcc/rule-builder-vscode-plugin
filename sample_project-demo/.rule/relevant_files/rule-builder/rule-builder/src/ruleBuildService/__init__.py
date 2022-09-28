import os
import sys

commondef_path = os.path.realpath(
    os.path.join(
        __file__, os.pardir, 'commondef/src/'
    )
)
if commondef_path not in sys.path:
    sys.path.insert(0, commondef_path) # usage becomes common.<COMPONENT>

print(sys.path)

from ruleBuildService.LoggingHandler import initialize_logging_util
initialize_logging_util()

rb_loc = os.path.realpath( # path to ruleBuildService directory
    os.path.join(
        __file__, os.pardir
    )
)

res_path = os.path.join( # path to resources (static)
    rb_loc, 'resources'
)

template_h_path = os.path.join(
    res_path, 'template.h'
)
