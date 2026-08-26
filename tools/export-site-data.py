"""Emit the portfolio site's work.json from profile.toml.

The site lives in a different repository, so the project list was duplicated by
hand and the two drifted. This makes profile.toml the single source: run it,
copy the output into portfolio-site/data/.
"""
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    cfg = tomllib.loads((ROOT / "data" / "profile.toml").read_text())
    work = [{
        "n": f"{i:02d}",
        "title": w["title"],
        "kind": w["kind"],
        "status": w["status"],
        "blurb": w["blurb"],
        "stack": w["stack"],
        "tags": w.get("tags", []),
        "url": w["url"],
    } for i, w in enumerate(cfg["work"], start=1)]

    out = ROOT / "data" / "work.json"
    out.write_text(json.dumps({"work": work}, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {out.relative_to(ROOT)} — {len(work)} projects")
    print("copy it to ../portfolio-site/data/work.json")


if __name__ == "__main__":
    main()
