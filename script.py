import os
import re
import sys

try:
    import yaml
except ImportError:
    print("Erreur : PyYAML n'est pas installé.")
    print("Installe-le avec : pip install pyyaml")
    sys.exit(1)


BLOCK_START_RE = re.compile(r"#([A-Za-z0-9_.-]+)#BEGIN")
INCLUDE_RE = re.compile(r"^([ \t]*)!INCLUDE\s+([A-Za-z0-9_.-]+)[ \t]*$", re.MULTILINE)


def load_config(config_path="config.yaml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Fichier de config introuvable : {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError("Le fichier config.yaml est vide ou invalide.")

    languages = config.get("languages", {})
    sources = config.get("sources", [])
    docs = config.get("docs", [])

    if not languages or not isinstance(languages, dict):
        raise ValueError("config.yaml doit contenir 'languages' sous forme de mapping.")

    if not sources or not isinstance(sources, list):
        raise ValueError("config.yaml doit contenir 'sources' sous forme de liste.")

    if not docs or not isinstance(docs, list):
        raise ValueError("config.yaml doit contenir 'docs' sous forme de liste.")

    for entry in docs:
        if not isinstance(entry, dict) or "input" not in entry or "output" not in entry:
            raise ValueError("Chaque entrée 'docs' doit contenir 'input' et 'output'.")

    return languages, sources, docs


def collect_source_files(source_dirs, allowed_extensions):
    files_found = []

    for source_dir in source_dirs:
        if not os.path.exists(source_dir):
            print(f"[WARN] Dossier source introuvable : {source_dir}")
            continue

        for root, _, files in os.walk(source_dir):
            for file_name in files:
                ext = os.path.splitext(file_name)[1]
                if ext in allowed_extensions:
                    files_found.append(os.path.join(root, file_name))

    return files_found


def extract_blocks_from_file(file_path, lang):
    with open(file_path, "r", encoding="utf-8", newline="\n") as f:
        content = f.read().replace("\r\n", "\n").replace("\r", "\n")
    lines = content.splitlines(keepends=True)

    blocks = {}
    i = 0

    while i < len(lines):
        line = lines[i]
        start_match = BLOCK_START_RE.search(line)

        if not start_match:
            i += 1
            continue

        block_id = start_match.group(1)
        end_token = f"#{block_id}#END"

        code_lines = []
        i += 1

        while i < len(lines):
            if end_token in lines[i]:
                break
            code_lines.append(lines[i])
            i += 1

        if i >= len(lines):
            print(f"[WARN] Bloc '{block_id}' sans fin trouvée dans {file_path}")
            break

        code_content = "".join(code_lines)

        # Supprime les lignes vides répétées
        code_content = re.sub(r"\n\s*\n+", "\n", code_content).strip()

        if block_id not in blocks:
            blocks[block_id] = {
                "content": code_content,
                "lang": lang,
                "file": file_path,
            }

        i += 1

    return blocks


def scan_all_blocks(source_files, lang_map):
    all_blocks = {}

    for file_path in source_files:
        ext = os.path.splitext(file_path)[1]
        lang = lang_map.get(ext, "")

        file_blocks = extract_blocks_from_file(file_path, lang)

        for block_id, block_data in file_blocks.items():
            if block_id not in all_blocks:
                all_blocks[block_id] = block_data
            else:
                print(
                    f"[WARN] Doublon ignoré pour '{block_id}' dans {file_path} "
                    f"(premier conservé : {all_blocks[block_id]['file']})"
                )

    return all_blocks


def replace_includes_in_markdown(md_content, blocks, include_filename=False):
    def replacer(match):
        indent = match.group(1)
        block_id = match.group(2)

        if block_id not in blocks:
            return f"{indent}<!-- Missing block: {block_id} -->"

        block = blocks[block_id]
        lang = block["lang"]
        code = block["content"]

        fenced_block = f"```{lang}\n{code}\n```" if lang else f"```\n{code}\n```"

        lines = "\n".join(
            f"{indent}{line}" if line else ""
            for line in fenced_block.splitlines()
        )

        if include_filename:
            filename = os.path.basename(block["file"])
            lines = f"{indent}**`{filename}`**\n{lines}"

        return lines

    return INCLUDE_RE.sub(replacer, md_content)


def process_markdown_file(input_path, output_path, blocks, include_filename=False):
    if not os.path.exists(input_path):
        print(f"[WARN] Fichier Markdown introuvable : {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    new_content = replace_includes_in_markdown(original_content, blocks, include_filename)

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"[OK] Fichier généré : {output_path}")


def main():
    try:
        lang_map, source_dirs, doc_files = load_config("config.yaml")
    except Exception as e:
        print(f"Erreur config : {e}")
        sys.exit(1)

    allowed_extensions = tuple(lang_map.keys())
    source_files = collect_source_files(source_dirs, allowed_extensions)
    blocks = scan_all_blocks(source_files, lang_map)

    print(f"[INFO] {len(source_files)} fichier(s) source analysé(s)")
    print(f"[INFO] {len(blocks)} bloc(s) trouvé(s)")

    for entry in doc_files:
        include_filename = entry.get("include_filename", False)
        process_markdown_file(entry["input"], entry["output"], blocks, include_filename)


if __name__ == "__main__":
    main()