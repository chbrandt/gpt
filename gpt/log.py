import logging
logging.basicConfig(format='{levelname}: {message!s}',
                    style='{',
                    level=logging.INFO)
logger = logging.getLogger()

log = logger.info
logerr = logger.error

del logger
del logging
