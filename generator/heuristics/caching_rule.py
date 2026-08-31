import re


def apply_caching_rule(file_path: str) -> str:
    """
    Injeta anotação Spring @Cacheable em métodos de leitura (get/find/search/load/fetch)
    que ainda não possuem anotação de cache.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "@Cacheable" in content:
        return content + "\n// Darwin Heuristic: Caching already present\n"

    # Procurar método de leitura: public <Type> get/find/search/load/fetch...
    pattern = r'(\n\s*)(public\s+[\w<>,\[\]\s]+\s+(?:get|find|search|load|fetch)\w*\s*\()'

    def replacer(match):
        indent_and_newline = match.group(1)
        method_signature = match.group(2)
        return f'{indent_and_newline}@org.springframework.cache.annotation.Cacheable("darwin-cache"){indent_and_newline}{method_signature}'

    modified, count = re.subn(pattern, replacer, content)

    if count == 0:
        # Se nenhum método específico de leitura foi encontrado, insere no primeiro public method
        modified, count = re.subn(r'(\n\s*)(public\s+)', r'\1@org.springframework.cache.annotation.Cacheable("darwin-cache")\1public ', content, count=1)

    if count == 0:
        modified = "// Darwin Heuristic: Caching rule evaluated\n" + content

    return modified
