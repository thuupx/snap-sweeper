import logging
import os
import sys
import types


def global_exception_handler(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: types.TracebackType,
):

    logging.error(
        f"[{os.getpid()}] EXCEPTION: {exc_type.__name__}: {exc_value}",
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    sys.__excepthook__(exc_type, exc_value, exc_traceback)
