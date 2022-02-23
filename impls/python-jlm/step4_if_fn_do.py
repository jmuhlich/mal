from typing import Optional

import core
import env
from mtypes import Node, Symbol, Sequence, List, Vector, Hashmap
import printer
import reader


class UnknownSymbolError(RuntimeError):
    pass

class InvalidSyntaxError(RuntimeError):
    pass


def READ(x: str) -> Node:
    return reader.read_str(x)


def EVAL(x: Node, e: env.Env) -> Node:
    match x:
        case List([]):
            return x
        case List([Symbol("def!"), Symbol(key), expr]):
            return e.set(key, EVAL(expr, e))
        case List([Symbol("def!"), *_]):
            raise InvalidSyntaxError("def! takes a symbol and an expression")
        case List([Symbol("let*"), Sequence(binds), expr]):
            if len(binds) % 2:
                raise InvalidSyntaxError("let* bindings must be matched pairs")
            e = env.Env(e)
            for bsym, bexpr in zip(binds[::2], binds[1::2]):
                match bsym:
                    case Symbol(key):
                        e.set(bsym.value, EVAL(bexpr, e))
                    case _:
                        raise InvalidSyntaxError("let* can only bind to a symbol")
            return EVAL(expr, e)
        case List([Symbol("let*"), *_]):
            raise InvalidSyntaxError("let* takes a binding list and an expression")
        case List([Symbol("do"), *nodes]):
            for node in nodes:
                ret = EVAL(node, e)
            return ret
        case List([Symbol("if"), cond, b_true, b_false]):
            return eval_if(cond, b_true, b_false, e)
        case List([Symbol("if"), cond, b_true]):
            return eval_if(cond, b_true, None, e)
        case List([Symbol("if"), *_]):
            raise InvalidSyntaxError(
                "if takes a condition and 1 or 2 branch expressions"
            )
        case List([Symbol("fn*"), Sequence(names), body]):
            def fn(*args):
                e_inner = env.Env(e, binds=[n.value for n in names], exprs=args)
                return EVAL(body, e_inner)
            return fn
        case List():
            # Apply
            func, *args = eval_ast(x, e)
            return func(*args)
        case _:
            return eval_ast(x, e)


def PRINT(x: Node) -> str:
    return printer.pr_str(x, print_readably=True)


def eval_ast(node: Node, e: env.Env):
    match node:
        case Symbol(value):
            return e.get(value)
        case List(values):
            return List([EVAL(v, e) for v in values])
        case Vector(values):
            return Vector([EVAL(v, e) for v in values])
        case Hashmap(values):
            return Hashmap({k: EVAL(v, e) for k, v in values.items()})
        case _:
            return node


def eval_if(cond: Node, b_true: Node, b_false: Node, e: env.Env):
    result = EVAL(cond, e)
    if result is None or result is False:
        return EVAL(b_false, e)
    else:
        return EVAL(b_true, e)

def rep(x: str) -> str:
    r = READ(x)
    e = EVAL(r, repl_env)
    p = PRINT(e)
    return p


repl_env = env.Env()
for k, v in core.ns.items():
    repl_env.set(k, v)

rep("(def! not (fn* (a) (if a false true)))")

while True:
    try:
        x = input("user> ")
    except EOFError:
        break
    try:
        p = rep(x)
    except reader.UnbalancedParenthesesError:
        print("unbalanced parentheses")
        continue
    except reader.UnbalancedQuoteError:
        print("unbalanced quotes")
        continue
    except env.UnknownSymbolError as e:
        print(f"'{e}' not found")
        continue
    except InvalidSyntaxError as e:
        print(f"syntax error: {e}")
        continue
    except reader.EmptyExpression:
        continue
    print(p)
