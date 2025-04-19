import os
import mimetypes
import argparse
import sys


def is_text_file(filepath):
    mime = mimetypes.guess_type(filepath)[0]
    if mime and mime.startswith("text"):
        return True
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(512)
            if b'\0' in chunk:
                return False
    except:
        return False
    return True


def escape_quotes(text):
    return text.replace('"', '\"')


def should_ignore(path, ignore_list):
    abs_path = os.path.abspath(path)
    for ignore in ignore_list:
        ignore_path = os.path.abspath(ignore)
        if abs_path == ignore_path:
            return True
    return False


def write_tree(path, output, prefix="", script_name="", base_path="", ignore_list=[]):
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return

    entries = [e for e in entries if not should_ignore(os.path.join(path, e), ignore_list)]
    entries_count = len(entries)
    for index, entry in enumerate(entries):
        entry_path = os.path.join(path, entry)

        if os.path.abspath(entry_path) == script_name:
            continue

        connector = "├─" if index < entries_count - 1 else "└─"
        output.write(f"{prefix}{connector} {entry}\n")

        if os.path.isdir(entry_path):
            new_prefix = prefix + ("│  " if index < entries_count - 1 else "   ")
            write_tree(entry_path, output, new_prefix, script_name, base_path, ignore_list)
        else:
            file_prefix = prefix + ("│  " if index < entries_count - 1 else "   ")
            output.write(f"{file_prefix}├─ ")
            try:
                size = os.path.getsize(entry_path)
                if size > args.max_file_size or not is_text_file(entry_path):
                    output.write("...\n")
                else:
                    with open(entry_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read().strip().replace("\n", "\\n")
                        output.write(f'"{escape_quotes(content)}"\n')
            except Exception as e:
                output.write(f"Error reading file: {e}\n")


def generate_tree(root_folder, max_file_size, output_file, ignore_list):
    script_path = os.path.abspath(sys.argv[0])
    abs_output_path = os.path.abspath(output_file)
    abs_ignore_list = [os.path.abspath(os.path.join(root_folder, i)) for i in ignore_list]
    abs_ignore_list.append(abs_output_path)  # Exclude output file itself

    with open(output_file, "w", encoding="utf-8") as out:
        out.write(f"{os.path.basename(root_folder)}/\n")
        write_tree(root_folder, out, script_name=script_path, base_path=root_folder, ignore_list=abs_ignore_list)


if __name__ == "__main__":
    if len(sys.argv) == 1 or any(arg.lower() in ["h", "help", "-h", "-help", "--h", "--help"] for arg in sys.argv[1:]):
        print("""
Usage: python script_name.py [--max_file_size SIZE_IN_BYTES] [--output_file OUTPUT_PATH] [--ignore FOLDER_OR_FILE ...]

Arguments:
  --max_file_size   Maximum size in bytes to include file content (default: 1024)
  --output_file     Output .txt file name (default: output.txt)
  --ignore          List of folders or files to ignore (relative to root folder)
        """)
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Generate ASCII tree with file contents.")
    parser.add_argument("--max_file_size", type=int, default=1024, help="Maximum file size to include contents (in bytes).")
    parser.add_argument("--output_file", type=str, default="output.txt", help="Path to output text file.")
    parser.add_argument("--ignore", nargs='*', default=[], help="List of folders or files to ignore (relative to the root folder).")
    args = parser.parse_args()

    current_directory = os.getcwd()
    generate_tree(current_directory, args.max_file_size, args.output_file, args.ignore)
