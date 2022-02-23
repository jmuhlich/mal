import collections.abc
import itertools
import re

from mtypes import List, Vector, Hashmap, Sequence


escapes_pat = re.compile('[\\\\"\n]')
escapes_map = {
    "\\": "\\\\",
    '"': '\\"',
    "\n": "\\n",
}


def pr_str(x, print_readably=False) -> str:
    match x:
        case List():
            return "(" + pr_str_sequence(x, print_readably) + ")"
        case Vector():
            return "[" + pr_str_sequence(x, print_readably) + "]"
        case Hashmap():
            return "{" + pr_str_hashmap(x, print_readably) + "}"
        case str():
            if print_readably:
                x = escapes_pat.sub(lambda m: escapes_map[m.group()], x)
                x = '"' + x + '"'
            return x
        case collections.abc.Callable():
            return f"#<function>"
        case None:
            return "nil"
        case True:
            return "true"
        case False:
            return "false"
        case _:
            return str(x)

def pr_str_sequence(x: Sequence, print_readably):
    return " ".join(pr_str(i, print_readably) for i in x)

def pr_str_hashmap(x: Hashmap, print_readably):
    it = itertools.chain.from_iterable(x.values.items())
    return pr_str_sequence(it, print_readably)
