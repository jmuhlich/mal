import collections.abc
import sys
from typing import Optional

import core
from env import Env
from mtypes import (
    Node,
    Symbol,
    Sequence,
    List,
    Vector,
    Hashmap,
    Fn,
    UnknownSymbolError,
    InvalidSyntaxError,
    InvalidTypeError,
)
import printer
import reader


def READ(x: str) -> Node:
    return reader.read_str(x)


def EVAL(ast: Node, env: Env) -> Node:
    while True:
        match ast:
            case List([]):
                return ast
            case List([Symbol("def!"), Symbol() as key, expr]):
                return env.set(key, EVAL(expr, env))
            case List([Symbol("def!"), *_]):
                raise InvalidSyntaxError("def! takes a symbol and an expression")
            case List([Symbol("let*"), Sequence(binds), expr]):
                if len(binds) % 2:
                    raise InvalidSyntaxError("let* bindings must be matched pairs")
                ast = expr
                env = Env(env)
                for bsym, bexpr in zip(binds[::2], binds[1::2]):
                    match bsym:
                        case Symbol():
                            env.set(bsym, EVAL(bexpr, env))
                        case _:
                            raise InvalidSyntaxError(
                                "let* can only bind to a symbol"
                            )
            case List([Symbol("let*"), *_]):
                raise InvalidSyntaxError(
                    "let* takes a binding list and an expression"
                )
            case List([Symbol("do"), *nodes]):
                for node in nodes[:-1]:
                    EVAL(node, env)
                ast = nodes[-1]
            case List([Symbol("if"), cond, b_true, b_false]):
                ast = eval_if(cond, b_true, b_false, env)
            case List([Symbol("if"), cond, b_true]):
                ast = eval_if(cond, b_true, None, env)
            case List([Symbol("if"), *_]):
                raise InvalidSyntaxError(
                    "if takes a condition and 1 or 2 branch expressions"
                )
            case List([Symbol("fn*"), Sequence() as params, body]):
                def fn(*args):
                    env_inner = Env(env, binds=params, exprs=args)
                    return EVAL(body, env_inner)
                return Fn(ast=body, params=params, env=env, fn=fn)
            case List():
                # Apply
                f, *args = eval_ast(ast, env)
                match f:
                    case collections.abc.Callable():
                        return f(*args)
                    case Fn():
                        ast = f.ast
                        env = Env(f.env, binds=f.params, exprs=args)
                    case _:
                        raise InvalidTypeError(
                            "attempted to call a non-function"
                        )
            case _:
                return eval_ast(ast, env)


def PRINT(ast: Node) -> str:
    return printer.pr_str(ast, print_readably=True)


def eval_ast(node: Node, env: Env):
    match node:
        case Symbol():
            return env.get(node)
        case List(values):
            return List([EVAL(v, env) for v in values])
        case Vector(values):
            return Vector([EVAL(v, env) for v in values])
        case Hashmap(values):
            return Hashmap({k: EVAL(v, env) for k, v in values.items()})
        case _:
            return node


def eval_if(cond: Node, b_true: Node, b_false: Node, env: Env):
    result = EVAL(cond, env)
    if result is None or result is False:
        return b_false
    else:
        return b_true

def rep(x: str) -> str:
    r = READ(x)
    e = EVAL(r, repl_env)
    p = PRINT(e)
    return p


repl_env = Env()
for k, v in core.ns.items():
    repl_env.set(Symbol(k), v)

repl_env.set(Symbol("eval"), lambda ast: EVAL(ast, repl_env))

rep(r'(def! not (fn* (a) (if a false true)))')
rep(r'(def! load-file (fn* (f) (eval (read-string (str "(do " (slurp f) "\nnil)")))))')

if len(sys.argv) > 1:
    _, script_path, *argv = sys.argv
    repl_env.set(Symbol("*ARGV*"), List(argv))
    path_val = printer.pr_str(script_path, print_readably=True)
    rep(f'(load-file {path_val})')
    sys.exit(0)
else:
    repl_env.set(Symbol("*ARGV*"), List([]))


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
    except UnknownSymbolError as e:
        print(f"'{e}' not found")
        continue
    except InvalidSyntaxError as e:
        print(f"syntax error: {e}")
        continue
    except InvalidTypeError as e:
        print(f"type error: {e}")
        continue
    except reader.EmptyExpression:
        continue
    print(p)
