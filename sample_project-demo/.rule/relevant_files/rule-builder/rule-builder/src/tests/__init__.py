import os
from ruleBuildService.logger import Logger

logger = Logger.get_log(test_mode=True)
rb_loc = os.path.realpath(
    os.path.join(
        __file__, os.pardir, os.pardir, 'ruleBuildService'
    )
)

test_dir = os.path.realpath(
    os.path.join(
        __file__, os.pardir, os.pardir, os.pardir, os.pardir, 'test'
    )
)
