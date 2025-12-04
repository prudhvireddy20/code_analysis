# backend/scanners/run_osv.py
import subprocess
import json
import os
import traceback

def run_osv_scan(sbom_file):
    try:
        # Make sure the SBOM file exists
        if not os.path.exists(sbom_file):
            return {"error": f"SBOM file not found: {sbom_file}", "details": "Please check the file path"}
        
        output_file = "osv-results.json"
        
        # Run OSV scanner with timeout to prevent hanging
        result = subprocess.run(
            ["osv-scanner", "--sbom", sbom_file, "--format", "json", "--output", output_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Check if the command succeeded OR found vulnerabilities (exit code 1)
        if result.returncode not in [0, 1]:
            return {
                "error": "OSV-Scanner failed",
                "details": result.stderr.strip() or result.stdout.strip(),
                "returncode": result.returncode
            }
        
        # Check if output file was created
        if not os.path.exists(output_file):
            return {"error": "OSV-Scanner did not generate output file", "details": "Check osv-scanner installation"}
        
        # Read and return the results
        with open(output_file, "r") as f:
            return json.load(f)
            
    except subprocess.TimeoutExpired:
        return {"error": "OSV-Scanner timed out after 5 minutes", "details": "The scan took too long to complete"}
    except subprocess.CalledProcessError as e:
        return {"error": "OSV-Scanner process error", "details": str(e)}
    except Exception as e:
        return {"error": "Exception in OSV", "details": traceback.format_exc()}