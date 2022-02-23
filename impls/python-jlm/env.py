from dataclasses import dataclass, field, InitVar
from typing import Optional

from mtypes import Node, Symbol, List


class UnknownSymbolError(RuntimeError):
    pass


@dataclass
class Env:
    outer: Optional["Env"] = None
    data: dict = field(default_factory=dict)
    binds: InitVar[list[Symbol]] = None
    exprs: InitVar[list[Node]] = None

    def __post_init__(self, binds, exprs):
        if binds:
            for i, k in enumerate(binds):
                if k == "&":
                    self.set(binds[i + 1], List(exprs[i:]))
                    break
                else:
                    self.set(k, exprs[i])

    def set(self, key: Symbol, value: Node):
        self.data[key] = value
        return value

    def find(self, key: Symbol):
        if key in self.data:
            return self
        elif self.outer:
            return self.outer.find(key)
        else:
            return None

    def get(self, key: Symbol):
        env = self.find(key)
        if env:
            return env.data[key]
        else:
            raise UnknownSymbolError(key)
