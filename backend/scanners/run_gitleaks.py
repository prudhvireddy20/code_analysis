# scanners/run_gitleaks.py
import subprocess
import json
import os
import traceback


def run_gitleaks_scan(path):
    try:
        output_dir = "results"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "gitleaks.json")

        cmd = [
            "gitleaks", "detect",
            "--source", path,
            "--report-format", "json",
            "--report-path", output_file,
            "-c", os.path.expanduser("~/.gitleaks/gitleaks.toml")
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # ✅ Exit 0 = no leaks, Exit 1 = leaks found
        if result.returncode not in (0, 1):
            return {"error": "Gitleaks scan failed",
                    "details": result.stderr.strip() or result.stdout.strip()}

        # ✅ Always try to parse the JSON report
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            with open(output_file) as f:
                return json.load(f)

        return {"message": "No leaks found."}

    except Exception as e:
        return {"error": f"Gitleaks exception: {str(e)}"}
