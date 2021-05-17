import logging

# default formatter
_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s'

# default level
_level = 'DEBUG'

# handlers available
_handlers = {
    'stream' : None,
    'logfile' : None
}

# create logger
logger = logging.getLogger(__package__)
logger.setLevel(_level)

info = logger.info
debug = logger.debug
warning = logger.warning
error = logger.error
critical = logger.critical


def set_level(level):
    logger.setLevel(level.upper() if isinstance(level, str) else level)

def set_stream(level=_level, format=_format):
    # create console handler if not there yet
    level = level.upper()
    assert level in 'DEBUG INFO WARNING ERROR CRITICAL'.split()
    stream = _handlers['stream']
    if not stream:
        stream = logging.StreamHandler()
        _handlers['stream'] = stream
    stream.setLevel(level)
    stream.setFormatter(logging.Formatter(format))
    logger.addHandler(stream)

def set_logfile(filename, level=_level, format=_format):
    # create ile handler and set level to debug
    level = level.upper()
    assert level in 'DEBUG INFO WARNING ERROR CRITICAL'.split()
    logfile = _handlers['logfile']
    if not logfile:
        logfile = logging.FileHandler(filename)
        _handlers['logfile'] = logfile
    logfile.setLevel(level)
    logfile.setFormatter(logging.Formatter(format))
    logger.addHandler(logfile)

def unset_logfile():
    _unset_handler('logfile')

def unset_stream():
    _unset_handler('stream')

def _unset_handler(label):
    hdlr = _handlers[label]
    logger.removeHandler(hdlr)
    _handlers[label] = None
