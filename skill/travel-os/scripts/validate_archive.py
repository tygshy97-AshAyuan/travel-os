#!/usr/bin/env python3
"""Validate a Travel OS workbook without third-party packages."""

import argparse
from datetime import datetime, timedelta
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL_NS = {"p": "http://schemas.openxmlformats.org/package/2006/relationships"}
REQUIRED_SHEETS = {
    "Travel Overview",
    "Daily Plan",
    "Bookings",
    "Checklist",
    "Preferences",
    "Change Log",
    "Members",
    "Proposals",
}
EXPECTED_HEADERS = {
    "Travel Overview": ["Trip ID", "旅行标题", "目的地", "开始日期", "结束日期", "人数", "负责人", "Active Version", "旅行阶段", "状态", "主时区", "备注"],
    "Daily Plan": ["项目ID", "版本", "日期", "开始", "结束", "时区", "城市", "活动", "地点", "交通", "预订ID", "执行状态", "费用", "币种", "来源", "核验时间", "备注"],
    "Bookings": ["预订ID", "类别", "供应方", "开始时间", "结束时间", "城市", "状态", "可退", "金额", "币种", "凭证位置", "来源", "核验时间", "备注"],
    "Checklist": ["任务ID", "类别", "任务", "负责人", "截止日期", "状态", "依赖", "关联ID", "备注"],
    "Preferences": ["偏好ID", "范围", "类别", "优先级", "适用人", "偏好或约束", "证据", "置信度", "生效日期", "失效日期", "备注"],
    "Change Log": ["版本", "创建时间", "作者", "原因", "变更摘要", "上一版本", "档案哈希"],
    "Members": ["成员ID", "显示名", "角色", "同行关系", "本次需求", "权限", "备注"],
    "Proposals": ["提案ID", "提交人", "日期", "影响项目或日期", "提案", "原因", "状态", "决策人", "处理结果", "结果版本"],
}
MAX_ARCHIVE_ENTRIES = 1000
MAX_UNCOMPRESSED_BYTES = 64 * 1024 * 1024
MAX_XML_BYTES = 8 * 1024 * 1024
ARCHIVE_ERRORS = (
    KeyError,
    IndexError,
    OSError,
    ValueError,
    ET.ParseError,
    zipfile.BadZipFile,
)
ENUM_FIELDS = {
    "Travel Overview": {
        8: {"行前规划", "旅行中", "旅行后"},
        9: {"Draft", "Active", "Completed", "Cancelled"},
    },
    "Daily Plan": {
        11: {"Planned", "Ready", "In progress", "Done", "Skipped", "Blocked"},
    },
    "Bookings": {6: {"待确认", "已确认", "已取消", "已完成"}},
    "Checklist": {5: {"待处理", "进行中", "已完成", "已取消", "阻塞"}},
    "Preferences": {
        1: {"长期", "本次旅行"},
        3: {"硬约束", "强偏好", "一般偏好", "可选"},
    },
    "Members": {2: {"Owner", "Editor", "Member", "Viewer"}},
    "Proposals": {6: {"待处理", "接受", "拒绝", "需澄清"}},
}


def _column_index(reference):
    letters = re.match(r"[A-Z]+", reference).group()
    index = 0
    for letter in letters:
        index = index * 26 + ord(letter) - ord("A") + 1
    return index - 1


def _xml_root(archive, name):
    info = archive.getinfo(name)
    if info.file_size > MAX_XML_BYTES:
        raise ValueError(f"{name} exceeds the XML size limit")
    data = archive.read(info)
    if b"<!DOCTYPE" in data.upper():
        raise ValueError(f"{name} contains a disallowed DOCTYPE")
    return ET.fromstring(data)


def workbook_rows(path):
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > MAX_ARCHIVE_ENTRIES:
            raise ValueError("workbook contains too many ZIP entries")
        if sum(entry.file_size for entry in entries) > MAX_UNCOMPRESSED_BYTES:
            raise ValueError("workbook exceeds the uncompressed size limit")

        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = _xml_root(archive, "xl/sharedStrings.xml")
            strings = [
                "".join(node.text or "" for node in item.iterfind(".//m:t", NS))
                for item in root.findall("m:si", NS)
            ]

        book = _xml_root(archive, "xl/workbook.xml")
        rels = _xml_root(archive, "xl/_rels/workbook.xml.rels")
        targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("p:Relationship", REL_NS)
        }
        result = {}
        for sheet in book.findall("m:sheets/m:sheet", NS):
            target = targets[sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
            xml = _xml_root(
                archive,
                target if target.startswith("xl/") else f"xl/{target}",
            )
            rows = []
            for row in xml.findall("m:sheetData/m:row", NS):
                values = []
                for cell in row.findall("m:c", NS):
                    index = _column_index(cell.attrib["r"])
                    values.extend([""] * (index - len(values)))
                    value = cell.find("m:v", NS)
                    raw = "" if value is None else value.text or ""
                    if cell.attrib.get("t") == "s" and raw:
                        raw = strings[int(raw)]
                    elif cell.attrib.get("t") == "inlineStr":
                        raw = "".join(
                            node.text or "" for node in cell.iterfind(".//m:t", NS)
                        )
                    values.append(raw)
                rows.append(values)
            result[sheet.attrib["name"]] = rows
        return result


def _date(value):
    if not value:
        return None
    try:
        if re.fullmatch(r"\d+(?:\.\d+)?", value):
            return (datetime(1899, 12, 30) + timedelta(days=float(value))).date()
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (TypeError, ValueError, OverflowError):
        return None


def validate_rows(rows):
    errors = []
    missing = REQUIRED_SHEETS - rows.keys()
    if missing:
        return [f"Missing sheets: {', '.join(sorted(missing))}"]

    for sheet_name, expected in EXPECTED_HEADERS.items():
        actual = rows[sheet_name][1][:len(expected)] if len(rows[sheet_name]) > 1 else []
        if actual != expected:
            errors.append(f"{sheet_name} headers do not match the Travel OS schema")

    for sheet_name, fields in ENUM_FIELDS.items():
        for row_number, row in enumerate(rows[sheet_name][2:], start=3):
            for index, allowed in fields.items():
                value = row[index] if len(row) > index else ""
                if value and value not in allowed:
                    errors.append(
                        f"{sheet_name} row {row_number} has invalid {EXPECTED_HEADERS[sheet_name][index]}: {value}"
                    )

    for sheet_name in REQUIRED_SHEETS - {"Travel Overview", "Daily Plan"}:
        identifiers = [row[0] for row in rows[sheet_name][2:] if row and row[0]]
        duplicates = sorted({value for value in identifiers if identifiers.count(value) > 1})
        if duplicates:
            errors.append(f"{sheet_name} has duplicate IDs: {', '.join(duplicates)}")

    plan_keys = [
        (row[1], row[0])
        for row in rows["Daily Plan"][2:]
        if len(row) > 1 and row[0] and row[1]
    ]
    duplicate_plan_keys = sorted(
        {key for key in plan_keys if plan_keys.count(key) > 1}
    )
    if duplicate_plan_keys:
        errors.append(
            "Daily Plan has duplicate version/item IDs: "
            + ", ".join(f"{version}/{item}" for version, item in duplicate_plan_keys)
        )

    trips = [row for row in rows["Travel Overview"][2:] if any(row)]
    if len(trips) != 1:
        return [f"Travel Overview must contain exactly one trip row; found {len(trips)}"]

    overview_header = rows["Travel Overview"][1]
    trip = trips[0]
    for field in ("Trip ID", "开始日期", "结束日期", "负责人", "状态", "主时区"):
        if not trip[overview_header.index(field)]:
            errors.append(f"Travel Overview is missing {field}")

    active = trip[overview_header.index("Active Version")]
    status = trip[overview_header.index("状态")]
    if status in {"Active", "Completed"} and not active:
        errors.append(f"{status} trip has no Active Version")
    start = _date(trip[overview_header.index("开始日期")])
    end = _date(trip[overview_header.index("结束日期")])
    if not start or not end or start > end:
        errors.append("Travel Overview has an invalid date range")

    if active:
        active_rows = [
            row for row in rows["Daily Plan"][2:]
            if len(row) > 1 and row[1] == active
        ]
        if not active_rows:
            errors.append(f"Active Version {active} has no Daily Plan rows")
        version_rows = [
            row for row in rows["Change Log"][2:] if row and row[0] == active
        ]
        if len(version_rows) != 1:
            errors.append(
                f"Active Version {active} must have exactly one Change Log row; found {len(version_rows)}"
            )

        booking_ids = {
            row[0] for row in rows["Bookings"][2:] if row and row[0]
        }
        missing_bookings = {
            row[10]
            for row in active_rows
            if len(row) > 10 and row[10] and row[10] not in booking_ids
        }
        if missing_bookings:
            errors.append(
                f"Missing booking references: {', '.join(sorted(missing_bookings))}"
            )

        for row_number, row in enumerate(active_rows, start=3):
            if len(row) > 11 and row[11] == "Ready":
                if len(row) <= 15 or not row[14] or not row[15]:
                    errors.append(
                        f"Ready Daily Plan row {row_number} needs source and checked time"
                    )

        if start and end and start <= end:
            for row_number, row in enumerate(active_rows, start=3):
                day = _date(row[2] if len(row) > 2 else "")
                note = row[16].lower() if len(row) > 16 else ""
                outside_marker = any(
                    marker in note
                    for marker in ("[pre-trip]", "[post-trip]", "行前", "行后")
                )
                if not day:
                    errors.append(f"Daily Plan row {row_number} has an invalid date")
                elif not outside_marker and not start <= day <= end:
                    errors.append(
                        f"Daily Plan row {row_number} falls outside the trip date range"
                    )

    members = rows["Members"]
    member_rows = [row for row in members[2:] if row and row[0]]
    member_ids = {row[0] for row in member_rows}
    owners = [row[0] for row in member_rows if len(row) > 2 and row[2] == "Owner"]
    if len(owners) != 1:
        errors.append(f"Members must contain exactly one Owner; found {len(owners)}")
    owner = trip[overview_header.index("负责人")]
    if owner and owner not in member_ids:
        errors.append(f"Trip owner {owner} is missing from Members")
    elif owners and owner != owners[0]:
        errors.append(f"Trip owner {owner} does not match Members Owner {owners[0]}")

    travelers = trip[overview_header.index("人数")]
    try:
        traveler_count = int(float(travelers))
    except (TypeError, ValueError):
        traveler_count = -1
    if traveler_count != len(member_rows):
        errors.append(
            f"Travel Overview traveler count {travelers or 'blank'} does not match {len(member_rows)} Members rows"
        )

    for row_number, row in enumerate(rows["Preferences"][2:], start=3):
        traveler = row[4] if len(row) > 4 else ""
        if traveler and traveler != "所有人" and traveler not in member_ids:
            errors.append(
                f"Preferences row {row_number} references missing member {traveler}"
            )

    for sheet_name, indexes in {"Checklist": [3], "Proposals": [1, 7]}.items():
        for row_number, row in enumerate(rows[sheet_name][2:], start=3):
            for index in indexes:
                if len(row) > index and row[index] and row[index] not in member_ids:
                    errors.append(
                        f"{sheet_name} row {row_number} references missing member {row[index]}"
                    )

    for row_number, row in enumerate(rows["Bookings"][2:], start=3):
        if len(row) > 6 and row[6] == "已确认":
            if len(row) <= 12 or not row[11] or not row[12]:
                errors.append(
                    f"Confirmed booking on row {row_number} needs source and checked time"
                )

    version_rows = [row for row in rows["Change Log"][2:] if row and row[0]]
    versions = {row[0] for row in version_rows}
    plan_versions = {
        row[1] for row in rows["Daily Plan"][2:] if len(row) > 1 and row[1]
    }
    missing_versions = sorted(plan_versions - versions)
    if missing_versions:
        errors.append(
            f"Daily Plan references missing versions: {', '.join(missing_versions)}"
        )
    version_order = {row[0]: index for index, row in enumerate(version_rows)}
    for row_number, row in enumerate(rows["Change Log"][2:], start=3):
        predecessor = row[5] if len(row) > 5 else ""
        if predecessor and (
            predecessor not in versions
            or version_order[predecessor] >= version_order[row[0]]
        ):
            errors.append(
                f"Change Log row {row_number} has invalid predecessor {predecessor}"
            )

    plan_ids = {row[0] for row in rows["Daily Plan"][2:] if row and row[0]}
    booking_ids = {row[0] for row in rows["Bookings"][2:] if row and row[0]}
    task_ids = {row[0] for row in rows["Checklist"][2:] if row and row[0]}
    for row_number, row in enumerate(rows["Checklist"][2:], start=3):
        dependency = row[6] if len(row) > 6 else ""
        related = row[7] if len(row) > 7 else ""
        if dependency and dependency not in task_ids:
            errors.append(
                f"Checklist row {row_number} references missing dependency {dependency}"
            )
        if related and related not in plan_ids | booking_ids:
            errors.append(
                f"Checklist row {row_number} references missing related item {related}"
            )

    for row_number, row in enumerate(rows["Proposals"][2:], start=3):
        if len(row) > 6 and row[6] in {"Accepted", "已接受", "接受"}:
            result_version = row[9] if len(row) > 9 else ""
            if not result_version or result_version not in versions:
                errors.append(
                    f"Accepted proposal on row {row_number} has no valid result version"
                )
    return errors


def is_uninitialized_template(rows):
    if not REQUIRED_SHEETS.issubset(rows):
        return False
    for sheet_name, expected in EXPECTED_HEADERS.items():
        sheet_rows = rows[sheet_name]
        if len(sheet_rows) < 2 or sheet_rows[1][:len(expected)] != expected:
            return False
        if any(any(row) for row in sheet_rows[2:]):
            return False
    return True


def validate(path):
    try:
        return validate_rows(workbook_rows(path))
    except ARCHIVE_ERRORS as error:
        return [f"Unreadable Travel OS archive: {error}"]


def main():
    parser = argparse.ArgumentParser(description="Validate a Travel OS Excel archive")
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    try:
        rows = workbook_rows(args.workbook)
    except ARCHIVE_ERRORS as error:
        print(f"ERROR: Unreadable Travel OS archive: {error}")
        return 1
    if is_uninitialized_template(rows):
        print(f"READY: {args.workbook} is an uninitialized Travel OS template")
        return 0
    errors = validate_rows(rows)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS: {args.workbook}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
