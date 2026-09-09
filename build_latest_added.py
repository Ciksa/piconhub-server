#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

CATALOG_DEFAULT = "catalog.json"
OUTPUT_DEFAULT = "latest_added.json"
LATEST_URL = "https://raw.githubusercontent.com/PiconHub-Warder/piconhub-server/main/latest_added.json"

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def git_added_dates(repo):
    """Return {repo_relative_path: ISO-8601 commit date} for files added to Git."""
    cmd = [
        "git", "-C", str(repo), "log",
        "--diff-filter=A",
        "--name-status",
        "--format=@@%aI"
    ]
    p = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8")
    current_date = ""
    result = {}
    # git log is newest -> oldest. Assign every A-path; normally each path is added once.
    for raw in p.stdout.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("@@"):
            current_date = line[2:].strip()
            continue
        parts = line.split("\t")
        if len(parts) >= 2 and parts[0] == "A" and current_date:
            path = parts[-1].replace("\\", "/")
            # Keep the newest add event if a path was deleted/re-added.
            result.setdefault(path, current_date)
    return result

def repo_path_from_url(url):
    if not url:
        return ""
    try:
        path = urlparse(url).path
        marker = "/main/"
        if marker in path:
            return path.split(marker, 1)[1].lstrip("/")
    except Exception:
        pass
    return ""

def manifest_local_path(repo, manifest_url):
    rel = repo_path_from_url(manifest_url)
    if rel:
        p = repo / rel
        if p.exists():
            return p
    name = Path(urlparse(manifest_url).path).name
    p = repo / name
    return p if p.exists() else None

def main():
    repo = Path.cwd()
    catalog_path = Path(sys.argv[1]) if len(sys.argv) > 1 else repo / CATALOG_DEFAULT
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else repo / OUTPUT_DEFAULT

    if not catalog_path.is_absolute():
        catalog_path = repo / catalog_path
    if not output_path.is_absolute():
        output_path = repo / output_path

    if not (repo / ".git").exists():
        raise SystemExit("CHYBA: spusti skript v koreňovom priečinku git repozitára (.git chýba).")
    if not catalog_path.exists():
        raise SystemExit(f"CHYBA: nenájdený {catalog_path}")

    catalog = load_json(catalog_path)
    added_dates = git_added_dates(repo)

    rows = []
    seen = set()

    for pkg in catalog.get("packages", []):
        if not isinstance(pkg, dict):
            continue
        manifest_url = str(pkg.get("manifest") or "").strip()
        manifest_path = manifest_local_path(repo, manifest_url)
        if not manifest_path:
            print(f"VAROVANIE: lokálny manifest nenájdený pre {manifest_url}")
            continue

        manifest = load_json(manifest_path)
        package_id = str(pkg.get("id") or manifest.get("package") or "").strip()
        provider = str(pkg.get("name") or manifest.get("name") or package_id).strip()

        for item in manifest.get("picons", []):
            if not isinstance(item, dict):
                continue

            name = str(item.get("name") or "").strip()
            filename = str(item.get("file") or "").strip()
            url = str(item.get("url") or "").strip()
            service_reference = str(item.get("service_reference") or "").strip()
            sha256 = str(item.get("sha256") or "").strip()

            # Prefer the actual repository path encoded by the raw GitHub URL.
            repo_rel = repo_path_from_url(url)
            candidates = []
            if repo_rel:
                candidates.append(repo_rel)
            if filename:
                candidates.append("picons/" + Path(filename).name)

            added_at = ""
            source_path = ""
            for candidate in candidates:
                candidate = candidate.replace("\\", "/")
                if candidate in added_dates:
                    added_at = added_dates[candidate]
                    source_path = candidate
                    break

            # Do not invent a date. If Git cannot prove when it was added, skip it.
            if not added_at:
                continue

            key = (package_id, filename, service_reference, url)
            if key in seen:
                continue
            seen.add(key)

            rows.append({
                "name": name or Path(filename).stem,
                "picon": filename or Path(repo_rel).name,
                "file": filename or Path(repo_rel).name,
                "added_at": added_at,
                "package": package_id,
                "provider": provider,
                "service_reference": service_reference,
                "sha256": sha256,
                "url": url,
                "source_path": source_path
            })

    rows.sort(key=lambda x: x.get("added_at", ""), reverse=True)

    payload = {
        "schema": 1,
        "generated_from": "git-add-history",
        "latest_added": rows
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Preserve catalog and update only latest_added_url.
    backup_path = catalog_path.with_suffix(catalog_path.suffix + ".before-latest.bak")
    backup_path.write_text(catalog_path.read_text(encoding="utf-8"), encoding="utf-8")
    catalog["latest_added_url"] = LATEST_URL
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"OK: vytvorené {output_path.name}")
    print(f"OK: položiek s reálnym Git dátumom pridania: {len(rows)}")
    print(f"OK: catalog.json doplnený o latest_added_url")
    print(f"Backup: {backup_path.name}")
    if rows:
        print("\nTOP 5 najnovších:")
        for row in rows[:5]:
            print(f"  {row['added_at']}  |  {row['name']}  |  {row['picon']}")
    else:
        print("\nVAROVANIE: nenašla sa žiadna položka s doložiteľným Git dátumom pridania.")

if __name__ == "__main__":
    main()
