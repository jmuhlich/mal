import printer
import reader
import mtypes


class UnknownSymbolError(RuntimeError):
    pass


def READ(x: str) -> mtypes.Node:
    return reader.read_str(x)


def EVAL(x: mtypes.Node, env: dict) -> mtypes.Node:
    match x:
        case mtypes.List() if len(x) == 0:
            return x
        case mtypes.List(values):
            func, *args = eval_ast(x, env)
            return func(*args)
        case _:
            return eval_ast(x, env)


def PRINT(x: mtypes.Node) -> str:
    return printer.pr_str(x, print_readably=True)


def eval_ast(node: mtypes.Node, env: dict):
    match node:
        case mtypes.Symbol(value):
            try:
                return env[value]
            except KeyError:
                raise UnknownSymbolError(value) from None
        case mtypes.List(values):
            return mtypes.List([EVAL(v, env) for v in values])
        case mtypes.Vector(values):
            return mtypes.Vector([EVAL(v, env) for v in values])
        case mtypes.Hashmap(values):
            return mtypes.Hashmap({k: EVAL(v, env) for k, v in values.items()})
        case _:
            return node


def rep(x: str) -> str:
    r = READ(x)
    e = EVAL(r, repl_env)
    p = PRINT(e)
    return p


repl_env = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a // b,
}


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
        print(f"unknown symbol: {e}")
        continue
    except reader.EmptyExpression:
        continue
    print(p)
