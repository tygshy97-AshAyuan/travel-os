import re
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "templates" / "TravelOS-Template.xlsx"
EXAMPLE_XLSX = ROOT / "templates" / "TravelOS-Example.xlsx"
sys.path.insert(0, str(ROOT / "skill" / "travel-os" / "scripts"))
from validate_archive import is_uninitialized_template, validate, validate_rows, workbook_rows
from build_map_url import build_directions_url
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def missing_booking_references(rows):
    overview = rows["Travel Overview"]
    active = overview[2][overview[1].index("Active Version")]
    bookings = {row[0] for row in rows["Bookings"][2:] if row and row[0]}
    return {
        row[10]
        for row in rows["Daily Plan"][2:]
        if len(row) > 10 and row[1] == active and row[10] and row[10] not in bookings
    }


def workbook_feature_count(path, feature):
    with zipfile.ZipFile(path) as archive:
        return sum(
            len(ET.fromstring(archive.read(name)).findall(f"m:{feature}", NS))
            for name in archive.namelist()
            if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name)
        )


class TravelOSContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = workbook_rows(EXAMPLE_XLSX)

    def test_required_files(self):
        for relative in [".github/workflows/release.yml", "README.md", "ROADMAP.md", "CONTRIBUTING.md", "SECURITY.md", "docs/images/travel-overview.png", "docs/images/daily-plan.png", "skill/travel-os/SKILL.md", "skill/travel-os/agents/openai.yaml", "skill/travel-os/assets/travel-os.svg", "skill/travel-os/assets/TravelOS-Template.xlsx", "skill/travel-os/scripts/validate_archive.py", "skill/travel-os/scripts/build_map_url.py", "skill/travel-os/references/archive-schema.md", "skill/travel-os/references/versioning.md", "skill/travel-os/references/operating-rules.md", "skill/travel-os/references/planning-rules.md", "skill/travel-os/references/import-rules.md", "templates/TravelOS-Template.xlsx", "templates/TravelOS-Example.xlsx"]:
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_installed_skill_contains_canonical_template(self):
        self.assertEqual(
            XLSX.read_bytes(),
            (ROOT / "skill/travel-os/assets/TravelOS-Template.xlsx").read_bytes(),
        )

    def test_template_starts_blank(self):
        rows = workbook_rows(XLSX)
        for sheet_rows in rows.values():
            self.assertFalse(any(any(row) for row in sheet_rows[2:]))

    def test_blank_template_is_ready_for_initialization(self):
        self.assertTrue(is_uninitialized_template(workbook_rows(XLSX)))
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "skill/travel-os/scripts/validate_archive.py"),
                str(XLSX),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("READY:", result.stdout)

    def test_populated_archive_is_not_an_uninitialized_template(self):
        self.assertFalse(is_uninitialized_template(self.rows))

    def test_workbooks_keep_filters_and_dropdowns(self):
        for path in (XLSX, EXAMPLE_XLSX):
            self.assertEqual(8, workbook_feature_count(path, "tableParts"), path)
            self.assertGreaterEqual(workbook_feature_count(path, "dataValidations"), 7, path)

    def test_skill_frontmatter_and_references(self):
        text = (ROOT / "skill/travel-os/SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"\A---\s+name: travel-os\s+description: .+?\s+---")
        for reference in re.findall(r"\]\((references/[^)]+)\)", text):
            self.assertTrue((ROOT / "skill/travel-os" / reference).is_file(), reference)

    def test_skill_interface_metadata(self):
        metadata = (ROOT / "skill/travel-os/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Travel OS"', metadata)
        self.assertRegex(metadata, r'short_description: ".{25,64}"')
        self.assertIn("$travel-os", metadata)
        for icon in re.findall(r'icon_(?:small|large): "(\./assets/[^"]+)"', metadata):
            self.assertTrue((ROOT / "skill/travel-os" / icon).is_file(), icon)
        icon_root = ET.parse(ROOT / "skill/travel-os/assets/travel-os.svg").getroot()
        self.assertEqual("0 0 512 512", icon_root.attrib["viewBox"])

    def test_workbook_schema(self):
        required = {"Travel Overview", "Daily Plan", "Bookings", "Checklist", "Preferences", "Change Log", "Members", "Proposals"}
        self.assertTrue(required.issubset(self.rows), required - self.rows.keys())
        self.assertEqual(1, sum(any(row) for row in self.rows["Travel Overview"][2:]), "one workbook must contain exactly one trip row")

    def test_active_version_integrity(self):
        overview = self.rows["Travel Overview"]
        overview_header, trip = overview[1], overview[2]
        active = trip[overview_header.index("Active Version")]
        status = trip[overview_header.index("状态")]
        self.assertTrue(active or status == "Draft")
        if active:
            itinerary = self.rows["Daily Plan"]
            versions = self.rows["Change Log"]
            self.assertIn(active, [row[1] for row in itinerary[2:] if len(row) > 1])
            self.assertEqual(1, sum(1 for row in versions[2:] if row and row[0] == active))

    def test_current_booking_references_exist(self):
        self.assertEqual(set(), missing_booking_references(self.rows))

    def test_missing_booking_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][10] = "B-404"
        self.assertEqual({"B-404"}, missing_booking_references(broken))
        self.assertIn("Missing booking references: B-404", validate_rows(broken))

    def test_example_passes_runtime_validator(self):
        self.assertEqual([], validate(EXAMPLE_XLSX))

    def test_duplicate_ids_are_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"].append(broken["Daily Plan"][2][:])
        self.assertIn(
            "Daily Plan has duplicate version/item IDs: v0.1.0/I-001",
            validate_rows(broken),
        )

    def test_stable_plan_ids_can_be_copied_to_a_new_version(self):
        copied = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        prior = copied["Daily Plan"][2][:]
        prior[1] = "v0.3.0"
        copied["Daily Plan"].append(prior)
        history = copied["Change Log"][2][:]
        history[0] = "v0.3.0"
        history[5] = ""
        copied["Change Log"].insert(2, history)
        self.assertEqual([], validate_rows(copied))

    def test_plan_version_must_exist_in_change_log(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][1] = "v9.9.9"
        self.assertIn(
            "Daily Plan references missing versions: v9.9.9",
            validate_rows(broken),
        )

    def test_out_of_range_plan_date_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][2] = "2040-01-01T00:00:00.000Z"
        self.assertIn(
            "Daily Plan row 3 falls outside the trip date range",
            validate_rows(broken),
        )

    def test_broken_version_and_checklist_links_are_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Change Log"][2][5] = "v9.9.9"
        broken["Checklist"][2][6] = "T-404"
        broken["Checklist"][2][7] = "I-404"
        errors = validate_rows(broken)
        self.assertIn("Change Log row 3 has invalid predecessor v9.9.9", errors)
        self.assertIn("Checklist row 3 references missing dependency T-404", errors)
        self.assertIn("Checklist row 3 references missing related item I-404", errors)

    def test_accepted_proposal_requires_result_version(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Proposals"][2][6] = "已接受"
        self.assertIn(
            "Accepted proposal on row 3 has no valid result version",
            validate_rows(broken),
        )

    def test_invalid_status_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][11] = "Probably"
        self.assertIn(
            "Daily Plan row 3 has invalid 执行状态: Probably",
            validate_rows(broken),
        )

    def test_confirmed_facts_require_evidence(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Bookings"][2][11] = ""
        broken["Daily Plan"][2][14] = ""
        errors = validate_rows(broken)
        self.assertIn(
            "Confirmed booking on row 3 needs source and checked time",
            errors,
        )
        self.assertIn(
            "Ready Daily Plan row 3 needs source and checked time",
            errors,
        )

    def test_owner_and_traveler_count_are_unambiguous(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Members"][3][2] = "Owner"
        broken["Travel Overview"][2][5] = "3"
        errors = validate_rows(broken)
        self.assertIn("Members must contain exactly one Owner; found 2", errors)
        self.assertIn(
            "Travel Overview traveler count 3 does not match 2 Members rows",
            errors,
        )

    def test_preference_member_reference_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Preferences"][2][4] = "M-404"
        self.assertIn(
            "Preferences row 3 references missing member M-404",
            validate_rows(broken),
        )

    def test_map_url_preserves_route_and_mode(self):
        url = build_directions_url(
            "Tokyo Station",
            "Shinjuku Station",
            waypoints=["Ginza", "Shibuya"],
            travel_mode="transit",
        )
        self.assertEqual(
            "https://www.google.com/maps/dir/?api=1&origin=Tokyo+Station&destination=Shinjuku+Station&travelmode=transit&waypoints=Ginza%7CShibuya",
            url,
        )

    def test_map_url_rejects_missing_location(self):
        with self.assertRaisesRegex(ValueError, "origin and destination are required"):
            build_directions_url("", "Shinjuku Station")

    def test_validator_rejects_unsafe_xml(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            path = Path(directory) / "unsafe.xlsx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "xl/workbook.xml",
                    '<!DOCTYPE workbook [<!ENTITY x "unsafe">]><workbook>&x;</workbook>',
                )
            self.assertIn(
                "Unreadable Travel OS archive: xl/workbook.xml contains a disallowed DOCTYPE",
                validate(path),
            )

    def test_member_references_and_owner(self):
        members = self.rows["Members"]
        member_ids = {row[0] for row in members[2:] if row and row[0]}
        roles = {row[2] for row in members[2:] if len(row) > 2}
        self.assertIn("Owner", roles)
        overview = self.rows["Travel Overview"]
        self.assertIn(overview[2][overview[1].index("负责人")], member_ids)
        for sheet_name, indexes in {"Checklist": [3], "Proposals": [1, 7]}.items():
            for row in self.rows[sheet_name][2:]:
                for index in indexes:
                    if len(row) > index and row[index]:
                        self.assertIn(row[index], member_ids)

    def test_no_common_credentials_or_redskill_scope(self):
        secret = re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}")
        for path in ROOT.rglob("*"):
            if path.is_file() and ".git" not in path.parts and ".tmp" not in path.parts:
                if path.suffix == ".xlsx":
                    with zipfile.ZipFile(path) as archive:
                        text = "\n".join(
                            archive.read(name).decode("utf-8", errors="ignore")
                            for name in archive.namelist()
                            if name.endswith(".xml")
                        )
                    self.assertIsNone(secret.search(text), path)
                    self.assertNotIn("RedSkill", text, path)
                    continue
                if path.suffix not in {"", ".md", ".py", ".yml", ".yaml"}:
                    continue
                text = path.read_text(encoding="utf-8")
                if path.name != "test_contract.py":
                    self.assertIsNone(secret.search(text), path)
                if path.name != "test_contract.py":
                    self.assertNotIn("RedSkill", text, path)


if __name__ == "__main__":
    unittest.main()
