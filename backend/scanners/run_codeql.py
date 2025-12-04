import os
import subprocess
import json
import traceback

# def run_codeql_scan(
#     source_path,
#     language="python",
#     backend_dir=None
# ):
#     results = {}
#     try:
#         # Use a user-writable path if none is provided
#         if backend_dir is None:
#             backend_dir = os.path.expanduser("~/codeql_storage")  # 👈 safe default

#         os.makedirs(backend_dir, exist_ok=True)

#         db_path = os.path.join(backend_dir, f"codeql-db-{language}")
#         output_dir = os.path.join(backend_dir, "results")
#         os.makedirs(output_dir, exist_ok=True)

#         output_file = os.path.join(output_dir, f"codeql-{language}.sarif")

#         print(f"\n[INFO] CodeQL database path: {db_path}")
#         print(f"[INFO] SARIF output path: {output_file}")

#         subprocess.run([
#             "codeql", "database", "create", db_path,
#             f"--language={language}",
#             "--source-root", source_path,
#             "--overwrite"
#         ], check=True)

#         subprocess.run([
#             "codeql", "database", "analyze", db_path,
#             f"codeql/{language}-queries:codeql-suites/{language}-security-and-quality.qls",
#             "--format=sarifv2.1.0",
#             "--output", output_file,
#             "--rerun"
#         ], check=True)

#         if not os.path.exists(output_file):
#             raise FileNotFoundError(f"SARIF results not found at {output_file}")

#         with open(output_file, "r", encoding="utf-8") as f:
#             results[language] = json.load(f)

#     except subprocess.CalledProcessError as e:
#         results[language] = {"error": "CodeQL scan failed", "details": str(e)}
#     except Exception:
#         results[language] = {"error": "Exception in CodeQL", "details": traceback.format_exc()}

#     print(f"CodeQL scan completed with {len(results['python']['runs'][0].get('results', []))} findings.")



#     return results

'''Code Implemented for choosing automatic languge and muliple languages.
!!!!LOOK HERE   ----   Ther is an issue with this code and not running currently, so what you need to do is to debug this code. '''
# import os
# import subprocess
# import json
# import traceback
# import glob

# def detect_languages(source_path):
#     """Detect which supported languages are present based on file extensions."""
#     extensions = {
#         "python": [".py"],
#         "javascript": [".js", ".jsx", ".ts", ".tsx"],
#         "cpp": [".cpp", ".cc", ".h", ".hpp", ".c"],
#         "java": [".java"],
#         "go": [".go"],
#         "ruby": [".rb"],
#         "csharp": [".cs"],
#     }

#     counts = {}
#     for lang, exts in extensions.items():
#         count = sum(
#             len(glob.glob(os.path.join(source_path, f"**/*{ext}"), recursive=True))
#             for ext in exts
#         )
#         if count > 0:
#             counts[lang] = count

#     return sorted(counts.keys(), key=lambda l: counts[l], reverse=True)


# def get_supported_languages():
#     """Ask CodeQL which languages are supported in this installation."""
#     try:
#         output = subprocess.check_output(["codeql", "resolve", "languages"], text=True)
#         langs = [line.strip() for line in output.splitlines() if line.strip()]
#         return langs
#     except Exception:
#         # fallback to known languages
#         return ["python", "javascript", "cpp", "java", "go", "ruby", "csharp"]


# def run_codeql_scan(source_path, language="python", backend_dir=None):
#     results = {}

#     try:
#         # Safe default backend dir
#         if backend_dir is None:
#             backend_dir = os.path.expanduser("~/codeql_storage")

#         os.makedirs(backend_dir, exist_ok=True)

#         # Auto-detect languages if not provided
#         supported = get_supported_languages()
#         detected = detect_languages(source_path)
#         if language:
#             langs_to_scan = [language] if language in supported else []
#         else:
#             langs_to_scan = [l for l in detected if l in supported]

#         if not langs_to_scan:
#             raise RuntimeError("No supported languages found in source directory.")

#         print(f"[INFO] Languages to scan: {langs_to_scan}")

#         output_dir = os.path.join(backend_dir, "results")
#         os.makedirs(output_dir, exist_ok=True)

#         for lang in langs_to_scan:
#             db_path = os.path.join(backend_dir, f"codeql-db-{lang}")
#             output_file = os.path.join(output_dir, f"codeql-{lang}.sarif")

#             print(f"\n[INFO] === Scanning {lang} code ===")
#             print(f"[INFO] Database path: {db_path}")
#             print(f"[INFO] SARIF output: {output_file}")

#             subprocess.run([
#                 "codeql", "database", "create", db_path,
#                 f"--language={lang}",
#                 "--source-root", source_path,
#                 "--overwrite"
#             ], check=True)

#             subprocess.run([
#                 "codeql", "database", "analyze", db_path,
#                 f"codeql/{lang}-queries:codeql-suites/{lang}-security-and-quality.qls",
#                 "--format=sarifv2.1.0",
#                 "--output", output_file,
#                 "--rerun"
#             ], check=True)

#             if not os.path.exists(output_file):
#                 raise FileNotFoundError(f"SARIF results not found for {lang}")

#             with open(output_file, "r", encoding="utf-8") as f:
#                 results[lang] = json.load(f)

#         # Merge SARIF results into one combined report
#         merged_sarif_path = os.path.join(output_dir, "codeql-combined.sarif")
#         all_runs = []
#         for sarif in results.values():
#             all_runs.extend(sarif.get("runs", []))
#         merged = {"version": "2.1.0", "runs": all_runs}
#         with open(merged_sarif_path, "w", encoding="utf-8") as f:
#             json.dump(merged, f, indent=2)
#         print(f"\n[INFO] Combined SARIF written to {merged_sarif_path}")

#         # Print summary
#         for lang, sarif in results.items():
#             findings = len(sarif.get("runs", [])[0].get("results", [])) if "runs" in sarif else 0
#             print(f"[INFO] {lang}: {findings} findings")

#     except subprocess.CalledProcessError as e:
#         results["error"] = {"error": "CodeQL scan failed", "details": str(e)}
#     except Exception:
#         results["error"] = {"error": "Exception in CodeQL", "details": traceback.format_exc()}

#     return results





# ---------------------------------------
# Detect languages based on file types
# ---------------------------------------
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


# # ---------------------------------------
# # Run CodeQL scan for one language
# # ---------------------------------------
# def run_codeql_scan_for_language(source_path, language, backend_dir):
#     results = {}

#     try:
#         db_path = os.path.join(backend_dir, f"codeql-db-{language}")
#         output_dir = os.path.join(backend_dir, "results")
#         os.makedirs(output_dir, exist_ok=True)

#         output_file = os.path.join(output_dir, f"codeql-{language}.sarif")

#         print(f"\n[INFO] Scanning {language} ...")
#         print(f"[INFO] Database: {db_path}")
#         print(f"[INFO] Output: {output_file}")

#         # Create database
#         subprocess.run([
#             "codeql", "database", "create", db_path,
#             f"--language={language}",
#             "--source-root", source_path,
#             "--overwrite"
#         ], check=True)

#         # Analyze
#         subprocess.run([
#             "codeql", "database", "analyze", db_path,
#             f"codeql/{language}-queries:codeql-suites/{language}-security-and-quality.qls",
#             "--format=sarifv2.1.0",
#             "--output", output_file,
#             "--rerun"
#         ], check=True)

#         with open(output_file, "r", encoding="utf-8") as f:
#             results[language] = json.load(f)

#     except Exception:
#         results[language] = {
#             "error": f"CodeQL scan failed for {language}",
#             "details": traceback.format_exc()
#         }

#     return results

def should_skip_cpp(source_path):
    BUILD_HINTS = [
        "Makefile", "CMakeLists.txt", "build.ninja",
        "configure", ".pro", "meson.build"
    ]
    
    for root, _, files in os.walk(source_path):
        if any(f in files for f in BUILD_HINTS):
            return False
    return True

# def run_codeql_scan_for_language(source_path, language, backend_dir):
#     results = {}

#     QUERY_PACK = {
#         "python": "codeql/python-queries:codeql-suites/python-security-and-quality.qls",
#         "javascript": "codeql/javascript-queries:codeql-suites/javascript-security-and-quality.qls",
#         "typescript": "codeql/javascript-queries:codeql-suites/javascript-security-and-quality.qls",  
#         "java": "codeql/java-queries:codeql-suites/java-security-and-quality.qls",
#         "cpp": "codeql/cpp-queries:codeql-suites/cpp-security-and-quality.qls",
#         "csharp": "codeql/csharp-queries:codeql-suites/csharp-security-and-quality.qls",
#         "go": "codeql/go-queries:codeql-suites/go-security-and-quality.qls",
#         "ruby": "codeql/ruby-queries:codeql-suites/ruby-security-and-quality.qls",
#     }

#     # Skip C++ if no build system exists
#     if language == "cpp" and should_skip_cpp(source_path):
#         print(f"⚠️ Skipping {language} — no build system found.")
#         return {
#             language: {
#                 "status": "skipped",
#                 "reason": "No C++ build system detected"
#             }
#         }

#     try:
#         db_path = os.path.join(backend_dir, f"codeql-db-{language}")
#         output_dir = os.path.join(backend_dir, "results")
#         os.makedirs(output_dir, exist_ok=True)

#         output_file = os.path.join(output_dir, f"codeql-{language}.sarif")

#         print(f"\n[INFO] Scanning {language} ...")

#         # Create DB
#         subprocess.run([
#             "codeql", "database", "create", db_path,
#             f"--language={language}",
#             "--source-root", source_path,
#             "--overwrite"
#         ], check=True)

#         # Analyze DB
#         subprocess.run([
#             "codeql", "database", "analyze", db_path,
#             QUERY_PACK[language],
#             "--format=sarifv2.1.0",
#             "--output", output_file,
#             "--rerun"
#         ], check=True)

#         # Load results
#         with open(output_file, "r", encoding="utf-8") as f:
#             sarif = json.load(f)
#             return {
#                 language: {
#                 "runs": sarif.get("runs", []),  # OLD EXPECTED STRUCTURE
#                 "status": "success",
#                 "issue_count": sum(len(run.get("results", [])) for run in sarif.get("runs", []))
#                 }
#             }

#     except Exception as e:
#         # Fail-safe mode — only this language fails
#         print(f"❌ CodeQL failed for {language}: {e}")
#         return {
#             language: {
#                 "status": "failed",
#                 "error": str(e),
#                 "details": traceback.format_exc()
#             }
#         }


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
                "runs": [],   # MUST match old format!
                "error": "No C++ build system detected"
            }
        }

    try:
        db_path = os.path.join(backend_dir, f"codeql-db-{language}")
        output_dir = os.path.join(backend_dir, "results")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"codeql-{language}.sarif")

        subprocess.run([
            "codeql", "database", "create", db_path,
            f"--language={language}",
            "--source-root", source_path,
            "--overwrite"
        ], check=True)

        subprocess.run([
            "codeql", "database", "analyze", db_path,
            QUERY_PACK[language],
            "--format=sarifv2.1.0",
            "--output", output_file,
            "--rerun"
        ], check=True)

        # Load SARIF
        with open(output_file, "r", encoding="utf-8") as f:
            sarif = json.load(f)

        # 🎯 Return EXACT same format as old system!
        return { language: sarif }

    except Exception as e:
        return {
            language: {
                "runs": [],
                "error": str(e),
                "details": traceback.format_exc()
            }
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
    
    #print(all_results)
    return all_results
