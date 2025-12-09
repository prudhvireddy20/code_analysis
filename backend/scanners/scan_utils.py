import os
import subprocess
import tempfile
import shutil
import traceback
import json
import zipfile

from scanners.run_codeql import run_codeql_scan
from scanners.run_gitleaks import run_gitleaks_scan
from scanners.run_syft import generate_sbom
from scanners.run_osv import run_osv_scan
from scanners.run_noir import run_noir_scan
from scanners.run_semgrep import run_semgrep_scan
from scanners.parse_results import (
    parse_syft,
    parse_osv,
    parse_gitleaks,
    parse_noir,
    parse_semgrep,
    parse_all_codeql,
)


def scan_project(input_type, repo_url_or_path):
    temp_dir = tempfile.mkdtemp(prefix="scan_input_")
    output_dir = tempfile.mkdtemp(prefix="scan_output_")
    repo_dir = os.path.join(temp_dir, "repo")

    try:
        os.makedirs(repo_dir, exist_ok=True)

        # ====================================================
        # 1️⃣ Input Handling (Git clone OR ZIP extraction)
        # ====================================================
        if input_type == "git":
            print(f"📥 Cloning repo: {repo_url_or_path}")
            subprocess.run(["git", "clone", repo_url_or_path, repo_dir], check=True)

        elif input_type == "upload":
            print(f"📦 Extracting ZIP file: {repo_url_or_path}")
            if not os.path.exists(repo_url_or_path):
                print("OOps... zip file not found\n")
                return {"error": f"ZIP file not found at {repo_url_or_path}"}, 400

            if not zipfile.is_zipfile(repo_url_or_path):
                print("Oops.... provided file is not valid.\n")
                return {"error": "Provided file is not a valid ZIP archive."}, 400

            with zipfile.ZipFile(repo_url_or_path, "r") as zip_ref:
                zip_ref.extractall(repo_dir)

            # ✅ Flatten structure if ZIP extracts with a top-level folder
            extracted_items = os.listdir(repo_dir)
            if len(extracted_items) == 1:
                first_item = os.path.join(repo_dir, extracted_items[0])
                if os.path.isdir(first_item):
                    repo_dir = first_item
                    print(f"📁 Detected nested folder: using {repo_dir} as repo root")

        else:
            return {"error": "Only 'git' and 'zip' input types are supported."}, 400

        print(f"✅ Repository ready at: {repo_dir}")

        # ====================================================
        # 2️⃣ Install dependencies (Node.js only)
        # ====================================================
        package_json = os.path.join(repo_dir, "package.json")
        if os.path.exists(package_json):
            print("📦 Detected Node.js project. Running npm install...")
            subprocess.run(["npm", "install"], cwd=repo_dir, check=True)
        else:
            print("⚠️ No package.json found. Skipping npm install.")

        # ====================================================
        # 3️⃣ Run scanners (identical for Git or ZIP)
        # ====================================================
        print("🔐 Running Gitleaks...")
        gitleaks_results = run_gitleaks_scan(repo_dir)
        print("✅ Gitleaks finished")

        print("📦 Generating SBOM with Syft...")
        generate_sbom(repo_dir)
        sbom_file = "sbom/sbom.json"
        if not os.path.exists(sbom_file):
            raise FileNotFoundError(f"Syft did not generate SBOM at {sbom_file}")

        print("📊 Running OSV-Scanner...")
        osv_results = run_osv_scan(sbom_file)
        print("✅ OSV scan finished")

        print("🧠 Running CodeQL...")
        codeql_results = run_codeql_scan(repo_dir)
        print("✅ CodeQL finished")

        print("🕵️‍♂️ Running OWASP Noir scan...")
        noir_results = run_noir_scan(repo_dir)
        print("✅ OWASP Noir finished")

        print("🕵️‍♂️ Running SEMGREP")
        semgrep_results = run_semgrep_scan(repo_dir)
        print("✅ SEMGREP finished")

        # ====================================================
        # 4️⃣ Parse and return results
        # ====================================================
        print("✅ Parsing results...")
        with open(sbom_file, "r") as f:
            sbom_json = json.load(f)

        final_results = {
            "codeql": parse_all_codeql(codeql_results),
            "syft": parse_syft(sbom_json),
            "osv": parse_osv(osv_results),
            "gitleaks": parse_gitleaks(gitleaks_results),
            "noir": parse_noir(noir_results),
            "semgrep": parse_semgrep(semgrep_results),
        }

        print("🎉 All scans completed successfully!")
        return final_results

    except subprocess.CalledProcessError as e:
        print(f"❌ Subprocess error: {e}")
        print(f"STDERR: {getattr(e, 'stderr', '')}")
        return {"error": str(e), "details": traceback.format_exc()}, 500

    except Exception as ex:
        print(f"🔥 Unexpected error: {ex}")
        return {"error": str(ex), "details": traceback.format_exc()}, 500

    finally:
        print("🧹 Cleaning up temporary files...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(output_dir, ignore_errors=True)
