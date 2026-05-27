import re
import json

def parse_nmap_output(raw_output: str) -> dict:
    result = {
        "host": "",
        "os": "",
        "ports": []
    }

    # Extract host
    host_match = re.search(r"Nmap scan report for (.+)", raw_output)
    if host_match:
        result["host"] = host_match.group(1).strip()

    # Extract OS
    os_match = re.search(r"OS details:\s*(.+)", raw_output)
    if os_match:
        result["os"] = os_match.group(1).strip()

    # Extract ports - only grab the port line itself, not script output
    lines = raw_output.splitlines()
    for line in lines:
        # Match lines like: 445/tcp   open   microsoft-ds?
        match = re.match(r"^(\d+)/tcp\s+(open|closed|filtered)\s+(\S+)\s*(.*)", line)
        if not match:
            continue

        version = re.sub(r"^(syn-ack|reset|no-response|host-unreach)\s*", "", match.group(4).strip())

        # Ignore version if it starts with script output characters
        if version.startswith("|") or version.startswith("_"):
            version = ""

        port_entry = {
            "port": int(match.group(1)),
            "state": match.group(2).strip(),
            "service": match.group(3).strip().rstrip("?"),
            "version": version
        }
        result["ports"].append(port_entry)

    return result


def parse_from_file(filepath: str) -> dict:
    with open(filepath, "r") as f:
        raw = f.read()
    return parse_nmap_output(raw)


def save_parsed(parsed: dict, filepath: str):
    with open(filepath, "w") as f:
        json.dump(parsed, f, indent=4)
    print(f"[+] Parsed output saved to {filepath}")


if __name__ == "__main__":
    import os

    scans_dir = "scans"
    files = [f for f in os.listdir(scans_dir) if f.endswith(".txt")]

    if not files:
        print("[!] No scan files found in scans/ folder")
        exit()

    print("\nAvailable scans:")
    for i, f in enumerate(files):
        print(f"  {i+1}. {f}")

    choice = input("\nChoose scan to parse [number]: ").strip()
    selected = files[int(choice) - 1]
    filepath = os.path.join(scans_dir, selected)

    parsed = parse_from_file(filepath)

    json_file = filepath.replace(".txt", ".json")
    save_parsed(parsed, json_file)

    print("\n--- PARSED OUTPUT ---")
    print(json.dumps(parsed, indent=4))