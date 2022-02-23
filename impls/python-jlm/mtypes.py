import collections
from dataclasses import dataclass, field

import env


class UnknownSymbolError(RuntimeError):
    pass


@dataclass
class Node:
    pass


@dataclass
class Symbol(Node):
    value: str

    def __str__(self):
        return self.value

    def __hash__(self):
        return hash(self.value)


@dataclass
class Keyword(Node):
    value: str

    def __str__(self):
        return ":" + self.value

    def __hash__(self):
        return hash(self.value)


@dataclass
class Sequence(Node, collections.abc.Sequence):
    values: list

    def __getitem__(self, i):
        return self.values[i]

    def __len__(self):
        return len(self.values)


@dataclass
class List(Sequence):
    pass


@dataclass
class Vector(Sequence):
    pass


@dataclass
class Hashmap(Node, collections.abc.Mapping):
    values: dict

    def __getitem__(self, k):
        return self.values[k]

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)


@dataclass
class Fn(Node):
    ast: Node
    params: Sequence(Symbol)
    env: "env.Env"
    fn: collections.abc.Callable

    def __str__(self):
        return "#<function>"
