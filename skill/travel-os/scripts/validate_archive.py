#!/usr/bin/env python3
"""Validate a Travel OS workbook without third-party packages."""

import argparse
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # Python 3.8 fallback keeps syntax validation available.
    ZoneInfo = None
    ZoneInfoNotFoundError = KeyError


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
VERSION_PATTERN = re.compile(r"v\d+\.\d+\.\d+(?:-[0-9A-Za-z][0-9A-Za-z.-]*)?")
TIME_ZONE_PATTERN = re.compile(
    r"(?:[A-Za-z0-9][A-Za-z0-9._+-]*/)*[A-Za-z0-9][A-Za-z0-9._+-]*"
)
try:
    TIME_ZONE_DATABASE_AVAILABLE = ZoneInfo is not None and bool(ZoneInfo("Etc/UTC"))
except ZoneInfoNotFoundError:
    TIME_ZONE_DATABASE_AVAILABLE = False
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
            if xml.find(".//m:f", NS) is not None:
                raise ValueError(
                    f"{sheet.attrib['name']} contains formulas; Travel OS cells must be literal values"
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


def _datetime(value):
    if not value:
        return None
    try:
        if re.fullmatch(r"\d+(?:\.\d+)?", value):
            return datetime(1899, 12, 30) + timedelta(days=float(value))
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, OverflowError):
        return None


def _date(value):
    parsed = _datetime(value)
    return parsed.date() if parsed else None


def _amount(value):
    try:
        amount = Decimal(str(value))
        return amount if amount.is_finite() and amount >= 0 else None
    except (InvalidOperation, TypeError, ValueError):
        return None


def _valid_time_zone(value):
    if not isinstance(value, str) or not TIME_ZONE_PATTERN.fullmatch(value):
        return False
    if not TIME_ZONE_DATABASE_AVAILABLE:
        return True
    try:
        ZoneInfo(value)
        return True
    except ZoneInfoNotFoundError:
        return False


def _clock_seconds(value):
    if not value:
        return None
    try:
        if re.fullmatch(r"\d+(?:\.\d+)?", value):
            fraction = float(value)
            if not 0 <= fraction < 1:
                return None
            return min(round(fraction * 86400), 86399)
        match = re.fullmatch(r"(\d{1,2}):(\d{2})(?::(\d{2}))?", value)
        if not match:
            return None
        hour, minute, second = (int(part or 0) for part in match.groups())
        if hour > 23 or minute > 59 or second > 59:
            return None
        return hour * 3600 + minute * 60 + second
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

    for sheet_name in REQUIRED_SHEETS - {"Travel Overview"}:
        for row_number, row in enumerate(rows[sheet_name][2:], start=3):
            if any(row) and not row[0]:
                errors.append(
                    f"{sheet_name} row {row_number} is missing {EXPECTED_HEADERS[sheet_name][0]}"
                )

    for row_number, row in enumerate(rows["Daily Plan"][2:], start=3):
        if not any(row):
            continue
        required = {
            0: "项目ID",
            1: "版本",
            2: "日期",
            5: "时区",
            7: "活动",
            11: "执行状态",
        }
        missing_fields = [
            name for index, name in required.items()
            if len(row) <= index or not row[index]
        ]
        if missing_fields:
            errors.append(
                f"Daily Plan row {row_number} is missing: {', '.join(missing_fields)}"
            )
        date_value = row[2] if len(row) > 2 else ""
        if date_value and not _date(date_value):
            errors.append(f"Daily Plan row {row_number} has an invalid date")
        start_value = row[3] if len(row) > 3 else ""
        end_value = row[4] if len(row) > 4 else ""
        if bool(start_value) != bool(end_value):
            errors.append(
                f"Daily Plan row {row_number} needs both start and end times"
            )
        elif start_value:
            start_seconds = _clock_seconds(start_value)
            end_seconds = _clock_seconds(end_value)
            if start_seconds is None or end_seconds is None:
                errors.append(f"Daily Plan row {row_number} has an invalid time range")
            elif end_seconds <= start_seconds:
                note = row[16].lower() if len(row) > 16 else ""
                if not any(
                    marker in note for marker in ("[overnight]", "跨夜", "过夜")
                ):
                    errors.append(
                        f"Daily Plan row {row_number} ends before it starts without an overnight marker"
                    )
        time_zone = row[5] if len(row) > 5 else ""
        if time_zone and not _valid_time_zone(time_zone):
            errors.append(
                f"Daily Plan row {row_number} has an invalid time zone: {time_zone}"
            )
        if len(row) > 11 and row[11] == "Ready":
            if len(row) <= 15 or not row[14] or not row[15]:
                errors.append(
                    f"Ready Daily Plan row {row_number} needs source and checked time"
                )
            elif not _datetime(row[15]):
                errors.append(
                    f"Ready Daily Plan row {row_number} has an invalid checked time"
                )
        cost = row[12] if len(row) > 12 else ""
        currency = row[13] if len(row) > 13 else ""
        if bool(cost) != bool(currency):
            errors.append(f"Daily Plan row {row_number} needs both cost and currency")
        elif cost:
            if _amount(cost) is None:
                errors.append(f"Daily Plan row {row_number} has an invalid cost")
            if not re.fullmatch(r"[A-Z]{3}", currency):
                errors.append(
                    f"Daily Plan row {row_number} has an invalid currency: {currency}"
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
    for field in (
        "Trip ID",
        "旅行标题",
        "目的地",
        "开始日期",
        "结束日期",
        "人数",
        "负责人",
        "旅行阶段",
        "状态",
        "主时区",
    ):
        if not trip[overview_header.index(field)]:
            errors.append(f"Travel Overview is missing {field}")

    active = trip[overview_header.index("Active Version")]
    phase = trip[overview_header.index("旅行阶段")]
    status = trip[overview_header.index("状态")]
    if status in {"Active", "Completed"} and not active:
        errors.append(f"{status} trip has no Active Version")
    if status == "Draft" and active:
        errors.append("Draft trip must not have an Active Version")
    if status == "Completed" and phase != "旅行后":
        errors.append("Completed trip must be in 旅行后 phase")
    start = _date(trip[overview_header.index("开始日期")])
    end = _date(trip[overview_header.index("结束日期")])
    home_time_zone = trip[overview_header.index("主时区")]
    if home_time_zone and not _valid_time_zone(home_time_zone):
        errors.append(
            f"Travel Overview has an invalid home time zone: {home_time_zone}"
        )
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

        if status == "Completed":
            unfinished_items = sorted(
                row[0]
                for row in active_rows
                if len(row) <= 11 or row[11] not in {"Done", "Skipped"}
            )
            if unfinished_items:
                errors.append(
                    "Completed trip has unfinished active items: "
                    + ", ".join(unfinished_items)
                )

        booking_by_id = {
            row[0]: row for row in rows["Bookings"][2:] if row and row[0]
        }
        booking_ids = set(booking_by_id)
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
            booking_id = row[10] if len(row) > 10 else ""
            execution_status = row[11] if len(row) > 11 else ""
            booking = booking_by_id.get(booking_id)
            if not booking:
                continue
            booking_status = booking[6] if len(booking) > 6 else ""
            if booking_status == "已取消" and execution_status not in {"Skipped", "Blocked"}:
                errors.append(
                    f"Daily Plan row {row_number} references cancelled booking {booking_id}"
                )
            if execution_status == "Ready" and booking_status not in {"已确认", "已完成"}:
                errors.append(
                    f"Ready Daily Plan row {row_number} requires confirmed booking {booking_id}"
                )

        if start and end and start <= end:
            for row_number, row in enumerate(active_rows, start=3):
                day = _date(row[2] if len(row) > 2 else "")
                note = row[16].lower() if len(row) > 16 else ""
                outside_marker = any(
                    marker in note
                    for marker in ("[pre-trip]", "[post-trip]", "行前", "行后")
                )
                if day and not outside_marker and not start <= day <= end:
                    errors.append(
                        f"Daily Plan row {row_number} falls outside the trip date range"
                    )

        timed_items = []
        for row_number, row in enumerate(rows["Daily Plan"][2:], start=3):
            if len(row) <= 1 or row[1] != active:
                continue
            start_value = row[3] if len(row) > 3 else ""
            end_value = row[4] if len(row) > 4 else ""
            if bool(start_value) != bool(end_value):
                continue
            if not start_value:
                continue
            start_seconds = _clock_seconds(start_value)
            end_seconds = _clock_seconds(end_value)
            if start_seconds is None or end_seconds is None:
                continue
            day = _date(row[2] if len(row) > 2 else "")
            if not day:
                continue
            note = row[16].lower() if len(row) > 16 else ""
            overnight = any(
                marker in note for marker in ("[overnight]", "跨夜", "过夜")
            )
            if end_seconds <= start_seconds:
                if not overnight:
                    continue
                end_seconds += 86400
            execution_status = row[11] if len(row) > 11 else ""
            if execution_status in {"Skipped", "Blocked"}:
                continue
            base = day.toordinal() * 86400
            timed_items.append(
                (
                    row[5] if len(row) > 5 else "",
                    base + start_seconds,
                    base + end_seconds,
                    row[0],
                )
            )

        for index, first in enumerate(timed_items):
            for second in timed_items[index + 1:]:
                if first[0] == second[0] and first[1] < second[2] and second[1] < first[2]:
                    errors.append(
                        f"Active Daily Plan items {first[3]} and {second[3]} overlap"
                    )

    members = rows["Members"]
    member_rows = [row for row in members[2:] if row and row[0]]
    member_ids = {row[0] for row in member_rows}
    member_roles = {
        row[0]: row[2] if len(row) > 2 else "" for row in member_rows
    }
    for row_number, row in enumerate(members[2:], start=3):
        if row and row[0]:
            missing_fields = [
                name
                for index, name in {1: "显示名", 2: "角色"}.items()
                if len(row) <= index or not row[index]
            ]
            if missing_fields:
                errors.append(
                    f"Members row {row_number} is missing: {', '.join(missing_fields)}"
                )
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
        traveler_number = Decimal(str(travelers))
        if (
            not traveler_number.is_finite()
            or traveler_number <= 0
            or traveler_number != traveler_number.to_integral_value()
        ):
            raise InvalidOperation
        traveler_count = int(traveler_number)
    except (InvalidOperation, TypeError, ValueError):
        traveler_count = None
        errors.append(
            f"Travel Overview has an invalid traveler count: {travelers or 'blank'}"
        )
    if traveler_count is not None and traveler_count != len(member_rows):
        errors.append(
            f"Travel Overview traveler count {travelers or 'blank'} does not match {len(member_rows)} Members rows"
        )

    for row_number, row in enumerate(rows["Preferences"][2:], start=3):
        if row and row[0]:
            required = {
                1: "范围",
                2: "类别",
                3: "优先级",
                4: "适用人",
                5: "偏好或约束",
                6: "证据",
                7: "置信度",
                8: "生效日期",
            }
            missing_fields = [
                name for index, name in required.items()
                if len(row) <= index or not row[index]
            ]
            if missing_fields:
                errors.append(
                    f"Preferences row {row_number} is missing: {', '.join(missing_fields)}"
                )
            effective_value = row[8] if len(row) > 8 else ""
            expiry_value = row[9] if len(row) > 9 else ""
            effective = _date(effective_value)
            expiry = _date(expiry_value)
            if effective_value and not effective:
                errors.append(
                    f"Preferences row {row_number} has an invalid effective date"
                )
            if expiry_value and not expiry:
                errors.append(f"Preferences row {row_number} has an invalid expiry date")
            elif effective and expiry and expiry < effective:
                errors.append(
                    f"Preferences row {row_number} expires before its effective date"
                )
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

    for row_number, row in enumerate(rows["Checklist"][2:], start=3):
        assignee = row[3] if len(row) > 3 else ""
        role = member_roles.get(assignee)
        if assignee in member_roles and role not in {"Owner", "Editor", "Member"}:
            errors.append(
                f"Checklist row {row_number} assignee {assignee} with role {role or 'blank'} cannot own tasks"
            )

    for row_number, row in enumerate(rows["Bookings"][2:], start=3):
        if row and row[0]:
            missing_fields = [
                name
                for index, name in {1: "类别", 2: "供应方", 6: "状态"}.items()
                if len(row) <= index or not row[index]
            ]
            if missing_fields:
                errors.append(
                    f"Bookings row {row_number} is missing: {', '.join(missing_fields)}"
                )
        amount = row[8] if len(row) > 8 else ""
        currency = row[9] if len(row) > 9 else ""
        if bool(amount) != bool(currency):
            errors.append(f"Bookings row {row_number} needs both amount and currency")
        elif amount:
            if _amount(amount) is None:
                errors.append(f"Bookings row {row_number} has an invalid amount")
            if not re.fullmatch(r"[A-Z]{3}", currency):
                errors.append(
                    f"Bookings row {row_number} has an invalid currency: {currency}"
                )
        start_time = _datetime(row[3] if len(row) > 3 else "")
        end_time = _datetime(row[4] if len(row) > 4 else "")
        if len(row) > 3 and row[3] and not start_time:
            errors.append(f"Bookings row {row_number} has an invalid start time")
        if len(row) > 4 and row[4] and not end_time:
            errors.append(f"Bookings row {row_number} has an invalid end time")
        if start_time and end_time:
            start_is_zoned = start_time.utcoffset() is not None
            end_is_zoned = end_time.utcoffset() is not None
            if start_is_zoned != end_is_zoned:
                errors.append(
                    f"Bookings row {row_number} mixes zoned and unzoned times"
                )
            elif end_time < start_time:
                errors.append(f"Bookings row {row_number} ends before it starts")
        if len(row) > 6 and row[6] == "已确认":
            if len(row) <= 12 or not row[11] or not row[12]:
                errors.append(
                    f"Confirmed booking on row {row_number} needs source and checked time"
                )
            elif not _datetime(row[12]):
                errors.append(f"Bookings row {row_number} has an invalid checked time")

    version_rows = [row for row in rows["Change Log"][2:] if row and row[0]]
    versions = {row[0] for row in version_rows}
    invalid_versions = sorted(
        version for version in versions if not VERSION_PATTERN.fullmatch(version)
    )
    if invalid_versions:
        errors.append(
            "Change Log has invalid version labels: " + ", ".join(invalid_versions)
        )
    version_by_id = {row[0]: row for row in version_rows}
    accepted_result_versions = {
        row[9]
        for row in rows["Proposals"][2:]
        if len(row) > 9 and row[6] == "接受" and row[9]
    }
    root_versions = [
        row[0] for row in version_rows if len(row) <= 5 or not row[5]
    ]
    if version_rows and len(root_versions) != 1:
        errors.append(
            f"Change Log must contain exactly one root version; found {len(root_versions)}"
        )
    if active and status in {"Active", "Completed"} and version_rows:
        latest = version_rows[-1][0]
        if active != latest:
            errors.append(
                f"Active Version {active} is not latest Change Log version {latest}"
            )
    plan_versions = {
        row[1] for row in rows["Daily Plan"][2:] if len(row) > 1 and row[1]
    }
    missing_versions = sorted(plan_versions - versions)
    if missing_versions:
        errors.append(
            f"Daily Plan references missing versions: {', '.join(missing_versions)}"
        )
    missing_snapshots = sorted(versions - plan_versions)
    if missing_snapshots:
        errors.append(
            "Change Log versions have no Daily Plan snapshot: "
            + ", ".join(missing_snapshots)
        )
    version_order = {row[0]: index for index, row in enumerate(version_rows)}
    for index, row in enumerate(version_rows):
        row_number = index + 3
        missing_fields = [
            name
            for field_index, name in {
                1: "创建时间",
                2: "作者",
                3: "原因",
                4: "变更摘要",
            }.items()
            if len(row) <= field_index or not row[field_index]
        ]
        if missing_fields:
            errors.append(
                f"Change Log row {row_number} is missing: {', '.join(missing_fields)}"
            )
        created_time = _datetime(row[1] if len(row) > 1 else "")
        if len(row) > 1 and row[1] and not created_time:
            errors.append(f"Change Log row {row_number} has an invalid creation time")
        author = row[2] if len(row) > 2 else ""
        if author and author not in member_ids:
            errors.append(
                f"Change Log row {row_number} references missing author {author}"
            )
        elif author and member_roles.get(author) not in {"Owner", "Editor"}:
            errors.append(
                f"Change Log row {row_number} author {author} must be Owner or Editor"
            )
        if not index and author != owner:
            errors.append(f"Root version must be authored by trip Owner {owner}")
        if index and row[0] not in accepted_result_versions:
            errors.append(
                f"Version {row[0]} has no accepted Owner proposal"
            )
        predecessor = row[5] if len(row) > 5 else ""
        if index and predecessor != version_rows[index - 1][0]:
            errors.append(
                f"Change Log row {row_number} must follow previous version {version_rows[index - 1][0]}"
            )
        if index and predecessor and created_time:
            previous_created = _datetime(version_rows[index - 1][1])
            if previous_created:
                created_is_zoned = created_time.utcoffset() is not None
                previous_is_zoned = previous_created.utcoffset() is not None
                if created_is_zoned != previous_is_zoned:
                    errors.append(
                        f"Change Log row {row_number} mixes zoned and unzoned creation times with predecessor {predecessor}"
                    )
                elif created_time < previous_created:
                    errors.append(
                        f"Change Log row {row_number} predates predecessor {predecessor}"
                    )
        if predecessor and (
            predecessor not in versions
            or version_order[predecessor] >= version_order[row[0]]
        ):
            errors.append(
                f"Change Log row {row_number} has invalid predecessor {predecessor}"
            )

    plan_by_version = {}
    for row in rows["Daily Plan"][2:]:
        if len(row) > 1 and row[0] and row[1]:
            plan_by_version.setdefault(row[1], {})[row[0]] = row
    for version_row in version_rows:
        version = version_row[0]
        predecessor = version_row[5] if len(version_row) > 5 else ""
        if not predecessor or predecessor not in plan_by_version:
            continue
        current_items = plan_by_version.get(version, {})
        for item_id, prior_row in plan_by_version[predecessor].items():
            prior_status = prior_row[11] if len(prior_row) > 11 else ""
            if prior_status not in {"Done", "Skipped"}:
                continue
            current_row = current_items.get(item_id)
            if not current_row:
                errors.append(
                    f"Version {version} drops completed item {item_id} from {predecessor}"
                )
                continue
            current_status = current_row[11] if len(current_row) > 11 else ""
            if current_status != prior_status:
                errors.append(
                    f"Version {version} regresses completed item {item_id} from {prior_status} to {current_status or 'blank'}"
                )

    plan_ids = {row[0] for row in rows["Daily Plan"][2:] if row and row[0]}
    booking_ids = {row[0] for row in rows["Bookings"][2:] if row and row[0]}
    task_ids = {row[0] for row in rows["Checklist"][2:] if row and row[0]}
    if status == "Completed":
        open_tasks = sorted(
            row[0]
            for row in rows["Checklist"][2:]
            if row and row[0] and (len(row) <= 5 or row[5] not in {"已完成", "已取消"})
        )
        if open_tasks:
            errors.append(
                "Completed trip has open checklist tasks: " + ", ".join(open_tasks)
            )
    dependencies = {}
    for row_number, row in enumerate(rows["Checklist"][2:], start=3):
        task_id = row[0] if row else ""
        if task_id:
            missing_fields = [
                name
                for index, name in {
                    1: "类别",
                    2: "任务",
                    3: "负责人",
                    4: "截止日期",
                    5: "状态",
                }.items()
                if len(row) <= index or not row[index]
            ]
            if missing_fields:
                errors.append(
                    f"Checklist row {row_number} is missing: {', '.join(missing_fields)}"
                )
            if len(row) > 4 and row[4] and not _date(row[4]):
                errors.append(f"Checklist row {row_number} has an invalid due date")
        dependency = row[6] if len(row) > 6 else ""
        related = row[7] if len(row) > 7 else ""
        if task_id and dependency:
            dependencies[task_id] = dependency
        if dependency and dependency not in task_ids:
            errors.append(
                f"Checklist row {row_number} references missing dependency {dependency}"
            )
        if related and related not in plan_ids | booking_ids:
            errors.append(
                f"Checklist row {row_number} references missing related item {related}"
            )

    processed = set()
    for start_task in sorted(task_ids):
        if start_task in processed:
            continue
        trail = []
        positions = {}
        task = start_task
        while task in dependencies and task not in processed:
            if task in positions:
                cycle = trail[positions[task]:]
                errors.append(
                    "Checklist dependency cycle: "
                    + " -> ".join(cycle + [cycle[0]])
                )
                break
            positions[task] = len(trail)
            trail.append(task)
            task = dependencies[task]
        processed.update(trail)

    if status == "Completed":
        unresolved_proposals = sorted(
            row[0]
            for row in rows["Proposals"][2:]
            if row and row[0] and (len(row) <= 6 or row[6] not in {"接受", "拒绝"})
        )
        if unresolved_proposals:
            errors.append(
                "Completed trip has unresolved proposals: "
                + ", ".join(unresolved_proposals)
            )

    for row_number, row in enumerate(rows["Proposals"][2:], start=3):
        proposal_id = row[0] if row else ""
        if proposal_id:
            required = {
                1: "提交人",
                2: "日期",
                3: "影响项目或日期",
                4: "提案",
                5: "原因",
                6: "状态",
            }
            missing_fields = [
                name for index, name in required.items()
                if len(row) <= index or not row[index]
            ]
            if missing_fields:
                errors.append(
                    f"Proposals row {row_number} is missing: {', '.join(missing_fields)}"
                )
            if len(row) > 2 and row[2] and not _date(row[2]):
                errors.append(f"Proposals row {row_number} has an invalid date")
        submitter = row[1] if len(row) > 1 else ""
        role = member_roles.get(submitter)
        if submitter in member_roles and role not in {"Owner", "Editor", "Member"}:
            errors.append(
                f"Proposals row {row_number} submitter {submitter} with role {role or 'blank'} cannot submit proposals"
            )
        status = row[6] if len(row) > 6 else ""
        if status in {"接受", "拒绝"}:
            decision_owner = row[7] if len(row) > 7 else ""
            resolution = row[8] if len(row) > 8 else ""
            if decision_owner != owner:
                errors.append(
                    f"Resolved proposal on row {row_number} must be decided by trip Owner {owner}"
                )
            if not resolution:
                errors.append(
                    f"Resolved proposal on row {row_number} needs a resolution"
                )
        if status == "接受":
            result_version = row[9] if len(row) > 9 else ""
            if not result_version or result_version not in versions:
                errors.append(
                    f"Accepted proposal on row {row_number} has no valid result version"
                )
            else:
                proposal_date = _date(row[2] if len(row) > 2 else "")
                result_row = version_by_id[result_version]
                result_created = _datetime(result_row[1] if len(result_row) > 1 else "")
                if (
                    proposal_date
                    and result_created
                    and result_created.date() < proposal_date
                ):
                    errors.append(
                        f"Accepted proposal {proposal_id} postdates result version {result_version}"
                    )
                if proposal_id not in " ".join(
                    str(value or "") for value in result_row[3:5]
                ):
                    errors.append(
                        f"Accepted proposal {proposal_id} is not referenced by result version {result_version}"
                    )
        elif len(row) > 9 and row[9]:
            errors.append(
                f"Non-accepted proposal {proposal_id} must not name a result version"
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
