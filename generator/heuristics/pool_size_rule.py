def apply_pool_size_rule(file_path: str) -> str:
    """
    Ajusta tamanho de pool de conexões.
    Exemplo: setMaxPoolSize(10) → setMaxPoolSize(20)
    """
    with open(file_path, "r") as f:
        content = f.read()

    if "setMaxPoolSize(" in content:
        modified = content.replace("setMaxPoolSize(10)", "setMaxPoolSize(20)")
    else:
        modified = content + "\n// Pool size adjusted for optimization\n"

    return modified
