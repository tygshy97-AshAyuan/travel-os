"""Export behavior: validated state, privacy, encoding and calendar boundaries."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skill/travel-os/scripts"))
from export_trip import clock, epoch, make_payload, render
from validate_archive import workbook_rows
from build_map_url import build_place_url


def example_rows():
    rows = workbook_rows(ROOT / "templates/TravelOS-Example.xlsx")
    return {sheet: data[:2] + [r for r in data[2:] if any(r)] for sheet, data in rows.items()}


def next_version(rows):
    rows = deepcopy(rows)
    for row in rows["Daily Plan"][2:4]:
        successor = row[:]
        successor[1] = "v0.1.1"
        rows["Daily Plan"].append(successor)
    history = rows["Change Log"][2][:]
    history[0], history[3], history[5] = "v0.1.1", "批准 PR-001", "v0.1.0"
    rows["Change Log"].append(history)
    rows["Travel Overview"][2][7] = "v0.1.1"
    proposal = rows["Proposals"][2]
    proposal[6], proposal[8], proposal[9] = "接受", "负责人接受", "v0.1.1"
    return rows


class ExportTests(unittest.TestCase):
    def test_active_only_and_direct_predecessor_diff(self):
        rows = next_version(example_rows())
        rows["Daily Plan"][5][3:5] = ["15:00", "17:00"]
        p = make_payload(rows)
        self.assertEqual("v0.1.0", p["previous"])
        self.assertEqual(2, len(p["items"]))
        self.assertEqual("15:00", p["items"][1]["start"])
        self.assertEqual(["start", "end"], p["changes"][0]["fields"])
        self.assertEqual("14:00", p["changes"][0]["before"]["start"])
        self.assertEqual([], p["proposals"])

    def test_added_removed_and_execution_only_updates(self):
        rows = next_version(example_rows())
        rows["Daily Plan"][4][11] = "In progress"
        self.assertEqual([], make_payload(rows)["changes"])
        rows["Daily Plan"][5][0] = "I-003"
        self.assertEqual({"added", "removed"}, {c["kind"] for c in make_payload(rows)["changes"]})

    def test_draft_cancelled_and_corrupt_archives_do_not_export(self):
        rows = example_rows()
        rows["Travel Overview"][2][9] = "Cancelled"
        with self.assertRaises(ValueError):
            make_payload(rows)
        rows["Travel Overview"][2][9] = "Draft"
        rows["Travel Overview"][2][7] = ""
        with self.assertRaises(ValueError):
            make_payload(rows)
        rows = example_rows()
        rows["Daily Plan"][2][10] = "MISSING"
        with self.assertRaisesRegex(ValueError, "Invalid archive"):
            make_payload(rows)

    def test_region_independent_of_language_and_city_override(self):
        rows = example_rows()
        for locale in ("en", "zh-CN"):
            self.assertEqual("amap", make_payload(rows, locale=locale, region="mainland-cn")["items"][0]["provider"])
        self.assertEqual("google", make_payload(rows, locale="zh-CN", region="other")["items"][0]["provider"])
        self.assertEqual("", make_payload(rows)["items"][0]["map_url"])
        rows["Daily Plan"][3][6] = "Tokyo"
        p = make_payload(rows, city_regions={"示例城": "mainland-cn", "Tokyo": "other"})
        self.assertEqual(["amap", "google"], [r["provider"] for r in p["items"]])
        with self.assertRaisesRegex(ValueError, "City region keys"):
            make_payload(rows, city_regions={"Typo": "mainland-cn"})

    def test_map_keywords_encoded_without_injection(self):
        for provider in ("amap", "google"):
            link = build_place_url('火车站 & <西口> #2', '杭州', provider)
            self.assertNotIn("<", link)
            parsed = parse_qs(urlparse(link).query)
            self.assertIn('火车站 & <西口> #2', str(parsed))
        with self.assertRaises(ValueError):
            build_place_url(" ")

    def test_companion_requires_allowlist_and_excludes_private_payload(self):
        rows = example_rows()
        with self.assertRaises(ValueError):
            make_payload(rows, audience="companion")
        with self.assertRaises(ValueError):
            make_payload(rows, audience="companion", share_items=["I-001"])
        with self.assertRaises(ValueError):
            make_payload(rows, audience="companion", share_items=["UNKNOWN"])
        rows["Daily Plan"][3][16] = "PRIVATE-NOTE"
        rows["Members"][2][1] = "PRIVATE-MEMBER"
        p = make_payload(rows, audience="companion", share_items=["I-002"])
        self.assertEqual(["I-002"], [r["id"] for r in p["items"]])
        self.assertEqual([], p["changes"] + p["todos"] + p["proposals"])
        self.assertEqual("2030-05-01", p["end"])
        html = render(p)
        for secret in ("PRIVATE-NOTE", "PRIVATE-MEMBER", "B-001", "T-001", "PR-001", "I-001"):
            self.assertNotIn(secret, html)

    def test_untrusted_text_cannot_close_script_or_inject_markup(self):
        rows = example_rows()
        attack = '</script><img src=x onerror=alert(1)>'
        rows["Daily Plan"][3][7] = attack
        rows["Travel Overview"][2][1] = attack
        p = make_payload(rows)
        html = render(p)
        self.assertNotIn(attack, html)
        data = re.search(r'<script type="application/json" id="trip-data">(.*?)</script>', html, re.S).group(1)
        self.assertEqual(attack, json.loads(data)["trip"]["title"])
        self.assertIn("&lt;/script&gt;", html)
        self.assertNotRegex(html, r'\{\{[A-Z_]+\}\}')

    def test_zero_unknown_and_currencies_remain_distinct(self):
        rows = example_rows()
        rows["Daily Plan"][3][12:14] = ["12.50", "JPY"]
        html = render(make_payload(rows))
        self.assertIn("0.00 CNY", html)
        self.assertIn("12.50 JPY", html)
        rows["Daily Plan"][3][12:14] = ["", ""]
        p = make_payload(rows)
        self.assertEqual("", p["items"][1]["cost"])
        self.assertIn("费用: 待核实", render(p))

    def test_dst_ambiguous_and_nonexistent_times_are_not_guessed(self):
        self.assertIsNone(epoch("2030-11-03", "01:30", "America/New_York"))
        self.assertIsNone(epoch("2030-03-10", "02:30", "America/New_York"))
        self.assertIsNotNone(epoch("2030-11-03", "03:30", "America/New_York"))
        self.assertIsNone(epoch("2030-05-01", "", "Asia/Shanghai"))

    def test_overnight_end_uses_next_local_day(self):
        rows = example_rows()
        rows["Daily Plan"][3][3:5] = ["23:00", "01:00"]
        rows["Daily Plan"][3][16] = "[overnight] 次日结束"
        p = make_payload(rows)
        self.assertEqual(2 * 3600 * 1000, p["items"][1]["end_epoch"] - p["items"][1]["start_epoch"])
        self.assertEqual("2030-05-02", p["items"][1]["end_date"])
        self.assertIn("次日 01:00", render(p))
        self.assertIn("next day 01:00", render(make_payload(rows, locale="en")))

    def test_second_precision_and_equal_time_overnight_marker(self):
        self.assertEqual("10:30:59", clock("10:30:59"))
        rows = example_rows()
        rows["Daily Plan"][3][3:5] = ["14:00", "14:00"]
        with self.assertRaises(ValueError):
            make_payload(rows)
        rows["Daily Plan"][3][16] = "[overnight]"
        p = make_payload(rows)
        self.assertEqual(24 * 3600 * 1000, p["items"][1]["end_epoch"] - p["items"][1]["start_epoch"])

    def test_cli_no_workbook_mutation_and_no_overwrite(self):
        workbook = ROOT / "templates/TravelOS-Example.xlsx"
        before = sha256(workbook.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "trip.html"
            cmd = [sys.executable, str(ROOT / "skill/travel-os/scripts/export_trip.py"), str(workbook), "--output", str(output)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stderr)
            first = output.read_bytes()
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(first, output.read_bytes())
            output.unlink()
            cmd[2] = str(ROOT / "templates/TravelOS-Template.xlsx")
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)
            self.assertFalse(output.exists())
        self.assertEqual(before, sha256(workbook.read_bytes()).hexdigest())

    def test_static_content_does_not_require_javascript_or_external_assets(self):
        html = render(make_payload(example_rows()))
        self.assertIn('<section class="day" data-date="2030-05-01">', html)
        self.assertIn("城市步行", html)
        self.assertNotRegex(html, r'<(?:script|link|img)[^>]+(?:src|href)=')
        self.assertIn("connect-src 'none'", html)


if __name__ == "__main__":
    unittest.main()
