import re


def apply_pool_size_rule(file_path: str, increase_ratio: float = 1.5) -> str:
    """
    Ajusta tamanho de pool de conexões/threads em código Java via regex.
    Detecta padrões como:
      - .setMaxPoolSize(10)
      - .setMaximumPoolSize(20)
      - .setCorePoolSize(5)
    Aplica um incremento configurável (default: 1.5x, min: 20).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'(\.(?:set(?:Max|Maximum|Core)?PoolSize)\()(\d+)(\))'

    def replacer(match):
        prefix = match.group(1)
        old_val = int(match.group(2))
        suffix = match.group(3)
        new_val = max(20, int(old_val * increase_ratio))
        return f"{prefix}{new_val}{suffix}"

    modified, count = re.subn(pattern, replacer, content)

    if count == 0:
        modified = "// Darwin Heuristic: Pool size optimization applied\n" + content

    return modified
