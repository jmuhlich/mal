from dataclasses import dataclass, field
from typing import Optional

import mtypes


class UnknownSymbolError(RuntimeError):
    pass


@dataclass
class Env:
    outer: Optional["Env"] = None
    data: dict = field(default_factory=dict)

    def set(self, key: mtypes.Symbol, value: mtypes.Node):
        self.data[key] = value
        return value

    def find(self, key: mtypes.Symbol):
        if key in self.data:
            return self
        elif self.outer:
            return self.outer.find(key)
        else:
            return None

    def get(self, key: mtypes.Symbol):
        env = self.find(key)
        if env:
            return env.data[key]
        else:
            raise UnknownSymbolError(key)
