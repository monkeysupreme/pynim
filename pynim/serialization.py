import json
import pickle
from typing import Optional


class Serializable:
    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    def to_json(self, indent: Optional[int]) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, j: str):
        return cls.from_dict(json.loads(j))

    def serialize(self):
        return pickle.dumps(self.to_dict())

    @classmethod
    def deserialize(cls, b: bytes):
        return pickle.loads(b)