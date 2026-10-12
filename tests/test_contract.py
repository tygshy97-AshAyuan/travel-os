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
        for relative in [".github/workflows/release.yml", "README.md", "ROADMAP.md", "CONTRIBUTING.md", "SECURITY.md", "docs/client-validation.md", "docs/images/travel-overview.png", "docs/images/daily-plan.png", "skill/travel-os/SKILL.md", "skill/travel-os/agents/openai.yaml", "skill/travel-os/assets/travel-os.svg", "skill/travel-os/assets/TravelOS-Template.xlsx", "skill/travel-os/scripts/validate_archive.py", "skill/travel-os/scripts/build_map_url.py", "skill/travel-os/references/archive-schema.md", "skill/travel-os/references/versioning.md", "skill/travel-os/references/operating-rules.md", "skill/travel-os/references/planning-rules.md", "skill/travel-os/references/import-rules.md", "skill/travel-os/references/weather-replanning.md", "templates/TravelOS-Template.xlsx", "templates/TravelOS-Example.xlsx"]:
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

    def test_skill_markdown_is_ascii_for_legacy_windows_validators(self):
        (ROOT / "skill/travel-os/SKILL.md").read_bytes().decode("ascii")

    def test_skill_interface_metadata(self):
        metadata = (ROOT / "skill/travel-os/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Travel OS"', metadata)
        self.assertRegex(metadata, r'short_description: ".{25,64}"')
        self.assertIn("$travel-os", metadata)
        for icon in re.findall(r'icon_(?:small|large): "(\./assets/[^"]+)"', metadata):
            self.assertTrue((ROOT / "skill/travel-os" / icon).is_file(), icon)
        icon_root = ET.parse(ROOT / "skill/travel-os/assets/travel-os.svg").getroot()
        self.assertEqual("0 0 512 512", icon_root.attrib["viewBox"])

    def test_weather_replanning_contract(self):
        rules = (ROOT / "skill/travel-os/references/weather-replanning.md").read_text(encoding="utf-8")
        for requirement in (
            "forecast window",
            "freeze completed",
            "confirmed bookings",
            "Owner-resolved proposal",
            "update Active Version last",
            "source and checked time",
        ):
            self.assertIn(requirement, rules)

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

    def test_version_labels_follow_the_documented_format(self):
        for label, expected_error in (
            ("latest", "Change Log has invalid version labels: latest"),
            ("v0.1.0-20300401T020000Z", None),
        ):
            candidate = {
                name: [row[:] for row in rows] for name, rows in self.rows.items()
            }
            overview_header = candidate["Travel Overview"][1]
            candidate["Travel Overview"][2][
                overview_header.index("Active Version")
            ] = label
            candidate["Change Log"][2][0] = label
            for row in candidate["Daily Plan"][2:]:
                if row and row[0]:
                    row[1] = label
            errors = validate_rows(candidate)
            if expected_error:
                self.assertIn(expected_error, errors)
            else:
                self.assertFalse(
                    any("invalid version labels" in error for error in errors)
                )

    def test_draft_cannot_claim_an_active_version(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        overview_header = broken["Travel Overview"][1]
        trip = broken["Travel Overview"][2]
        trip[overview_header.index("状态")] = "Draft"
        self.assertIn(
            "Draft trip must not have an Active Version",
            validate_rows(broken),
        )

    def test_current_booking_references_exist(self):
        self.assertEqual(set(), missing_booking_references(self.rows))

    def test_missing_booking_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][10] = "B-404"
        self.assertEqual({"B-404"}, missing_booking_references(broken))
        self.assertIn("Missing booking references: B-404", validate_rows(broken))

    def test_example_passes_runtime_validator(self):
        self.assertEqual([], validate(EXAMPLE_XLSX))

    def test_operational_rows_require_minimum_fields(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        overview_header = broken["Travel Overview"][1]
        trip = broken["Travel Overview"][2]
        for field in ("旅行标题", "目的地", "人数", "旅行阶段"):
            trip[overview_header.index(field)] = ""
        booking = broken["Bookings"][2]
        booking[1] = ""
        booking[2] = ""
        booking[6] = ""
        checklist = broken["Checklist"][2]
        checklist[1] = ""
        checklist[2] = ""
        checklist[3] = ""
        checklist[4] = ""
        checklist[5] = ""
        errors = validate_rows(broken)
        for field in ("旅行标题", "目的地", "人数", "旅行阶段"):
            self.assertIn(f"Travel Overview is missing {field}", errors)
        self.assertIn("Bookings row 3 is missing: 类别, 供应方, 状态", errors)
        self.assertIn(
            "Checklist row 3 is missing: 类别, 任务, 负责人, 截止日期, 状态",
            errors,
        )

        invalid_date = {
            name: [row[:] for row in rows] for name, rows in self.rows.items()
        }
        invalid_date["Checklist"][2][4] = "not-a-date"
        errors = validate_rows(invalid_date)
        self.assertIn("Checklist row 3 has an invalid due date", errors)

    def test_completed_trip_requires_closed_execution_state(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        overview_header = broken["Travel Overview"][1]
        trip = broken["Travel Overview"][2]
        trip[overview_header.index("状态")] = "Completed"
        errors = validate_rows(broken)
        self.assertIn("Completed trip must be in 旅行后 phase", errors)
        self.assertIn(
            "Completed trip has unfinished active items: I-001, I-002",
            errors,
        )
        self.assertIn("Completed trip has open checklist tasks: T-001", errors)

    def test_duplicate_ids_are_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"].append(broken["Daily Plan"][2][:])
        self.assertIn(
            "Daily Plan has duplicate version/item IDs: v0.1.0/I-001",
            validate_rows(broken),
        )

    def test_stable_plan_ids_can_be_copied_to_a_new_version(self):
        copied = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        for row in copied["Daily Plan"][2:4]:
            successor = row[:]
            successor[1] = "v0.1.1"
            copied["Daily Plan"].append(successor)
        history = copied["Change Log"][2][:]
        history[0] = "v0.1.1"
        history[3] = "批准 PR-001"
        history[5] = "v0.1.0"
        copied["Change Log"].append(history)
        overview_header = copied["Travel Overview"][1]
        copied["Travel Overview"][2][overview_header.index("Active Version")] = "v0.1.1"
        proposal = copied["Proposals"][2]
        proposal[6] = "接受"
        proposal[8] = "负责人接受"
        proposal[9] = "v0.1.1"
        self.assertEqual([], validate_rows(copied))

    def test_versions_require_owner_approval(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        for row in broken["Daily Plan"][2:4]:
            successor = row[:]
            successor[1] = "v0.1.1"
            broken["Daily Plan"].append(successor)
        history = broken["Change Log"][2][:]
        history[0] = "v0.1.1"
        history[5] = "v0.1.0"
        broken["Change Log"].append(history)
        overview_header = broken["Travel Overview"][1]
        broken["Travel Overview"][2][overview_header.index("Active Version")] = "v0.1.1"
        self.assertIn(
            "Version v0.1.1 has no accepted Owner proposal",
            validate_rows(broken),
        )

        broken["Members"][3][2] = "Editor"
        broken["Change Log"][2][2] = "M-002"
        self.assertIn(
            "Root version must be authored by trip Owner M-001",
            validate_rows(broken),
        )

    def test_change_log_requires_auditable_fields(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        history = broken["Change Log"][2]
        history[1] = ""
        history[2] = ""
        history[3] = ""
        history[4] = ""
        errors = validate_rows(broken)
        self.assertIn(
            "Change Log row 3 is missing: 创建时间, 作者, 原因, 变更摘要",
            errors,
        )

        invalid_time = {
            name: [row[:] for row in rows] for name, rows in self.rows.items()
        }
        invalid_time["Change Log"][2][1] = "not-a-time"
        self.assertIn(
            "Change Log row 3 has an invalid creation time",
            validate_rows(invalid_time),
        )

    def test_version_history_has_one_root_and_latest_active_version(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        history = broken["Change Log"][2][:]
        history[0] = "v0.1.1"
        history[5] = ""
        broken["Change Log"].append(history)
        errors = validate_rows(broken)
        self.assertIn(
            "Change Log must contain exactly one root version; found 2",
            errors,
        )
        self.assertIn(
            "Active Version v0.1.0 is not latest Change Log version v0.1.1",
            errors,
        )

    def test_plan_version_must_exist_in_change_log(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][1] = "v9.9.9"
        self.assertIn(
            "Daily Plan references missing versions: v9.9.9",
            validate_rows(broken),
        )

    def test_every_version_has_a_plan_snapshot(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        prior = broken["Change Log"][2][:]
        prior[0] = "v0.0.9"
        prior[5] = ""
        broken["Change Log"].insert(2, prior)
        current = broken["Change Log"][3]
        current[3] = "批准 PR-001"
        current[5] = "v0.0.9"
        proposal = broken["Proposals"][2]
        proposal[6] = "接受"
        proposal[7] = "M-001"
        proposal[8] = "负责人接受"
        proposal[9] = "v0.1.0"
        self.assertIn(
            "Change Log versions have no Daily Plan snapshot: v0.0.9",
            validate_rows(broken),
        )

    def test_out_of_range_plan_date_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][2] = "2040-01-01T00:00:00.000Z"
        self.assertIn(
            "Daily Plan row 3 falls outside the trip date range",
            validate_rows(broken),
        )

    def test_historical_plan_date_is_validated(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        prior_plan = broken["Daily Plan"][2][:]
        prior_plan[1] = "v0.0.9"
        prior_plan[2] = "not-a-date"
        row_number = len(broken["Daily Plan"]) + 1
        broken["Daily Plan"].append(prior_plan)
        prior_history = broken["Change Log"][2][:]
        prior_history[0] = "v0.0.9"
        prior_history[5] = ""
        broken["Change Log"].insert(2, prior_history)
        broken["Change Log"][3][5] = "v0.0.9"
        self.assertIn(
            f"Daily Plan row {row_number} has an invalid date",
            validate_rows(broken),
        )

    def test_daily_plan_time_range_is_validated(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][3] = "11:00"
        broken["Daily Plan"][2][4] = "10:00"
        self.assertIn(
            "Daily Plan row 3 ends before it starts without an overnight marker",
            validate_rows(broken),
        )

    def test_historical_plan_time_ranges_are_validated(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        invalid_time = broken["Daily Plan"][2][:]
        invalid_time[0] = "I-H1"
        invalid_time[1] = "v0.0.9"
        invalid_time[3] = "25:00"
        invalid_time[4] = "26:00"
        missing_end = invalid_time[:]
        missing_end[0] = "I-H2"
        missing_end[3] = "10:00"
        missing_end[4] = ""
        first_row = len(broken["Daily Plan"]) + 1
        broken["Daily Plan"].extend((invalid_time, missing_end))
        prior_history = broken["Change Log"][2][:]
        prior_history[0] = "v0.0.9"
        prior_history[5] = ""
        broken["Change Log"].insert(2, prior_history)
        broken["Change Log"][3][5] = "v0.0.9"
        errors = validate_rows(broken)
        self.assertIn(
            f"Daily Plan row {first_row} has an invalid time range",
            errors,
        )
        self.assertIn(
            f"Daily Plan row {first_row + 1} needs both start and end times",
            errors,
        )

    def test_daily_plan_overlap_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][3][3] = "10:30"
        broken["Daily Plan"][3][4] = "11:30"
        self.assertIn(
            "Active Daily Plan items I-001 and I-002 overlap",
            validate_rows(broken),
        )

    def test_overnight_daily_plan_is_allowed(self):
        overnight = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        overnight["Daily Plan"][2][3] = "23:00"
        overnight["Daily Plan"][2][4] = "01:00"
        overnight["Daily Plan"][2][16] = "[overnight]"
        self.assertFalse(
            any("Daily Plan row 3 ends before" in error for error in validate_rows(overnight))
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

    def test_checklist_dependency_cycle_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        second_task = broken["Checklist"][2][:]
        second_task[0] = "T-002"
        second_task[6] = "T-001"
        broken["Checklist"][2][6] = "T-002"
        broken["Checklist"].append(second_task)
        self.assertIn(
            "Checklist dependency cycle: T-001 -> T-002 -> T-001",
            validate_rows(broken),
        )

    def test_accepted_proposal_requires_result_version(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Proposals"][2][6] = "接受"
        self.assertIn(
            "Accepted proposal on row 3 has no valid result version",
            validate_rows(broken),
        )

    def test_accepted_proposal_is_traced_in_result_version(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        proposal = broken["Proposals"][2]
        proposal[6] = "接受"
        proposal[8] = "负责人接受"
        proposal[9] = "v0.1.0"
        self.assertIn(
            "Accepted proposal PR-001 is not referenced by result version v0.1.0",
            validate_rows(broken),
        )

    def test_resolved_proposal_requires_owner_and_resolution(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Proposals"][2][6] = "拒绝"
        broken["Proposals"][2][7] = "M-002"
        errors = validate_rows(broken)
        self.assertIn(
            "Resolved proposal on row 3 must be decided by trip Owner M-001",
            errors,
        )
        self.assertIn(
            "Resolved proposal on row 3 needs a resolution",
            errors,
        )

    def test_proposal_lifecycle_is_complete(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        proposal = broken["Proposals"][2]
        proposal[2] = "not-a-date"
        proposal[3] = ""
        proposal[4] = ""
        proposal[9] = "v0.1.0"
        errors = validate_rows(broken)
        self.assertIn(
            "Proposals row 3 is missing: 影响项目或日期, 提案",
            errors,
        )
        self.assertIn("Proposals row 3 has an invalid date", errors)
        self.assertIn(
            "Non-accepted proposal PR-001 must not name a result version",
            errors,
        )

        overview_header = broken["Travel Overview"][1]
        trip = broken["Travel Overview"][2]
        trip[overview_header.index("状态")] = "Completed"
        self.assertIn(
            "Completed trip has unresolved proposals: PR-001",
            validate_rows(broken),
        )
    def test_invalid_status_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][11] = "Probably"
        self.assertIn(
            "Daily Plan row 3 has invalid 执行状态: Probably",
            validate_rows(broken),
        )

    def test_daily_plan_requires_executable_fields(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][1] = ""
        broken["Daily Plan"][2][5] = ""
        self.assertIn(
            "Daily Plan row 3 is missing: 版本, 时区",
            validate_rows(broken),
        )

    def test_time_zones_are_valid_iana_names(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        overview_header = broken["Travel Overview"][1]
        broken["Travel Overview"][2][overview_header.index("主时区")] = "China time"
        broken["Daily Plan"][2][5] = "Asia Shanghai"
        errors = validate_rows(broken)
        self.assertIn("Travel Overview has an invalid home time zone: China time", errors)
        self.assertIn("Daily Plan row 3 has an invalid time zone: Asia Shanghai", errors)

    def test_new_version_preserves_completed_execution_state(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        prior_plan = broken["Daily Plan"][2][:]
        prior_plan[1] = "v0.0.9"
        prior_plan[11] = "Done"
        broken["Daily Plan"].append(prior_plan)
        prior_history = broken["Change Log"][2][:]
        prior_history[0] = "v0.0.9"
        prior_history[5] = ""
        broken["Change Log"].insert(2, prior_history)
        broken["Change Log"][3][5] = "v0.0.9"
        self.assertIn(
            "Version v0.1.0 regresses completed item I-001 from Done to Ready",
            validate_rows(broken),
        )

    def test_new_version_keeps_completed_items(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        prior_plan = broken["Daily Plan"][2][:]
        prior_plan[1] = "v0.0.9"
        prior_plan[11] = "Done"
        broken["Daily Plan"].append(prior_plan)
        broken["Daily Plan"].pop(2)
        prior_history = broken["Change Log"][2][:]
        prior_history[0] = "v0.0.9"
        prior_history[5] = ""
        broken["Change Log"].insert(2, prior_history)
        broken["Change Log"][3][5] = "v0.0.9"
        self.assertIn(
            "Version v0.1.0 drops completed item I-001 from v0.0.9",
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

    def test_confirmed_fact_checked_times_are_valid(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Bookings"][2][12] = "not-a-time"
        broken["Daily Plan"][2][15] = "not-a-time"
        errors = validate_rows(broken)
        self.assertIn("Bookings row 3 has an invalid checked time", errors)
        self.assertIn("Ready Daily Plan row 3 has an invalid checked time", errors)

    def test_historical_ready_plan_keeps_fact_evidence(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        prior_plan = broken["Daily Plan"][2][:]
        prior_plan[0] = "I-H1"
        prior_plan[1] = "v0.0.9"
        prior_plan[14] = ""
        prior_plan[15] = ""
        row_number = len(broken["Daily Plan"]) + 1
        broken["Daily Plan"].append(prior_plan)
        prior_history = broken["Change Log"][2][:]
        prior_history[0] = "v0.0.9"
        prior_history[5] = ""
        broken["Change Log"].insert(2, prior_history)
        broken["Change Log"][3][5] = "v0.0.9"
        self.assertIn(
            f"Ready Daily Plan row {row_number} needs source and checked time",
            validate_rows(broken),
        )

    def test_costs_require_non_negative_amounts_and_currencies(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        plan = broken["Daily Plan"][2]
        plan[12] = "100"
        plan[13] = ""
        booking = broken["Bookings"][2]
        booking[8] = "-1"
        booking[9] = "yuan"
        errors = validate_rows(broken)
        self.assertIn("Daily Plan row 3 needs both cost and currency", errors)
        self.assertIn("Bookings row 3 has an invalid amount", errors)
        self.assertIn("Bookings row 3 has an invalid currency: yuan", errors)

    def test_ready_plan_requires_usable_booking(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Bookings"][2][6] = "已取消"
        errors = validate_rows(broken)
        self.assertIn(
            "Daily Plan row 3 references cancelled booking B-001",
            errors,
        )
        self.assertIn(
            "Ready Daily Plan row 3 requires confirmed booking B-001",
            errors,
        )

    def test_booking_time_range_is_validated(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Bookings"][2][3] = "2030-05-02T12:00:00Z"
        broken["Bookings"][2][4] = "2030-05-02T10:00:00Z"
        self.assertIn(
            "Bookings row 3 ends before it starts",
            validate_rows(broken),
        )

    def test_booking_time_zones_cannot_be_mixed(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Bookings"][2][3] = "2030-05-02T10:00:00Z"
        broken["Bookings"][2][4] = "2030-05-02T12:00:00"
        self.assertIn(
            "Bookings row 3 mixes zoned and unzoned times",
            validate_rows(broken),
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

    def test_traveler_count_is_a_positive_whole_number(self):
        for value in ("2.5", "0", "-1", "two"):
            with self.subTest(value=value):
                broken = {
                    name: [row[:] for row in rows]
                    for name, rows in self.rows.items()
                }
                broken["Travel Overview"][2][5] = value
                self.assertIn(
                    f"Travel Overview has an invalid traveler count: {value}",
                    validate_rows(broken),
                )

    def test_preference_member_reference_is_detected(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Preferences"][2][4] = "M-404"
        self.assertIn(
            "Preferences row 3 references missing member M-404",
            validate_rows(broken),
        )

    def test_filled_rows_require_an_id(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Daily Plan"][2][0] = ""
        self.assertIn(
            "Daily Plan row 3 is missing 项目ID",
            validate_rows(broken),
        )

    def test_preferences_require_evidence_and_confidence(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Preferences"][2][6] = ""
        broken["Preferences"][2][7] = ""
        self.assertIn(
            "Preferences row 3 is missing: 证据, 置信度",
            validate_rows(broken),
        )

    def test_preferences_have_a_valid_lifecycle(self):
        missing = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        missing["Preferences"][2][8] = ""
        self.assertIn(
            "Preferences row 3 is missing: 生效日期",
            validate_rows(missing),
        )

        invalid = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        invalid["Preferences"][2][8] = "not-a-date"
        self.assertIn(
            "Preferences row 3 has an invalid effective date",
            validate_rows(invalid),
        )

        reversed_range = {
            name: [row[:] for row in rows] for name, rows in self.rows.items()
        }
        reversed_range["Preferences"][2][9] = "2030-04-30"
        self.assertIn(
            "Preferences row 3 expires before its effective date",
            validate_rows(reversed_range),
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

    def test_validator_rejects_workbook_formulas(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "tests") as directory:
            path = Path(directory) / "formula.xlsx"
            with zipfile.ZipFile(EXAMPLE_XLSX) as source, zipfile.ZipFile(path, "w") as target:
                for info in source.infolist():
                    data = source.read(info)
                    if info.filename == "xl/worksheets/sheet1.xml":
                        root = ET.fromstring(data)
                        cell = root.find(".//m:c[@r='L3']", NS)
                        ET.SubElement(cell, f"{{{NS['m']}}}f").text = 'WEBSERVICE("https://example.invalid")'
                        data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                    target.writestr(info, data)
            self.assertIn(
                "Unreadable Travel OS archive: Travel Overview contains formulas; Travel OS cells must be literal values",
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

    def test_viewer_cannot_change_or_own_trip_work(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Members"][3][2] = "Viewer"
        broken["Checklist"][2][3] = "M-002"
        broken["Proposals"][2][1] = "M-002"
        broken["Change Log"][2][2] = "M-002"
        errors = validate_rows(broken)
        self.assertIn(
            "Checklist row 3 assignee M-002 with role Viewer cannot own tasks",
            errors,
        )
        self.assertIn(
            "Proposals row 3 submitter M-002 with role Viewer cannot submit proposals",
            errors,
        )
        self.assertIn(
            "Change Log row 3 author M-002 must be Owner or Editor",
            errors,
        )

    def test_members_require_display_name_and_role(self):
        broken = {name: [row[:] for row in rows] for name, rows in self.rows.items()}
        broken["Members"][3][1] = ""
        broken["Members"][3][2] = ""
        self.assertIn(
            "Members row 4 is missing: 显示名, 角色",
            validate_rows(broken),
        )

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
