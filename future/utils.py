import logging



def decode_header(headers: list[tuple[bytes]]):
    """Decode request headers"""
    return [(key.decode("utf-8"), value.decode("utf-8")) for key, value in headers]


def get_level_names_mapping():
    level_names = {
        logging.CRITICAL: 'CRITICAL',
        logging.ERROR: 'ERROR',
        logging.WARNING: 'WARNING',
        logging.INFO: 'INFO',
        logging.DEBUG: 'DEBUG',
        logging.NOTSET: 'NOTSET',
    }
    return level_names

#level_names_mapping = get_level_names_mapping()
#print(level_names_mapping)

