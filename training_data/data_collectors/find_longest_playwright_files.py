import os
import argparse
from pathlib import Path
import shutil

def is_playwright_test(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return "@playwright/test" in f.read()
    except Exception:
        return False

def count_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def find_longest_playwright_tests(root_dir, top_n=10):
    extensions = (".ts", ".js", ".mjs")
    matches = []

    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(extensions):
                full_path = os.path.join(dirpath, file)
                if is_playwright_test(full_path):
                    line_count = count_lines(full_path)
                    matches.append((line_count, Path(full_path)))

    matches.sort(reverse=True)
    return matches[:top_n]

def save_top_files(file_list, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, (line_count, file_path) in enumerate(file_list, 1):
        target_name = f"{i:02d}_{file_path.name}"
        target_path = output_dir / target_name

        try:
            shutil.copy(file_path, target_path)
            print(f"[✓] Saved: {target_name} ({line_count} lines)")
        except Exception as e:
            print(f"[!] Failed to copy {file_path}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find and save longest Playwright test files.")
    parser.add_argument("directory", type=Path, help="Directory to search")
    parser.add_argument("--top", type=int, default=10, help="Top N longest files to return")
    parser.add_argument("--out", type=Path, default=Path("longest_playwright_tests"),
                        help="Output directory to store longest files")

    args = parser.parse_args()

    results = find_longest_playwright_tests(args.directory, args.top)
    if not results:
        print("No Playwright test files found.")
    else:
        save_top_files(results, args.out)
