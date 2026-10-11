import re
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "templates" / "TravelOS-Template.xlsx"
EXAMPLE_XLSX = ROOT / "templates" / "TravelOS-Example.xlsx"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}


def workbook_rows(path=EXAMPLE_XLSX):
    def column_index(reference):
        letters = re.match(r"[A-Z]+", reference).group()
        index = 0
        for letter in letters:
            index = index * 26 + ord(letter) - ord("A") + 1
        return index - 1

    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall("m:si", NS):
                strings.append("".join(node.text or "" for node in item.iterfind(".//m:t", NS)))

        book = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels.findall("p:Relationship", REL_NS)}
        result = {}
        for sheet in book.findall("m:sheets/m:sheet", NS):
            target = targets[sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
            path = target if target.startswith("xl/") else f"xl/{target}"
            xml = ET.fromstring(archive.read(path))
            rows = []
            for row in xml.findall("m:sheetData/m:row", NS):
                values = []
                for cell in row.findall("m:c", NS):
                    index = column_index(cell.attrib["r"])
                    values.extend([""] * (index - len(values)))
                    value = cell.find("m:v", NS)
                    raw = "" if value is None else value.text or ""
                    if cell.attrib.get("t") == "s" and raw:
                        raw = strings[int(raw)]
                    elif cell.attrib.get("t") == "inlineStr":
                        raw = "".join(node.text or "" for node in cell.iterfind(".//m:t", NS))
                    values.append(raw)
                rows.append(values)
            result[sheet.attrib["name"]] = rows
        return result


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
        cls.rows = workbook_rows()

    def test_required_files(self):
        for relative in ["README.md", "skill/travel-os/SKILL.md", "skill/travel-os/assets/TravelOS-Template.xlsx", "skill/travel-os/references/archive-schema.md", "skill/travel-os/references/versioning.md", "skill/travel-os/references/operating-rules.md", "skill/travel-os/references/planning-rules.md", "templates/TravelOS-Template.xlsx", "templates/TravelOS-Example.xlsx"]:
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

    def test_workbooks_keep_filters_and_dropdowns(self):
        for path in (XLSX, EXAMPLE_XLSX):
            self.assertEqual(8, workbook_feature_count(path, "tableParts"), path)
            self.assertGreaterEqual(workbook_feature_count(path, "dataValidations"), 7, path)

    def test_skill_frontmatter_and_references(self):
        text = (ROOT / "skill/travel-os/SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(text, r"\A---\s+name: travel-os\s+description: .+?\s+---")
        for reference in re.findall(r"\]\((references/[^)]+)\)", text):
            self.assertTrue((ROOT / "skill/travel-os" / reference).is_file(), reference)

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
