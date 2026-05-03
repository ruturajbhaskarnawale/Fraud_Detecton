import json
from unittest.mock import MagicMock

class SerializableMock(MagicMock):
    """
    A MagicMock that can be serialized to JSON/B by returning its name or a dict.
    Essential for SQLAlchemy JSONB fields.
    """
    def __json__(self):
        return {"mock": str(self)}
    
    def __str__(self):
        return f"MockObject_{id(self)}"
    
    def __repr__(self):
        return self.__str__()

def to_jsonable(obj):
    import numpy as np
    if isinstance(obj, MagicMock):
        return str(obj)
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_jsonable(x) for x in obj]
    return obj
