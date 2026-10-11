#!/usr/bin/env python3
"""Validate a Travel OS workbook without third-party packages."""

import argparse
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


def _column_index(reference):
    letters = re.match(r"[A-Z]+", reference).group()
    index = 0
    for letter in letters:
        index = index * 26 + ord(letter) - ord("A") + 1
    return index - 1


def workbook_rows(path):
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = [
                "".join(node.text or "" for node in item.iterfind(".//m:t", NS))
                for item in root.findall("m:si", NS)
            ]

        book = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("p:Relationship", REL_NS)
        }
        result = {}
        for sheet in book.findall("m:sheets/m:sheet", NS):
            target = targets[sheet.attrib[f"{{{NS['r']}}}id"]].lstrip("/")
            xml = ET.fromstring(
                archive.read(target if target.startswith("xl/") else f"xl/{target}")
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


def validate_rows(rows):
    errors = []
    missing = REQUIRED_SHEETS - rows.keys()
    if missing:
        return [f"Missing sheets: {', '.join(sorted(missing))}"]

    for sheet_name, expected in EXPECTED_HEADERS.items():
        actual = rows[sheet_name][1][:len(expected)] if len(rows[sheet_name]) > 1 else []
        if actual != expected:
            errors.append(f"{sheet_name} headers do not match the Travel OS schema")

    for sheet_name in REQUIRED_SHEETS - {"Travel Overview"}:
        identifiers = [row[0] for row in rows[sheet_name][2:] if row and row[0]]
        duplicates = sorted({value for value in identifiers if identifiers.count(value) > 1})
        if duplicates:
            errors.append(f"{sheet_name} has duplicate IDs: {', '.join(duplicates)}")

    trips = [row for row in rows["Travel Overview"][2:] if any(row)]
    if len(trips) != 1:
        return [f"Travel Overview must contain exactly one trip row; found {len(trips)}"]

    overview_header = rows["Travel Overview"][1]
    trip = trips[0]
    active = trip[overview_header.index("Active Version")]
    status = trip[overview_header.index("状态")]
    if status in {"Active", "Completed"} and not active:
        errors.append(f"{status} trip has no Active Version")

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

    members = rows["Members"]
    member_ids = {row[0] for row in members[2:] if row and row[0]}
    roles = {row[2] for row in members[2:] if len(row) > 2}
    if "Owner" not in roles:
        errors.append("Members has no Owner")
    owner = trip[overview_header.index("负责人")]
    if owner and owner not in member_ids:
        errors.append(f"Trip owner {owner} is missing from Members")
    for sheet_name, indexes in {"Checklist": [3], "Proposals": [1, 7]}.items():
        for row_number, row in enumerate(rows[sheet_name][2:], start=3):
            for index in indexes:
                if len(row) > index and row[index] and row[index] not in member_ids:
                    errors.append(
                        f"{sheet_name} row {row_number} references missing member {row[index]}"
                    )

    versions = {row[0] for row in rows["Change Log"][2:] if row and row[0]}
    for row_number, row in enumerate(rows["Proposals"][2:], start=3):
        if len(row) > 6 and row[6] in {"Accepted", "已接受", "接受"}:
            result_version = row[9] if len(row) > 9 else ""
            if not result_version or result_version not in versions:
                errors.append(
                    f"Accepted proposal on row {row_number} has no valid result version"
                )
    return errors


def validate(path):
    try:
        return validate_rows(workbook_rows(path))
    except (KeyError, IndexError, ET.ParseError, zipfile.BadZipFile) as error:
        return [f"Unreadable Travel OS archive: {error}"]


def main():
    parser = argparse.ArgumentParser(description="Validate a Travel OS Excel archive")
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    errors = validate(args.workbook)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"PASS: {args.workbook}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
