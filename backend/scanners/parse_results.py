import json
import re
import os
import traceback

# def parse_codeql(codeql_result):
#     results = []
#     try:
#         if not codeql_result or "error" in codeql_result:
#             return [{"tool": "CodeQL", "error": codeql_result.get("error", "No results"),
#                      "details": codeql_result.get("details", "")}]

#         for run in codeql_result.get("runs", []):
#             for result in run.get("results", []):
#                 rule = result.get("ruleId", "N/A")
#                 message = result.get("message", {}).get("text", "")
#                 file_path = (
#                     result.get("locations", [{}])[0]
#                     .get("physicalLocation", {})
#                     .get("artifactLocation", {})
#                     .get("uri", "")
#                 )

#                 results.append({
#                     "tool": "CodeQL",
#                     "rule": rule,
#                     "message": message,
#                     "file": file_path
#                 })
#     except Exception as e:
#         results.append({"tool": "CodeQL", "error": f"Parse error: {e}"})
#     return results


def parse_single_sarif(sarif):
    results = []

    if not sarif or "error" in sarif:
        return [
            {
                "tool": "CodeQL",
                "error": sarif.get("error", "No results"),
                "details": sarif.get("details", ""),
            }
        ]

    # build rule → severity map
    rule_map = {}
    for run in sarif.get("runs", []):
        driver = run.get("tool", {}).get("driver", {})
        for rule in driver.get("rules", []):
            rule_map[rule["id"]] = rule.get("defaultConfiguration", {}).get(
                "level", "unknown"
            )

    for run in sarif.get("runs", []):
        for result in run.get("results", []):
            rule_id = result.get("ruleId", "N/A")
            message = result.get("message", {}).get("text", "")

            # file + line
            physical = result.get("locations", [{}])[0].get("physicalLocation", {})
            file_path = physical.get("artifactLocation", {}).get("uri", "")
            line = physical.get("region", {}).get("startLine", "")

            severity = rule_map.get(rule_id, "unknown")

            results.append(
                {
                    "tool": "CodeQL",
                    "rule": rule_id,
                    "message": message,
                    "severity": severity,
                    "file": f"{file_path}:{line}" if line else file_path,
                }
            )

    if not results:
        results.append(
            {"tool": "CodeQL", "message": "No vulnerabilities found in this SARIF."}
        )

    return results


def parse_all_codeql(all_results):
    final_results = []

    for lang, sarif in all_results.items():
        # handle failures
        if sarif.get("status") == "skipped" or "error" in sarif:
            final_results.append(
                {
                    "tool": "CodeQL",
                    "language": lang,
                    "error": sarif.get("error", sarif.get("reason", "Scan skipped")),
                    "details": sarif.get("details", ""),
                }
            )
            continue

        parsed = parse_single_sarif(sarif)
        for item in parsed:
            item["language"] = lang
            final_results.append(item)

    return final_results


def parse_syft(sbom_result):

    results = []
    try:

        # CycloneDX puts packages under "components"
        for component in sbom_result.get("components", []):
            name = component.get("name", "")
            version = component.get("version", "")
            purl = component.get("purl", "")
            type_ = component.get("type", "")

            results.append(
                {
                    "tool": "Syft",
                    "name": name,
                    "version": version,
                    "type": type_,
                    "purl": purl,
                }
            )
    except Exception as e:
        results.append({"tool": "Syft", "error": f"Parse error: {e}"})

    return results


# backend/scanners/parse_results.py
def parse_osv(osv_result):
    results = []
    try:
        # Handle error cases first
        if isinstance(osv_result, dict) and "error" in osv_result:
            return [
                {
                    "tool": "OSV-Scanner",
                    "error": osv_result.get("error", "Unknown error"),
                    "details": osv_result.get("details", ""),
                }
            ]

        # Check if we have the main 'results' key
        if not isinstance(osv_result, dict) or "results" not in osv_result:
            return [
                {
                    "tool": "OSV-Scanner",
                    "error": "Invalid OSV result format",
                    "received_data": str(type(osv_result)),
                }
            ]

        for result in osv_result.get("results", []):
            for pkg in result.get("packages", []):
                package_info = pkg.get("package", {})
                pkg_name = package_info.get("name", "Unknown")
                pkg_version = package_info.get("version", "Unknown")
                pkg_ecosystem = package_info.get("ecosystem", "Unknown")

                vulnerabilities = pkg.get("vulnerabilities", [])

                if vulnerabilities:
                    for vuln in vulnerabilities:
                        vuln_id = vuln.get("id", "N/A")
                        aliases = vuln.get("aliases", [])
                        cve_ids = [
                            alias for alias in aliases if alias.startswith("CVE-")
                        ]
                        display_id = cve_ids[0] if cve_ids else vuln_id

                        severity_val = "UNKNOWN"
                        db_specific = vuln.get("database_specific", {})
                        if "severity" in db_specific:
                            severity_val = db_specific["severity"]
                        elif "severity" in vuln and isinstance(vuln["severity"], list):
                            for severity_item in vuln["severity"]:
                                if severity_item.get("type") == "CVSS_V3":
                                    severity_val = f"CVSS_V3: {severity_item.get('score', 'UNKNOWN')}"
                                    break
                                elif severity_item.get("score"):
                                    severity_val = severity_item.get("score")
                                    break

                        summary = vuln.get("summary", "")
                        details = vuln.get("details", summary)

                        results.append(
                            {
                                "tool": "OSV-Scanner",
                                "package": pkg_name,
                                "version": pkg_version,
                                "ecosystem": pkg_ecosystem,
                                "id": display_id,
                                "severity": severity_val,
                                "summary": summary,
                                "details": details,
                            }
                        )
                else:
                    results.append(
                        {
                            "tool": "OSV-Scanner",
                            "package": pkg_name,
                            "version": pkg_version,
                            "ecosystem": pkg_ecosystem,
                            "status": "No vulnerabilities found",
                        }
                    )

        if not results:
            results.append(
                {
                    "tool": "OSV-Scanner",
                    "status": "No vulnerabilities found",
                    "summary": "Scan completed successfully but no vulnerabilities detected.",
                }
            )

    except Exception as e:
        results.append(
            {
                "tool": "OSV-Scanner",
                "error": f"Parse error: {str(e)}",
                "traceback": traceback.format_exc(),
            }
        )

    return results


def parse_gitleaks(gitleaks_result):

    results = []
    try:
        if not gitleaks_result:
            return [{"tool": "Gitleaks", "error": "No results"}]

        if isinstance(gitleaks_result, dict):
            if "error" in gitleaks_result:
                return [
                    {
                        "tool": "Gitleaks",
                        "error": gitleaks_result.get("error"),
                        "details": gitleaks_result.get("details", ""),
                    }
                ]
            if "message" in gitleaks_result:
                return [{"tool": "Gitleaks", "message": gitleaks_result["message"]}]

        if isinstance(gitleaks_result, list):
            for leak in gitleaks_result:
                results.append(
                    {
                        "tool": "Gitleaks",
                        "rule": leak.get("RuleID", ""),
                        "file": leak.get("File", ""),
                        "secret": leak.get("Secret", "[REDACTED]"),
                        "line": leak.get("StartLine", ""),
                    }
                )

    except Exception as e:
        results.append({"tool": "Gitleaks", "error": f"Parse error: {e}"})

    return results


def parse_noir(noir_result):

    """
    Parse OWASP Noir JSON output into a standardized list of dictionaries.
    """
    print(noir_result, "\n")
    results = []
    try:
        if not noir_result:
            return [{"tool": "Noir", "error": "No results found"}]

        # Handle error returned by the scan
        if isinstance(noir_result, dict):
            if "error" in noir_result:
                print("There is error in noir result\n")
                return [
                    {
                        "tool": "Noir",
                        "error": noir_result.get("error"),
                        "details": noir_result.get("details", ""),
                    }
                ]
            # Handle message-only responses
            if "message" in noir_result:
                print("There is no message form noir\n")
                return [{"tool": "Noir", "message": noir_result["message"]}]

        # Assume main results are in a list of findings
        if isinstance(noir_result, list):
            for finding in noir_result:
                # Each finding may contain keys like: 'file', 'line', 'severity', 'description', 'rule'
                results.append(
                    {
                        "tool": "Noir",
                        "rule": finding.get("rule", ""),
                        "file": finding.get("file", ""),
                        "line": finding.get("line", ""),
                        "severity": finding.get("severity", ""),
                        "description": finding.get("description", ""),
                    }
                )

    except Exception as e:

        results.append({"tool": "Noir", "error": f"Parse error: {e}"})

    return results


# def parse_semgrep(semgrep_result):
#     results = []
#     try:
#         if not semgrep_result or "error" in semgrep_result:
#             return [{
#                 "tool": "Semgrep",
#                 "error": semgrep_result.get("error", "No results"),
#                 "details": semgrep_result.get("details", "")
#             }]

#         findings = semgrep_result.get("results", [])
#         for item in findings:
#             rule_id = item.get("check_id", "N/A")
#             message = item.get("extra", {}).get("message", "")
#             file_path = item.get("path", "")
#             start_line = item.get("start", {}).get("line", "")
#             end_line = item.get("end", {}).get("line", "")

#             results.append({
#                 "tool": "Semgrep",
#                 "rule": rule_id,
#                 "message": message,
#                 "file": file_path,
#                 "start_line": start_line,
#                 "end_line": end_line
#             })

#     except Exception as e:
#         results.append({"tool": "Semgrep", "error": f"Parse error: {e}"})
#     return results


import json


def parse_semgrep(semgrep_result):
    results = []

    # print("\n--- RAW SEMGREP RESULT ---")
    # print(json.dumps(semgrep_result, indent=2))

    try:
        # Semgrep result is nested under semgrep: {...}
        semgrep_data = semgrep_result.get("semgrep", {})

        if not semgrep_data:
            print("No semgrep data found")
            return []

        raw_results = semgrep_data.get("results", [])
        print(f"Semgrep results count: {len(raw_results)}")

        for item in raw_results:
            results.append(
                {
                    "path": item.get("path", ""),
                    "check_id": item.get("check_id", "N/A"),
                    "extra": {"message": item.get("extra", {}).get("message", "")},
                    "start": {"line": item.get("start", {}).get("line", None)},
                }
            )

    except Exception as e:
        print("Error parsing semgrep:", e)
        results.append(
            {
                "path": "",
                "check_id": "parse_error",
                "extra": {"message": str(e)},
                "start": {"line": None},
            }
        )

    # print("\n--- PARSED SEMGREP RESULT ---")
    # print(json.dumps(results, indent=2))

    return results
