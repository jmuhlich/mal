def READ(x: str) -> str:
    return x

def EVAL(x: str) -> str:
    return x

def PRINT(x: str) -> str:
    return x

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
    p = rep(x)
    print(p)
