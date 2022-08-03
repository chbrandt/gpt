from dataclasses import dataclass
from abc import ABC, abstractmethod


class Sources:
    """Data sources container/manager"""
    _sources: dict

    def add(self, name, **kwargs):
        self._sources[name] = Source(name, **kwargs)

    def remove(self, name):
        src = self._sources[name]
        del self._sources[name]

    def list(self):
        return list(self._sources.keys())


class Source(ABC):
    """Define a data-source interface"""
    _name: str
    _data: dict

    def __init__(self, name, **kwargs):
        self._name = name
        self._data = kwargs

    @abstractmethod
    def search(*args, **kwargs) -> ResultSource:
        """Query source for a product or products in a region/bbox"""
        raise NotImplementedError
