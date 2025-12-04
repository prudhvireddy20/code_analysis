import os
import json
import subprocess
import traceback

def run_semgrep_scan(source_path, backend_dir=None):
    results = {}
    try:
        # Define default backend directory
        if backend_dir is None:
            backend_dir = os.path.expanduser("~/semgrep_storage")

        os.makedirs(backend_dir, exist_ok=True)

        output_dir = os.path.join(backend_dir, "results")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "semgrep-results.json")

        print(f"\n[INFO] Semgrep scan output path: {output_file}")

        # Run semgrep scan with built-in security rules
        subprocess.run([
            "semgrep",
            "--config", "auto",            # auto-detect languages
            "--json",                      # output JSON
            "--output", output_file,
            source_path
        ], check=True)

        if not os.path.exists(output_file):
            raise FileNotFoundError(f"Semgrep results not found at {output_file}")

        with open(output_file, "r", encoding="utf-8") as f:
            results["semgrep"] = json.load(f)

    except subprocess.CalledProcessError as e:
        print("semgrep faced an issue\n")
        results["semgrep"] = {"error": "Semgrep scan failed", "details": str(e)}
    except Exception:
        print("semgrep faced an exception")
        results["semgrep"] = {"error": "Exception in Semgrep", "details": traceback.format_exc()}

    return results
