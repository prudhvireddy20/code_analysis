import os
import subprocess
import json
import traceback


LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "cpp": [".c", ".cpp", ".cc", ".h", ".hpp"],
    "csharp": [".cs"],
    "go": [".go"],
    "ruby": [".rb"],
}


def detect_languages_in_repo(source_path):
    detected = set()

    for root, _, files in os.walk(source_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            for lang, ext_list in LANGUAGE_EXTENSIONS.items():
                if ext in ext_list:
                    detected.add(lang)

    return list(detected)



def should_skip_cpp(source_path):
    BUILD_HINTS = [
        "Makefile",
        "CMakeLists.txt",
        "build.ninja",
        "configure",
        ".pro",
        "meson.build",
    ]

    for root, _, files in os.walk(source_path):
        if any(f in files for f in BUILD_HINTS):
            return False
    return True




def run_codeql_scan_for_language(source_path, language, backend_dir):

    QUERY_PACK = {
        "python": "codeql/python-queries:codeql-suites/python-security-and-quality.qls",
        "javascript": "codeql/javascript-queries:codeql-suites/javascript-security-and-quality.qls",
        "typescript": "codeql/javascript-queries:codeql-suites/javascript-security-and-quality.qls",
        "java": "codeql/java-queries:codeql-suites/java-security-and-quality.qls",
        "cpp": "codeql/cpp-queries:codeql-suites/cpp-security-and-quality.qls",
        "csharp": "codeql/csharp-queries:codeql-suites/csharp-security-and-quality.qls",
        "go": "codeql/go-queries:codeql-suites/go-security-and-quality.qls",
        "ruby": "codeql/ruby-queries:codeql-suites/ruby-security-and-quality.qls",
    }

    if language == "cpp" and should_skip_cpp(source_path):
        return {
            language: {
                "runs": [],  # MUST match old format!
                "error": "No C++ build system detected",
            }
        }

    try:
        db_path = os.path.join(backend_dir, f"codeql-db-{language}")
        output_dir = os.path.join(backend_dir, "results")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"codeql-{language}.sarif")

        subprocess.run(
            [
                "codeql",
                "database",
                "create",
                db_path,
                f"--language={language}",
                "--source-root",
                source_path,
                "--overwrite",
            ],
            check=True,
        )

        subprocess.run(
            [
                "codeql",
                "database",
                "analyze",
                db_path,
                QUERY_PACK[language],
                "--format=sarifv2.1.0",
                "--output",
                output_file,
                "--rerun",
            ],
            check=True,
        )

        # Load SARIF
        with open(output_file, "r", encoding="utf-8") as f:
            sarif = json.load(f)

        # 🎯 Return EXACT same format as old system!
        return {language: sarif}

    except Exception as e:
        return {
            language: {"runs": [], "error": str(e), "details": traceback.format_exc()}
        }


# ---------------------------------------
# Run CodeQL for all detected languages
# ---------------------------------------
def run_codeql_scan(source_path, backend_dir=None):
    if backend_dir is None:
        backend_dir = os.path.expanduser("~/codeql_storage")

    os.makedirs(backend_dir, exist_ok=True)

    # 1. Detect languages
    languages = detect_languages_in_repo(source_path)

    if not languages:
        print("❌ No supported CodeQL languages found.")
        return {}

    print(f"✅ Detected languages: {languages}")

    # 2. Run scan for all
    all_results = {}

    for lang in languages:
        result = run_codeql_scan_for_language(source_path, lang, backend_dir)
        all_results.update(result)

    # print(all_results)
    return all_results
