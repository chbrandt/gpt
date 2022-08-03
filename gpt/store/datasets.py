from dataclasses import dataclass

from gpt import store

@dataclass
class Dataset:
    """Handler for dataset labeling and source/data provider"""
    _target: str
    _instrument: str
    _instrument_type: str
    _product_type: str
    _source: str

    def __str__(self):
        return '{:s}/{:s}/{:s}/{:s}'.format(
            self._target,
            self._instrument,
            self._instrument_type,
            self._product_type
        )

    def name(self):
        return str(self)

    def source(self):
        return store.Source(self._source)
