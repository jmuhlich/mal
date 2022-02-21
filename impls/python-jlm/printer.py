def pr_str(x) -> str:
    if isinstance(x, list):
        return "(" + " ".join(pr_str(i) for i in x) + ")"
    else:
        return str(x)
