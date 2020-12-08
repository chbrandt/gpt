import logging

# create logger
logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

log = logger.info

# import logging
# logging.basicConfig(format='{levelname}: {message!s}',
#                     style='{',
#                     level=logging.INFO)
# logger = logging.getLogger('gpt')
#
# log = logger.info
# logerr = logger.error
#
# del logger
# del logging
#
