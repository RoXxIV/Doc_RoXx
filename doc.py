import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    print("Erreur : PyYAML n'est pas installé.")
    print("Installe-le avec : pip install pyyaml")
    sys.exit(1)


BLOCK_START_RE = re.compile(r"#([A-Za-z0-9_.-]+)#BEGIN(?::([A-Za-z0-9_+.-]+))?")
BLOCK_END_RE = re.compile(r"#([A-Za-z0-9_.-]+)#END")
INCLUDE_RE = re.compile(
    r"^([ \t]*)!INCLUDE\s+([A-Za-z0-9_.-]+)((?:\s+[A-Za-z0-9_.-]+:[^\s]+)*)[ \t]*$",
    re.MULTILINE,
)


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
    duplicates = []
    stack = []  # list de [block_id, inline_lang, code_lines]

    for line in lines:
        start_match = BLOCK_START_RE.search(line)
        end_match = BLOCK_END_RE.search(line)

        if start_match:
            block_id = start_match.group(1)
            inline_lang = start_match.group(2)
            stack.append([block_id, inline_lang, []])

        elif end_match and stack and stack[-1][0] == end_match.group(1):
            block_id, inline_lang, code_lines = stack.pop()
            code_content = "".join(code_lines)
            code_content = re.sub(r"\n\s*\n+", "\n", code_content).strip()
            if block_id not in blocks:
                blocks[block_id] = {
                    "content": code_content,
                    "lang": inline_lang if inline_lang else lang,
                    "file": file_path,
                }
            else:
                duplicates.append((block_id, file_path, file_path))

        else:
            for item in stack:
                item[2].append(line)

    for item in stack:
        print(f"[WARN] Bloc '{item[0]}' sans fin trouvée dans {file_path}")

    return blocks, duplicates


def scan_all_blocks(source_files, lang_map, strict=False):
    all_blocks = {}
    duplicates = []

    for file_path in source_files:
        ext = os.path.splitext(file_path)[1]
        lang = lang_map.get(ext, "")

        file_blocks, file_duplicates = extract_blocks_from_file(file_path, lang)
        duplicates.extend(file_duplicates)

        for block_id, block_data in file_blocks.items():
            if block_id not in all_blocks:
                all_blocks[block_id] = block_data
            else:
                duplicates.append((block_id, all_blocks[block_id]["file"], file_path))
                if not strict:
                    print(
                        f"[WARN] Doublon ignoré pour '{block_id}' dans {file_path} "
                        f"(premier conservé : {all_blocks[block_id]['file']})"
                    )

    if strict and duplicates:
        print(f"[ERREUR] {len(duplicates)} doublon(s) détecté(s) — génération annulée :\n")
        for block_id, first, second in duplicates:
            print(f"  '{block_id}'")
            print(f"    -> {first}")
            print(f"    -> {second}")
        sys.exit(1)

    return all_blocks


def parse_include_params(params_str):
    params = {}
    for token in params_str.split():
        if ":" in token:
            key, value = token.split(":", 1)
            params[key] = value
    return params


def replace_includes_in_markdown(md_content, blocks, include_filename=False):
    def replacer(match):
        indent = match.group(1)
        block_id = match.group(2)
        params = parse_include_params(match.group(3))

        if block_id not in blocks:
            return f"{indent}<!-- Missing block: {block_id} -->"

        block = blocks[block_id]
        lang = params.get("lang", block["lang"])
        code = block["content"]

        show_filename = include_filename
        if "filename" in params:
            show_filename = params["filename"].lower() == "true"

        fenced_block = f"```{lang}\n{code}\n```" if lang else f"```\n{code}\n```"

        lines = "\n".join(
            f"{indent}{line}" if line else ""
            for line in fenced_block.splitlines()
        )

        if show_filename:
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


def get_doc_blocks(input_path):
    """Retourne l'ensemble des block IDs référencés dans un template Markdown."""
    if not os.path.exists(input_path):
        return set()
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {m.group(2) for m in INCLUDE_RE.finditer(content)}


def main():
    parser = argparse.ArgumentParser(description="Doc_RoXx — générateur de documentation")
    parser.add_argument(
        "--file", metavar="FILENAME",
        help="Ne régénère que les docs utilisant des blocs de ce fichier source (ex: TaskDashboard.vue)"
    )
    parser.add_argument(
        "--block", metavar="BLOCK_ID",
        help="Ne régénère que les docs contenant cette ancre (ex: TASK_ADD)"
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Arrête l'exécution si des blocs en doublon sont détectés"
    )
    args = parser.parse_args()

    try:
        lang_map, source_dirs, doc_files = load_config("config.yaml")
    except Exception as e:
        print(f"Erreur config : {e}")
        sys.exit(1)

    allowed_extensions = tuple(lang_map.keys())
    source_files = collect_source_files(source_dirs, allowed_extensions)
    blocks = scan_all_blocks(source_files, lang_map, strict=args.strict)

    print(f"[INFO] {len(source_files)} fichier(s) source analysé(s)")
    print(f"[INFO] {len(blocks)} bloc(s) trouvé(s)")

    filtered_docs = doc_files

    if args.file:
        target_blocks = {
            block_id for block_id, data in blocks.items()
            if os.path.basename(data["file"]) == args.file
        }
        if not target_blocks:
            print(f"[WARN] Aucun bloc trouvé dans le fichier source : {args.file}")
            sys.exit(0)
        filtered_docs = [
            entry for entry in doc_files
            if get_doc_blocks(entry["input"]) & target_blocks
        ]
        if not filtered_docs:
            print(f"[INFO] Aucun doc ne référence des blocs de : {args.file}")
            sys.exit(0)
        print(f"[INFO] --file {args.file} : {len(target_blocks)} bloc(s), {len(filtered_docs)} doc(s) à régénérer")

    elif args.block:
        if args.block not in blocks:
            print(f"[WARN] Bloc introuvable : {args.block}")
            sys.exit(1)
        filtered_docs = [
            entry for entry in doc_files
            if args.block in get_doc_blocks(entry["input"])
        ]
        if not filtered_docs:
            print(f"[INFO] Aucun doc ne référence le bloc : {args.block}")
            sys.exit(0)
        print(f"[INFO] --block {args.block} : {len(filtered_docs)} doc(s) à régénérer")

    for entry in filtered_docs:
        include_filename = entry.get("include_filename", False)
        process_markdown_file(entry["input"], entry["output"], blocks, include_filename)


if __name__ == "__main__":
    main()