import subprocess
import os
import json
import traceback


def generate_sbom(path):
    try:
        output_dir = "sbom"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "sbom.json")

        subprocess.run(
            ["syft", path, "-o", "cyclonedx-json", "-q"],
            stdout=open(output_file, "w"),
            check=True
        )

        with open(output_file) as f:
            return json.load(f)

    except subprocess.CalledProcessError as e:
        return {"error": "Syft SBOM generation failed", "details": str(e)}
    except Exception as e:
        return {"error": "Exception in Syft", "details": traceback.format_exc()}
