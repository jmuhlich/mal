from dataclasses import dataclass, field
import re
from typing import List

import mtypes


class UnbalancedParenthesesError(RuntimeError):
    pass


class UnbalancedQuoteError(RuntimeError):
    pass


class EmptyExpression(RuntimeError):
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
    tokens = tokenize(s)
    if not tokens:
        raise EmptyExpression
    r = Reader(tokens)
    return read_form(r)


tokens_pat = re.compile(
    # Final + in last group changed from original * to avoid trailing empty token.
    r"""[\s,]*(~@|[\[\]{}()'`~^@]|"(?:\\.|[^\\"])*"?|;.*|[^\s\[\]{}('"`,;)]+)"""
)
unescapes_pat = re.compile(r'\\[\\"n]')
unescapes_map = {
    "\\": "\\",
    '"': '"',
    "n": "\n",
}
macro_map = {
    "'": "quote",
    "`": "quasiquote",
    "~": "unquote",
    "~@": "splice-unquote",
    "@": "deref",
    "^": "with-meta",
}

def tokenize(s) -> List[str]:
    return [t for t in tokens_pat.findall(s) if not t.startswith(";")]


def read_form(r: Reader):
    t = r.peek()
    if t == "(":
        return read_list(r)
    elif t == "[":
        return read_vector(r)
    elif t == "{":
        return read_hashmap(r)
    elif m := macro_map.get(t, None):
        return read_macro(r, m)
    else:
        return read_atom(r)


def read_sequence(r: Reader, end_tok: str):
    r.next()
    v = []
    while r.peek() != end_tok:
        v.append(read_form(r))
    r.next()
    return v


def read_list(r: Reader):
    v = read_sequence(r, ")")
    return mtypes.List(v)


def read_vector(r: Reader):
    v = read_sequence(r, "]")
    return mtypes.Vector(v)


def read_hashmap(r: Reader):
    v = read_sequence(r, "}")
    m = dict(zip(v[::2], v[1::2]))
    return mtypes.Hashmap(m)


def read_atom(r: Reader):
    t = r.next()
    if t == "":
        return ""
    elif t[0] == '"':
        if len(t) < 2 or t[-1] != '"':
            raise UnbalancedQuoteError
        t = t[1:-1]
        if m := re.search(r"\\*$", t):
            a, b = m.span()
            if (b - a) % 2 == 1:
                raise UnbalancedQuoteError
        t = unescapes_pat.sub(lambda m: unescapes_map[m.group()[1]], t)
        return t
    elif re.match(r":.", t):
        return mtypes.Keyword(t[1:])
    elif re.match(r"-?\d+$", t):
        return int(t)
    elif t == "nil":
        return None
    elif t == "true":
        return True
    elif t == "false":
        return False
    else:
        return mtypes.Symbol(t)


def read_macro(r: Reader, symbol: str):
    r.next()
    if symbol == "with-meta":
        meta = read_form(r)
        form = read_form(r)
        l = [form, meta]
    else:
        l = [read_form(r)]
    return mtypes.List([mtypes.Symbol(symbol)] + l)
