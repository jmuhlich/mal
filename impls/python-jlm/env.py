from dataclasses import dataclass, field, InitVar
from typing import Optional

import mtypes


@dataclass
class Env:
    outer: Optional["Env"] = None
    data: dict = field(default_factory=dict)
    binds: InitVar[list["mtypes.Symbol"]] = None
    exprs: InitVar[list["mtypes.Node"]] = None

    def __post_init__(self, binds, exprs):
        if binds:
            for i, k in enumerate(binds):
                match k:
                    case mtypes.Symbol("&"):
                        self.set(binds[i + 1], mtypes.List(exprs[i:]))
                        break
                    case _:
                        self.set(k, exprs[i])

    def set(self, key: "mtypes.Symbol", value: "mtypes.Node"):
        self.data[key] = value
        return value

    def find(self, key: "mtypes.Symbol"):
        if key in self.data:
            return self
        elif self.outer:
            return self.outer.find(key)
        else:
            return None

    def get(self, key: "mtypes.Symbol"):
        env = self.find(key)
        if env:
            return env.data[key]
        else:
            raise mtypes.UnknownSymbolError(key)
