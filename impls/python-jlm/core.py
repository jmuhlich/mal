import operator

from mtypes import Sequence, List
import printer


def f_prn(*args):
    print(f_pr_str(*args))

def f_pr_str(*args):
    return " ".join(printer.pr_str(x, print_readably=True) for x in args)

def f_str(*args):
    return "".join(printer.pr_str(x) for x in args)

def f_println(*args):
    print(" ".join(printer.pr_str(x) for x in args))

def f_list(*args):
    return List(list(args))

def f_listp(x, *_):
    return isinstance(x, List)

def f_emptyp(x, *_):
    return len(x) == 0

def f_count(x, *_):
    match x:
        case Sequence():
            return len(x)
        case _:
            return 0

def f_eq(x, y, *_):
    match x, y:
        case Sequence(), Sequence():
            return len(x) == len(y) and all(f_eq(xi, yi) for xi, yi in zip(x, y))
        case _:
            return x == y

ns = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv,
    "prn": f_prn,
    "pr-str": f_pr_str,
    "str": f_str,
    "println": f_println,
    "list": f_list,
    "list?": f_listp,
    "empty?": f_emptyp,
    "count": f_count,
    "=": f_eq,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}
