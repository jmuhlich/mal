import printer
import reader

def READ(x: str) -> str:
    return reader.read_str(x)

def EVAL(x: str) -> str:
    return x

def PRINT(x: str) -> str:
    return printer.pr_str(x)

def rep(x: str) -> str:
    r = READ(x)
    e = EVAL(r)
    p = PRINT(e)
    return p

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
    print(p)
