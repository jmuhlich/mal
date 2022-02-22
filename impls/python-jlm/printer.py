import itertools
import re

import mtypes


escapes_pat = re.compile('[\\\\"\n]')
escapes_map = {
    "\\": "\\\\",
    '"': '\\"',
    "\n": "\\n",
}


def pr_str(x, print_readably=False) -> str:
    if isinstance(x, mtypes.List):
        return "(" + pr_str_sequence(x, print_readably) + ")"
    elif isinstance(x, mtypes.Vector):
        return "[" + pr_str_sequence(x, print_readably) + "]"
    elif isinstance(x, mtypes.Hashmap):
        return "{" + pr_str_hashmap(x, print_readably) + "}"
    elif isinstance(x, str):
        if print_readably:
            x = escapes_pat.sub(lambda m: escapes_map[m.group()], x)
        return '"' + x + '"'
    else:
        return str(x)

def pr_str_sequence(x: mtypes.Sequence, print_readably):
    return " ".join(pr_str(i, print_readably) for i in x)

def pr_str_hashmap(x: mtypes.Hashmap, print_readably):
    it = itertools.chain.from_iterable(x.values.items())
    return pr_str_sequence(it, print_readably)
