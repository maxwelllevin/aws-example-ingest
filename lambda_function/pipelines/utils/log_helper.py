import traceback

import json
import logging
import sys

logger = logging.getLogger()


def log_exception(error_message=''):
    exception_type, exception_value, exception_traceback = sys.exc_info()
    traceback_string = traceback.format_exception(exception_type, exception_value, exception_traceback)
    err_msg = json.dumps({
        "Error_Message": error_message,
        "Error_Type": exception_type.__name__,
        "Exception_Message": str(exception_value),
        "Stack_Trace": traceback_string
    })
    logger.error(err_msg)
