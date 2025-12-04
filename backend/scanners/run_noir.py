# import subprocess
# import json
# import os
# import traceback

# def run_noir_scan(path):
#     """
#     Run OWASP Noir scan on the given directory.
#     Returns JSON output if successful, else error details.
#     """
#     try:
#         output_dir = os.path.join(path, "noir_results")
#         os.makedirs(output_dir, exist_ok=True)
#         output_file = os.path.join(output_dir, "noir.json")

#         # Step 1: Run Noir scan
#         # Using -b <path> as base directory and --output <file> for JSON output
#         subprocess.run([
#             "noir",
#             "-b", path,
#             "--output", output_file,
#             "--format", "json"  # Ensure Noir outputs JSON
#         ], check=True)

#         # Step 2: Load results
#         with open(output_file) as f:
#             return json.load(f)

#     except subprocess.CalledProcessError as e:
#         return {"error": "Noir scan failed", "details": str(e)}
#     except Exception as e:
#         return {"error": "Exception in Noir scan", "details": traceback.format_exc()}

import subprocess
import json
import os
import traceback
import re

def run_noir_scan(path, tech="python_fastapi"):
    """
    Fully automatic OWASP Noir scan.
    Handles missing rules, CLI differences, and text-only output.
    Returns a list of findings.
    """

    valid_techs = subprocess.run(["noir", "tech", "list"], capture_output=True, text=True).stdout.splitlines()
    

    try:
        output_dir = os.path.join(path, "results")
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "noir.json")

        # --- Detect Noir command (scan or detect) ---
        try:
            help_output = subprocess.run(["noir", "--help"], capture_output=True, text=True).stdout
            noir_command = "detect" if "detect" in help_output else "scan"
        except Exception:
            noir_command = "scan"

        print(f"🕵️ Running OWASP Noir scan for tech: {tech}")

        # --- Ensure rulepacks exist ---
        rules_check = subprocess.run(
            ["noir", "rules", "list"], capture_output=True, text=True
        )
        if "no rules" in rules_check.stdout.lower() or not rules_check.stdout.strip():
            print("⚙️  Updating Noir rules (first-time setup)...")
            subprocess.run(["noir", "rules", "update"], capture_output=True, text=True)

        # --- Build Noir command ---
        cmd = [
            "noir", noir_command,
            "--base-path", path,
            "-t", tech,
            "--format", "json",
            "-o", output_file
        ]

        # --- Run Noir scan ---
        result = subprocess.run(cmd, capture_output=True, text=True)

        print("Noir STDOUT (truncated):\n", result.stdout[:300])
        print("Noir STDERR (truncated):\n", result.stderr[:300])

        if result.returncode != 0:
            print(" Noir scan completed and didn't find any output.")
            return []

        # --- Parse JSON output ---
        data = None
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
        else:
            # Attempt to load from stdout (may not be valid JSON)
            try:
                data = json.loads(result.stdout)
            except json.JSONDecodeError:
                # Try to extract textual findings if JSON missing
                findings = []
                for line in result.stdout.splitlines():
                    match = re.search(r"(?P<file>[\w\/\.-]+):(?P<line>\d+).*?(?P<desc>Potential|Possible|Detected).*", line)
                    if match:
                        findings.append({
                            "rule": "Unknown",
                            "file": match.group("file"),
                            "line": int(match.group("line")),
                            "description": match.group("desc"),
                            "severity": "medium",
                            "confidence": "low",
                            "tool": "Noir"
                        })
                if findings:
                    print(f"✅ Parsed {len(findings)} text-based Noir findings.")
                    return findings
                else:
                    print("⚠️ Noir produced no JSON or text findings.")
                    return []

        # --- Normalize JSON findings ---
        findings = []
        for item in data.get("findings", data.get("results", [])):
            findings.append({
                "rule": item.get("rule") or item.get("rule_id"),
                "file": item.get("file"),
                "line": item.get("line") or item.get("lineNumber"),
                "description": item.get("description") or item.get("message"),
                "severity": item.get("severity", "unknown"),
                "confidence": item.get("confidence", "N/A"),
                "tool": "Noir"
            })

        print(f"✅ OWASP Noir finished — {len(findings)} findings detected.")
        return findings

    except Exception as e:
        print("🔥 Exception in Noir scan:", e)
        print(traceback.format_exc())
        return []
