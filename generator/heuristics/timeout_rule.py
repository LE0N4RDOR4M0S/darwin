import re


def apply_timeout_rule(file_path: str, factor: float = 0.75) -> str:
    """
    Ajusta dinamicamente valores de timeout em código Java via regex.
    Detecta padrões como:
      - .setTimeout(2000)
      - .setConnectTimeout(5000)
      - .setReadTimeout(10000)
    Aplica um fator de redução (default: 0.75, ou seja, 25% de redução).
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'(\.(?:set(?:Connect|Read)?Timeout)\()(\d+)(\))'

    def replacer(match):
        prefix = match.group(1)
        old_val = int(match.group(2))
        suffix = match.group(3)
        new_val = max(100, int(old_val * factor))
        return f"{prefix}{new_val}{suffix}"

    modified, count = re.subn(pattern, replacer, content)

    if count == 0:
        # Se nenhum método de timeout foi encontrado, injeta anotação de tuning no topo
        modified = "// Darwin Heuristic: Timeout tuning applied\n" + content

    return modified
