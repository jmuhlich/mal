from dataclasses import dataclass, field
import re
from typing import List


class UnbalancedParenthesesError(ValueError):
    pass


@dataclass
class Reader:

    tokens: List[str]
    position: int = 0

    def next(self) -> str:
        t = self.peek()
        self.position += 1
        return t

    def peek(self) -> str:
        try:
            return self.tokens[self.position]
        except IndexError:
            raise UnbalancedParenthesesError


def read_str(s):
    r = Reader(tokenize(s))
    return read_form(r)


tokens_pattern = re.compile(
    r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:\\.|[^\\"])*"?|;.*|[^\s\[\]{}('"`,;)]*)"""
)


def tokenize(s) -> List[str]:
    return tokens_pattern.findall(s)


def read_form(r: Reader):
    t = r.peek()
    if t == "(":
        return read_list(r)
    else:
        return read_atom(r)


def read_list(r: Reader):
    r.next()
    l = []
    while r.peek() != ")":
        l.append(read_form(r))
    r.next()
    return l


def read_atom(r: Reader):
    # FIXME actually parse values
    return r.next()
