from dataclasses import dataclass, field, InitVar
from typing import Optional, List

from mtypes import Node, Symbol


class UnknownSymbolError(RuntimeError):
    pass


@dataclass
class Env:
    outer: Optional["Env"] = None
    data: dict = field(default_factory=dict)
    binds: InitVar[List[Symbol]] = None
    exprs: InitVar[List[Node]] = None

    def __post_init__(self, binds, exprs):
        if binds and exprs:
            for k, v in zip(binds, exprs):
                self.set(k, v)

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
