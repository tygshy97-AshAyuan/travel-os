from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preview_builder", ROOT / "tools/build_preview.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PreviewPackageTests(unittest.TestCase):
    def test_reproducible_contents_and_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "preview.zip"
            builder.build(ROOT / "skill/travel-os", output)
            first = output.read_bytes()
            builder.build(ROOT / "skill/travel-os", output)
            self.assertEqual(first, output.read_bytes())
            manifest = json.loads(output.with_suffix(".manifest.json").read_text())
            self.assertEqual(sha256(first).hexdigest(), manifest["sha256"])
            with zipfile.ZipFile(output) as package:
                self.assertEqual(set(builder.FILES), set(package.namelist()))
                for row in manifest["files"]:
                    self.assertEqual(row["sha256"], sha256(package.read(row["path"])).hexdigest())
                self.assertIn("SKILL.md", package.namelist())
                self.assertNotIn("TravelOS-Example.xlsx", package.namelist())

    def test_extracted_package_exports_without_source_tree_dependencies(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            output = folder / "preview.zip"
            builder.build(ROOT / "skill/travel-os", output)
            install = folder / "isolated"
            with zipfile.ZipFile(output) as package:
                package.extractall(install)
            result = subprocess.run([sys.executable, str(install / "scripts/export_trip.py"),
                str(ROOT / "templates/TravelOS-Example.xlsx"), "--output", str(folder / "trip.html"),
                "--locale", "en", "--region", "mainland-cn"], cwd=folder, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            html = (folder / "trip.html").read_text()
            self.assertIn("uri.amap.com/search", html)
            self.assertIn("Your itinerary", html)
            result = subprocess.run([sys.executable, str(install / "scripts/validate_archive.py"),
                str(install / "assets/TravelOS-Template.xlsx")], cwd=folder, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("READY", result.stdout)


if __name__ == "__main__":
    unittest.main()
