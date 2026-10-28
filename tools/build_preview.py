#!/usr/bin/env python3
"""Build the local Skill preview from an explicit file list, including uncommitted work.

Releases still use git archive of their exact tag. This command neither installs
the preview nor publishes it. Generated artifacts are reproducible and contain no
trip data, demonstration files, caches or screenshots.
"""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "SKILL.md", "agents/openai.yaml",
    "assets/TravelOS-Template.xlsx", "assets/travel-os.svg",
    "assets/trip-view.html", "assets/trip-view.css", "assets/trip-view.js",
    "scripts/build_map_url.py", "scripts/export_trip.py", "scripts/validate_archive.py",
    "references/archive-schema.md", "references/export-view.md",
    "references/import-rules.md", "references/operating-rules.md",
    "references/planning-rules.md", "references/regional-adaptation.md",
    "references/user-journey.md", "references/versioning.md",
    "references/weather-replanning.md",
)


def build(source, output):
    source, output = Path(source).resolve(), Path(output)
    data, entries = BytesIO(), []
    with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as package:
        for name in sorted(FILES):
            path = source / name
            if not path.resolve().is_relative_to(source):
                raise ValueError(f"Package file resolves outside the Skill: {name}")
            content = path.read_bytes()
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, content)
            entries.append(dict(path=name, bytes=len(content), sha256=sha256(content).hexdigest()))
    content = data.getvalue()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    digest = sha256(content).hexdigest()
    output.with_suffix(".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    output.with_suffix(".manifest.json").write_text(json.dumps(dict(kind="unreleased-local-preview", sha256=digest, files=entries), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "artifacts/Travel-OS-Skill-local-preview.zip")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".zip":
        parser.error("output must be a .zip file")
    entries = build(ROOT / "skill/travel-os", args.output)
    print(f"Built local preview: {args.output} ({len(entries)} files)")


if __name__ == "__main__":
    main()
