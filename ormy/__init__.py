import logging

__all__ = [
    "Column",
    "IntegerColumn",
    "FloatColumn",
    "StringColumn",
    "DateColumn"
]

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
log = logging.getLogger(__name__)
print('in __init__ logger = %s' % __name__)
log.setLevel(logging.INFO)
