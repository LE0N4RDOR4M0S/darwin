def apply_timeout_rule(file_path: str) -> str:
    """
    Aumenta ou reduz timeouts de requisições em código Java.
    Exemplo: .setTimeout(2000) → .setTimeout(1500)
    """
    with open(file_path, "r") as f:
        content = f.read()

    if ".setTimeout(" in content:
        modified = content.replace(".setTimeout(2000)", ".setTimeout(1500)")
    else:
        modified = content + "\n// Added timeout tuning\n"

    return modified
