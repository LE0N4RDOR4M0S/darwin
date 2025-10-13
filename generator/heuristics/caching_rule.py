def apply_caching_rule(file_path: str) -> str:
    """
    Injeta anotações simples de cache (simulação).
    Exemplo: adiciona @Cacheable("endpoint") acima de métodos.
    """
    with open(file_path, "r") as f:
        content = f.read()

    if "@Cacheable" not in content:
        modified = content.replace("public", "@Cacheable(\"endpoint\")\npublic")
    else:
        modified = content + "\n// Cache rule reapplied\n"

    return modified
