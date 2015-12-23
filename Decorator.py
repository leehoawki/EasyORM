import inspect
import time
import logging
from functools import wraps


def logger(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logging.debug("function   = " + fn.__name__)
        logging.debug("    arguments = {0} {1}".format(args, kwargs))
        ts = time.time()
        result = fn(*args, **kwargs)
        te = time.time()
        logging.debug("    return    = {0}".format(result))
        logging.debug("    time      = %.6f sec" % (te - ts))
        logging.debug("    called_from_line : " + str(inspect.currentframe().f_back.f_lineno))
        return result

    return wrapper


