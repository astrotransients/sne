"""Class for representing spectra.
"""
from astrocats.catalog.catdict import CatDict
from astrocats.catalog.key import KEY_TYPES, Key, KeyCollection


class QUANTITY(KeyCollection):
    # Any
    VALUE = Key('value')
    # Numeric
    ERROR = Key('error', KEY_TYPES.NUMERIC)
    PROB = Key('probability', KEY_TYPES.NUMERIC)
    # Booleans
    UPPER_LIMIT = Key('upperlimit', KEY_TYPES.BOOL)
    # Strings
    UNIT = Key('unit', KEY_TYPES.STRING)
    KIND = Key('kind', KEY_TYPES.STRING)
    SOURCE = Key('source', KEY_TYPES.STRING, compare=False)


class Quantity(CatDict):
    """
    """

    _KEYS = QUANTITY

    def __init__(self, parent, **kwargs):
        self.REQ_KEY_TYPES = [
            [QUANTITY.VALUE],
            [QUANTITY.SOURCE]
        ]
        super().__init__(parent, **kwargs)

        parent._clean_quantity(self)